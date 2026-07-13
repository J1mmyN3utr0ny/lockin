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

// Fetch the Lab's /status snapshot with a hard timeout (LAN can be flaky).
export async function fetchStatus(timeoutMs = 4000) {
  const base = labUrl();
  if (!base) throw new Error("No Lab address set (Settings → Lab).");
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(base + "/status", { signal: ctrl.signal, cache: "no-store" });
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
    return await fetch(base + path, { cache: "no-store", signal: ctrl.signal, ...opts });
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

// One cycle: adopt the hub's copy if it's newer, otherwise push ours up. Returns "pulled"/"pushed"/"".
export async function syncState() {
  if (!labConfigured()) return "";
  const adopted = await pullState();
  if (adopted) return "pulled";
  // A fresh / not-yet-onboarded device only pulls — it must never overwrite real data on the hub.
  const st = S.getState();
  if (!st.settings.onboarded && (st.xp || 0) === 0) return "";
  const pushed = await pushState();
  return pushed ? "pushed" : "";
}

// ---- real-time link to the Lab (Server-Sent Events) ------------------------------------------
// The Lab pushes app-state and its own progress the instant they change; we push our edits back the
// moment they happen. No polling — changes cross devices in well under a second.
let _es = null;
let _esUrl = "";
let _lastPushed = -1;
let _started = false;

function _openStream() {
  const base = labUrl();
  const want = base ? base + "/events" : "";
  if (want === _esUrl && _es && _es.readyState !== 2) return; // already connected to the right Lab
  if (_es) { try { _es.close(); } catch (_e) {} _es = null; }
  _esUrl = want;
  if (!want) return;
  try {
    _es = new EventSource(want);
    _es.addEventListener("appstate", (e) => {
      try {
        const remote = JSON.parse(e.data);
        if (remote && remote.version !== undefined && (remote.updatedAt || 0) > (S.getState().updatedAt || 0)) {
          _lastPushed = remote.updatedAt || 0; // we now match the hub; don't echo it back
          S.applyRemote(remote);
        }
      } catch (_e) {}
    });
    _es.addEventListener("labstatus", (e) => {
      try {
        const status = JSON.parse(e.data);
        // per-device display data — store it WITHOUT bumping the sync clock
        if (status && status.ok) { S.getState().lab = { status, syncedAt: new Date().toISOString() }; S.save(); S.emit(); }
      } catch (_e) {}
    });
    _es.onerror = () => {}; // EventSource auto-reconnects; the watchdog re-points it if the URL changed
  } catch (_e) { _es = null; }
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
    if (!labConfigured()) return;
    const ua = S.getState().updatedAt || 0;
    if (ua <= _lastPushed) return; // nothing new (e.g. just a status refresh) — don't echo
    clearTimeout(pushT);
    pushT = setTimeout(() => { _lastPushed = S.getState().updatedAt || 0; pushState(); }, 300);
  });
}
