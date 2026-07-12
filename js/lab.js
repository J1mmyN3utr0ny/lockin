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
