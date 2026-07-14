# expansions.py — merges the deep-dive expansion data files (expansions_1/2/3.py,
# authored per track) into one lookup the lesson renderer draws after the lesson body.
# Each entry: {"title_check": str, "sections": [{"h","body"}], "links": [{"label","url"}]}
def _load(name):
    try:
        mod = __import__(name)
        return dict(getattr(mod, "EXPANSIONS", {}) or {})
    except Exception:
        return {}  # a broken/missing data file must never take the Lab down


ALL = {}
for _n in ("expansions_1", "expansions_2", "expansions_3"):
    ALL.update(_load(_n))


def for_lesson(tid, idx, title):
    """The expansion for lesson #idx of track tid — None if absent or the title moved."""
    e = ALL.get("%s:%d" % (tid, idx))
    if not e:
        return None
    tc = e.get("title_check")
    if tc and tc != title:
        return None  # lesson order changed since authoring — better to hide than mislabel
    return e
