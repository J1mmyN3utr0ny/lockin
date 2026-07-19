# sync.py — a tiny local web server so the phone app can read the Lab's progress over Wi-Fi.
# The phone polls GET /status to show synced records and to auto-unlock its Focus Lock once you've
# finished your Lab work. CORS is open (localhost tool on your own LAN) so the PWA can fetch it.
import datetime
import json
import os
import queue
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DEFAULT_PORT = 8765
APP_STATE_FILE = "app_state.json"  # the phone/PC app state, relayed through the Lab (kept local)
# finished workouts pushed by the gymmy Android app (kept local, next to this file)
GYMMY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gymmy_state.json")

# Real-time push: every connected device holds a /events stream; we fan out changes to all of them.
_subscribers = set()
_subs_lock = threading.Lock()


def _broadcast(event, data):
    with _subs_lock:
        subs = list(_subscribers)
    for q in subs:
        try:
            q.put_nowait((event, data))
        except Exception:
            pass


CLOCK_SKEW_MS = 5 * 60 * 1000  # tolerate honest drift between the phone and this PC


def sanitize_clock(state):
    """Clamp a state blob's updatedAt to 'now' if it claims to be from the future.

    updatedAt drives last-write-wins sync. A future timestamp is poison: it beats every real
    edit forever, so every device adopts the blob carrying it, and a genuine edit afterwards
    LOWERS the clock (to the true now) — which the phone's push guard reads as "nothing new",
    so the edit never gets sent. A hand-injected 9999999999999 sitting in app_state.json is
    exactly how phone->desktop sync went silently dead. The hub refuses to relay one.

    An impossible clock is demoted to 0, NOT clamped to now: we don't know when that blob was
    really written, and calling it "now" would promote a stale snapshot to newest-in-the-system,
    upgrading a stuck sync into real data loss. 0 makes it lose every comparison instead — safe,
    because the app merges day ticks independently of the clock.
    """
    if not isinstance(state, dict):
        return state
    now = int(time.time() * 1000)
    try:
        ts = float(state.get("updatedAt"))
    except (TypeError, ValueError):
        ts = 0
    if not (0 < ts <= now + CLOCK_SKEW_MS):
        state["updatedAt"] = 0
    return state


def _wake_for(d):
    """Mirrors the web app's schedule: Saturday rests (no alarm), Friday wakes 08:30,
    course days 07:00 (Sun & Wed through Jul 15; Mon & Thu from Jul 17 — Thu Jul 16 is
    skipped — until the Sep-3 exam), every other day 07:30."""
    wd = d.weekday()  # Mon=0 .. Sun=6
    if wd == 5:
        return None
    if wd == 4:
        return "08:30"
    if datetime.date(2026, 7, 14) <= d <= datetime.date(2026, 9, 3) and d != datetime.date(2026, 7, 16):
        course = wd in (6, 2) if d <= datetime.date(2026, 7, 15) else wd in (0, 3)
        if course:
            return "07:00"
    return "07:30"


def wake_plan():
    """Today + tomorrow's wake times — consumed by the Alarma app to build the morning burst."""
    today = datetime.date.today()
    return {"days": [
        {"date": d.isoformat(), "wake": _wake_for(d)}
        for d in (today, today + datetime.timedelta(days=1))
    ]}


def local_ip():
    """Best-effort LAN IP of this machine (for the URL you type into the phone)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


class _Handler(BaseHTTPRequestHandler):
    snapshot = staticmethod(lambda: {})  # replaced by SyncServer
    app_state = {}                        # last app-state blob a device pushed (shared phone <-> PC)
    gymmy_state = {}                      # last workout payload gymmy pushed ({"sessions":[...]})
    state_path = APP_STATE_FILE

    def _send(self, code, body):
        data = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        # Older Chrome private-network preflights ask for this before letting a public
        # HTTPS page (the installed PWA) talk to a LAN address. Harmless everywhere else.
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")
        if path in ("", "/"):
            self._send(200, {"ok": True, "app": "LockIn Lab"})
        elif path == "/status":
            try:
                self._send(200, _Handler.snapshot())
            except Exception as e:
                self._send(500, {"ok": False, "error": repr(e)})
        elif path == "/appstate":
            self._send(200, _Handler.app_state or {"updatedAt": 0})
        elif path == "/gymmy":
            self._send(200, _Handler.gymmy_state or {"sessions": []})
        elif path == "/waketime":
            self._send(200, wake_plan())
        elif path == "/events":
            self._sse()
        else:
            self._send(404, {"ok": False, "error": "not found"})

    def _sse_write(self, event, data):
        payload = "event: %s\ndata: %s\n\n" % (event, json.dumps(data))
        self.wfile.write(payload.encode("utf-8"))
        self.wfile.flush()

    def _sse(self):
        """Server-Sent Events: push app-state and Lab-status changes to this device in real time."""
        q = queue.Queue()
        with _subs_lock:
            _subscribers.add(q)
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            # bring a freshly-connected device up to date immediately
            self._sse_write("appstate", _Handler.app_state or {"updatedAt": 0})
            self._sse_write("gymmy", _Handler.gymmy_state or {"sessions": []})
            try:
                self._sse_write("labstatus", _Handler.snapshot())
            except Exception:
                pass
            while True:
                try:
                    event, data = q.get(timeout=15)
                    self._sse_write(event, data)
                except queue.Empty:
                    self.wfile.write(b": ping\n\n")  # keepalive; also detects a dead connection
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass  # client disconnected
        finally:
            with _subs_lock:
                _subscribers.discard(q)

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")
        if path == "/appstate":
            try:
                length = int(self.headers.get("Content-Length", 0) or 0)
                raw = self.rfile.read(length) if length else b"{}"
                data = sanitize_clock(json.loads(raw.decode("utf-8")))
                _Handler.app_state = data
                try:
                    with open(_Handler.state_path, "w", encoding="utf-8") as f:
                        json.dump(data, f)
                except Exception:
                    pass  # relaying still works from memory even if the disk write fails
                _broadcast("appstate", data)  # push to every other connected device in real time
                self._send(200, {"ok": True, "updatedAt": data.get("updatedAt", 0)})
            except Exception as e:
                self._send(400, {"ok": False, "error": repr(e)})
        elif path == "/gymmy":
            # gymmy replaces its store wholesale each push (last 14 days) — idempotent by design.
            try:
                length = int(self.headers.get("Content-Length", 0) or 0)
                raw = self.rfile.read(length) if length else b"{}"
                data = json.loads(raw.decode("utf-8"))
                if not isinstance(data, dict) or not isinstance(data.get("sessions"), list):
                    self._send(400, {"ok": False, "error": "expected {sessions:[...]}"})
                    return
                _Handler.gymmy_state = data
                try:
                    with open(GYMMY_FILE, "w", encoding="utf-8") as f:
                        json.dump(data, f)
                except Exception:
                    pass
                _broadcast("gymmy", data)  # LockIn devices adopt the workouts in real time
                self._send(200, {"ok": True, "sessions": len(data["sessions"])})
            except Exception as e:
                self._send(400, {"ok": False, "error": repr(e)})
        else:
            self._send(404, {"ok": False, "error": "not found"})

    def log_message(self, *args):
        pass  # keep the console quiet


class SyncServer:
    """Runs the status server in a background daemon thread."""

    def __init__(self, snapshot_fn, port=DEFAULT_PORT, app_state_path=APP_STATE_FILE):
        self.port = port
        self.httpd = None
        self.thread = None
        self._snapshot = snapshot_fn
        _Handler.snapshot = staticmethod(snapshot_fn)
        _Handler.state_path = app_state_path
        try:
            with open(app_state_path, encoding="utf-8") as f:
                _Handler.app_state = sanitize_clock(json.load(f))  # survive a Lab restart
        except Exception:
            _Handler.app_state = {}
        try:
            with open(GYMMY_FILE, encoding="utf-8") as f:
                _Handler.gymmy_state = json.load(f)
        except Exception:
            _Handler.gymmy_state = {}

    def start(self):
        try:
            self.httpd = ThreadingHTTPServer(("0.0.0.0", self.port), _Handler)
        except OSError:
            # port busy — try a couple of fallbacks
            for p in (self.port + 1, self.port + 2, 8770):
                try:
                    self.httpd = ThreadingHTTPServer(("0.0.0.0", p), _Handler)
                    self.port = p
                    break
                except OSError:
                    continue
            if not self.httpd:
                return None
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        return self.url()

    def broadcast_status(self):
        """Call after Lab progress changes so connected phones/PCs update in real time."""
        try:
            _broadcast("labstatus", self._snapshot())
        except Exception:
            pass

    def url(self):
        return "http://%s:%d" % (local_ip(), self.port)

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
