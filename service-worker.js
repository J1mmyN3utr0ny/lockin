/* LockIn service worker — offline-first precache of the app shell. */
const VERSION = "lockin-v12";
const ASSETS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./css/styles.css",
  "./icons/icon.svg",
  "./icons/icon-maskable.svg",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-192.png",
  "./icons/icon-maskable-512.png",
  "./js/app.js",
  "./js/state.js",
  "./js/srs.js",
  "./js/schedule.js",
  "./js/ui.js",
  "./js/ai.js",
  "./js/focus.js",
  "./js/lab.js",
  "./js/modules/today.js",
  "./js/modules/progress.js",
  "./js/modules/physique.js",
  "./js/modules/diet.js",
  "./js/modules/sleep.js",
  "./js/modules/cs_mentor.js",
  "./js/modules/projects.js",
  "./js/modules/math.js",
  "./js/modules/pet.js",
  "./js/modules/cyber.js",
  "./js/modules/offday.js",
  "./js/modules/testmode.js",
  "./js/modules/review.js",
  "./js/data/workout_program.js",
  "./js/data/meals.js",
  "./js/data/cs_milestones.js",
  "./js/data/resume_projects.js",
  "./js/data/math_checklist.js",
  "./js/data/pet_content.js",
  "./js/data/pte_vocab.js",
  "./js/data/cyber_decks.js",
  "./js/data/skill_tracks.js",
  "./js/data/gama_notes.js",
  "./js/data/git_lessons.js"
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(VERSION).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

/* Cache-first for our OWN assets only. Cross-origin requests (the LockIn Lab status server,
   the Gemini API) must bypass the SW entirely — never cache them, or sync/AI would go stale. */
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  if (new URL(req.url).origin !== self.location.origin) return; // let the network handle it live
  e.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(VERSION).then((c) => c.put(req, copy)).catch(() => {});
          return res;
        })
        .catch(() => caches.match("./index.html"));
    })
  );
});
