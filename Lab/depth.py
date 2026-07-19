# depth.py — merges the per-track extended-teaching files (depth_<track>.py) into one lookup,
# keyed by LESSON ID. This is the "much longer lessons" layer: where expansions.py adds a short
# deep-dive after the body, DEPTH replaces the thin original body with several thousand words of
# real teaching — mental model, mechanism, worked example, failure modes, professional practice.
# Each entry: {"title_check": str, "sections": [{"h": str, "body": str}, ...]}
TRACKS = ("python", "csharp", "c", "asm", "linux", "cmd", "cyber_high", "cyber_low", "dsa")


def _load(track):
    try:
        mod = __import__("depth_" + track)
        return dict(getattr(mod, "DEPTH", {}) or {})
    except Exception:
        return {}  # a missing or broken data file must never take the Lab down


ALL = {}
for _t in TRACKS:
    ALL.update(_load(_t))


def for_lesson(lesson_id, title):
    """The extended content for a lesson id — None if absent, or if the lesson was retitled
    since the content was authored (better to show nothing than to mislabel a wall of text)."""
    e = ALL.get(lesson_id)
    if not e:
        return None
    tc = e.get("title_check")
    if tc and tc != title:
        return None
    return e


def stats():
    """(lessons covered, total characters) — used by the Lab's status line and tests."""
    chars = sum(len(s.get("body", "")) for e in ALL.values() for s in e.get("sections", []))
    return len(ALL), chars
