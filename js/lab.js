// lab.js — the phone's sync client to the desktop LockIn Lab. Pulls progress over Wi-Fi and
// powers the Lab-gated Focus Lock (the phone unlocks once you finish work in the Lab).
import * as S from "./state.js";

export function labUrl() {
  let u = (S.getState().settings.labUrl || "").trim();
  if (!u) return "";
  if (!/^https?:\/\//i.test(u)) u = "http://" + u;
  return u.replace(/\/+$/, "");
}
export function labConfigured() { return !!labUrl(); }

// Chrome's Local Network Access (LNA, Chrome 142+): the installed PWA is served over HTTPS
// (GitHub Pages), and an HTTPS page may only reach the plain-HTTP LAN hub if the request is
// recognizably local — a private-IP literal or .local host — AND annotated with
// targetAddressSpace, which lifts the mixed-content block behind a one-tap "local network"
// permission. Without this annotation the phone can NEVER connect. Browsers that don't know
// the option ignore it, so it's safe everywhere (desktop localhost included).
function lanOpts(url) {
  try {
    const host = new URL(url).hostname;
    const priv = /^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|169\.254\.)/.test(host) || host.endsWith(".local");
    return priv ? { targetAddressSpace: "local" } : {};
  } catch (_e) { return {}; }
}

// Fetch the Lab's /status snapshot with a hard timeout (LAN can be flaky).
export async function fetchStatus(timeoutMs = 4000) {
  const base = labUrl();
  if (!base) throw new Error("No Lab address set (Settings → Lab).");
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(base + "/status", { signal: ctrl.signal, cache: "no-store", ...lanOpts(base) });
    if (!res.ok) throw new Error("Lab responded " + res.status);
    const data = await res.json();
    if (!data || !data.ok) throw new Error("Unexpected reply from Lab");
    return data;
  } catch (e) {
    if (e.name === "AbortError") throw new Error("Lab didn't answer — same Wi-Fi? correct address?");
    throw new Error(e.message || "Couldn't reach the Lab");
  } finally {
    clearTimeout(timer);
  }
}

// Pull once and store the snapshot into app state.
export async function syncNow() {
  const status = await fetchStatus();
  S.update((st) => { st.lab = { status, syncedAt: new Date().toISOString() }; });
  return status;
}

export function lastStatus() { return S.getState().lab && S.getState().lab.status; }
export function lastSyncedAt() { return S.getState().lab && S.getState().lab.syncedAt; }

// ---- app-data sync (phone <-> PC, relayed through the Lab hub) --------------------------------
// The Lab stores whichever device's state is newest; every device pushes its own edits and pulls
// the other's. Last-write-wins by state.updatedAt. Connection settings stay per-device.
async function labFetch(path, opts, timeoutMs = 4000) {
  const base = labUrl();
  if (!base) return null;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    return await fetch(base + path, { cache: "no-store", signal: ctrl.signal, ...lanOpts(base), ...opts });
  } catch (_e) {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

export async function pushState() {
  const res = await labFetch("/appstate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(S.getState()),
  });
  return !!(res && res.ok);
}

export async function pullState() {
  const res = await labFetch("/appstate", {});
  if (!res || !res.ok) return false;
  let remote;
  try { remote = await res.json(); } catch (_e) { return false; }
  if (remote && remote.version !== undefined && (remote.updatedAt || 0) > (S.getState().updatedAt || 0)) {
    return S.applyRemote(remote);
  }
  return false;
}

// A fresh / not-yet-onboarded device only pulls — it must never overwrite real data on the hub.
function canPush() {
  const st = S.getState();
  return st.settings.onboarded || (st.xp || 0) > 0;
}

// One cycle: adopt the hub's copy if it's newer, otherwise push ours up. Returns "pulled"/"pushed"/"".
export async function syncState() {
  if (!labConfigured()) return "";
  const adopted = await pullState();
  if (adopted) return "pulled";
  if (!canPush()) return "";
  const pushed = await pushState();
  return pushed ? "pushed" : "";
}

// ---- gymmy → LockIn: adopt finished workouts pushed to the hub --------------------------------
// The gymmy Android app POSTs its completed sessions to the hub's /gymmy; we fold them into
// workoutLogs (gymmy is authoritative per exercise it logged) and tick the day's gym block.
// Exercise ids are shared between the apps, so history and overload hints just work.
export function adoptGymmy(payload) {
  const sessions = payload && payload.sessions;
  if (!Array.isArray(sessions) || !sessions.length) return false;
  const st = S.getState();
  const updates = [];
  for (const s of sessions) {
    if (!s || !/^\d{4}-\d{2}-\d{2}$/.test(s.date || "") || !Array.isArray(s.sets) || !s.sets.length) continue;
    const ex = {};
    for (const t of s.sets) {
      if (!t || typeof t.exerciseId !== "string" || !t.exerciseId) continue;
      (ex[t.exerciseId] = ex[t.exerciseId] || []).push({ w: Number(t.weightKg) || 0, r: Number(t.reps) || 0 });
    }
    if (!Object.keys(ex).length) continue;
    const m = /^day\s+([a-e])$/i.exec((s.plan || "").trim());
    const existing = st.workoutLogs[s.date];
    const merged = {
      ...(existing || {}),
      dayId: m ? m[1].toUpperCase() : (existing && existing.dayId),
      ex: { ...((existing && existing.ex) || {}), ...ex },
      gymmy: true
    };
    if (JSON.stringify(existing || null) !== JSON.stringify(merged)) updates.push([s.date, merged]);
  }
  if (!updates.length) return false;
  S.update((s2) => {
    for (const [date, merged] of updates) {
      s2.workoutLogs[date] = merged;
      if (!s2.days[date]) s2.days[date] = { blocks: {}, offDay: false, note: "" };
      s2.days[date].blocks.gym = true; // the lift happened — gymmy said so
    }
  });
  return true;
}

// ---- real-time link to the Lab (Server-Sent Events over fetch) --------------------------------
// The Lab pushes app-state and its own progress the instant they change; we push our edits back the
// moment they happen. No polling — changes cross devices in well under a second.
// NOTE: this deliberately does NOT use EventSource — Chrome's Local Network Access mixed-content
// exemption only covers fetch(), so EventSource from the HTTPS PWA to the HTTP LAN hub is blocked.
// A fetch-streamed reader parses the same text/event-stream format instead.
let _sseCtrl = null;   // AbortController of the live stream
let _sseUrl = "";      // hub /events URL the stream is bound to
let _sseAlive = false; // true while a stream is connected/being read
let _lastPushed = -1;
let _started = false;

function _onHubEvent(event, data) {
  if (event === "appstate") {
    try {
      const remote = JSON.parse(data);
      if (remote && remote.version !== undefined && (remote.updatedAt || 0) > (S.getState().updatedAt || 0)) {
        _lastPushed = remote.updatedAt || 0; // we now match the hub; don't echo it back
        S.applyRemote(remote);
      }
    } catch (_e) {}
  } else if (event === "gymmy") {
    try { adoptGymmy(JSON.parse(data)); } catch (_e) {}
  } else if (event === "labstatus") {
    try {
      const status = JSON.parse(data);
      // per-device display data — store it WITHOUT bumping the sync clock
      if (status && status.ok) { S.getState().lab = { status, syncedAt: new Date().toISOString() }; S.save(); S.emit(); }
    } catch (_e) {}
  }
}

async function _readStream(url, ctrl) {
  _sseAlive = true;
  try {
    const res = await fetch(url, { cache: "no-store", signal: ctrl.signal, ...lanOpts(url) });
    if (!res.ok || !res.body) return;
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    let buf = "";
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      let i;
      while ((i = buf.indexOf("\n\n")) !== -1) {
        const chunk = buf.slice(0, i);
        buf = buf.slice(i + 2);
        let event = "message", data = "";
        for (const line of chunk.split("\n")) {
          if (line.startsWith("event:")) event = line.slice(6).trim();
          else if (line.startsWith("data:")) data += (data ? "\n" : "") + line.slice(5).trim();
          // lines starting with ":" are keepalive pings — ignored
        }
        if (data) _onHubEvent(event, data);
      }
    }
  } catch (_e) {
    // dropped/aborted — the watchdog reconnects within 4s
  } finally {
    _sseAlive = false;
  }
}

function _openStream() {
  const base = labUrl();
  const want = base ? base + "/events" : "";
  if (want === _sseUrl && _sseAlive) return; // already connected to the right Lab
  if (_sseCtrl) { try { _sseCtrl.abort(); } catch (_e) {} _sseCtrl = null; }
  _sseUrl = want;
  if (!want) return;
  _sseCtrl = new AbortController();
  _readStream(want, _sseCtrl);
}

// Start the real-time link. Safe to call once; keeps itself connected as the Lab URL changes.
export function startAppSync() {
  if (_started) return;
  _started = true;
  _openStream();
  setInterval(_openStream, 4000); // (re)connect when the Lab URL is set/changed or the stream drops
  // push local edits the instant they land (tiny debounce to coalesce rapid changes)
  let pushT = null;
  S.subscribe(() => {
    if (!labConfigured() || !canPush()) return;
    const ua = S.getState().updatedAt || 0;
    if (ua <= _lastPushed) return; // nothing new (e.g. just a status refresh) — don't echo
    clearTimeout(pushT);
    pushT = setTimeout(() => { _lastPushed = S.getState().updatedAt || 0; pushState(); }, 300);
  });
}
