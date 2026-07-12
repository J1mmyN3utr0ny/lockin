# sync.py — a tiny local web server so the phone app can read the Lab's progress over Wi-Fi.
# The phone polls GET /status to show synced records and to auto-unlock its Focus Lock once you've
# finished your Lab work. CORS is open (localhost tool on your own LAN) so the PWA can fetch it.
import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DEFAULT_PORT = 8765


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

    def _send(self, code, body):
        data = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
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
        else:
            self._send(404, {"ok": False, "error": "not found"})

    def log_message(self, *args):
        pass  # keep the console quiet


class SyncServer:
    """Runs the status server in a background daemon thread."""

    def __init__(self, snapshot_fn, port=DEFAULT_PORT):
        self.port = port
        self.httpd = None
        self.thread = None
        _Handler.snapshot = staticmethod(snapshot_fn)

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

    def url(self):
        return "http://%s:%d" % (local_ip(), self.port)

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
