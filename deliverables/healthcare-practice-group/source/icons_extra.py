"""Extra line icons (shared by bifold/trifold editors)."""
import math

from idmlkit import Oval, Path
from layouts import icon


def extra_icon(kind, x, y, s, color="Midnight", sw=1.3):
    P = lambda pts, closed=False: Path([(x + px * s, y + py * s) for px, py in pts], closed, None, color, sw,
                                       name=f"icon {kind}")
    O = lambda px, py, pw, ph, fill=None: Oval(x + px * s, y + py * s, pw * s, ph * s, fill=fill,
                                                stroke=None if fill else color, sw=sw, name=f"icon {kind}")
    if kind == "key":
        return [O(0.04, 0.3, 0.4, 0.4), P([(0.44, 0.5), (0.96, 0.5)]), P([(0.8, 0.5), (0.8, 0.68)]),
                P([(0.92, 0.5), (0.92, 0.63)])]
    if kind == "calendar":
        return [P([(0.08, 0.16), (0.92, 0.16), (0.92, 0.94), (0.08, 0.94)], True), P([(0.08, 0.36), (0.92, 0.36)]),
                P([(0.3, 0.04), (0.3, 0.24)]), P([(0.7, 0.04), (0.7, 0.24)]),
                P([(0.33, 0.64), (0.46, 0.77), (0.68, 0.52)])]
    if kind == "target":
        return [O(0.05, 0.05, 0.9, 0.9), O(0.27, 0.27, 0.46, 0.46), O(0.43, 0.43, 0.14, 0.14, fill=color)]
    if kind == "people":
        arc = lambda cx: [(cx + 0.2 * math.cos(math.radians(a)), 0.86 + 0.26 * math.sin(math.radians(a)))
                          for a in range(180, 361, 15)]
        return [O(0.13, 0.12, 0.24, 0.24), O(0.63, 0.12, 0.24, 0.24), P(arc(0.25)), P(arc(0.75))]
    if kind == "dollar":
        s_curve = [(0.66, 0.33), (0.5, 0.27), (0.35, 0.33), (0.36, 0.45), (0.5, 0.5), (0.64, 0.55), (0.65, 0.67),
                   (0.5, 0.73), (0.34, 0.67)]
        return [O(0.04, 0.04, 0.92, 0.92), P(s_curve), P([(0.5, 0.17), (0.5, 0.83)])]
    return icon(kind, x, y, s, color, sw)
