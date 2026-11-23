"""Comp ordering shared by the map builder and the layout: newest close date first.
Accepts MM/DD/YYYY or MM/YYYY; undated comps go last."""


def key(c):
    p = (c.get("date") or "").split("/")
    if len(p) == 3: return (p[2], p[0].zfill(2), p[1].zfill(2))
    if len(p) == 2: return (p[1], p[0].zfill(2), "00")
    return ("0000", "00", "00")


def sort(comps):
    return sorted(comps, key=key, reverse=True)
