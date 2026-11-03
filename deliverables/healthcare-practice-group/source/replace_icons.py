"""Swap the generated line icons in a bifold/trifold for Cresa library icons (outline, Midnight).
Usage: replace_icons.py <unpacked target dir> <unpacked icon library dir> <out.idml> <stroke pt> <id base hex>"""
import copy
import glob
import os
import sys
import zipfile

from lxml import etree

TGT, LIB, OUT = sys.argv[1:4]
STROKE = float(sys.argv[4])
NID = [int(sys.argv[5], 16)]
SIDE = float(sys.argv[6])

TITLE_TO_ICON = {
    "Opening a New Location": "u1d97",          # Location_Midnight
    "Growing Across Markets": "u1d47",          # Expand (Midnight)
    "Renewals & Rightsizing": "u1ce1",          # Connectivity_Midnight
    "Mergers & Integration": "u1d13",           # DiagonalGroup_Midnight
    "Relocating Without Disruption": "u1d41",   # Dolly_Midnight
    "Freeing Up Capital": "u1dc7",              # Money_Midnight
    "Every Location": "u1b03",                  # PortfolioSolutions_Midnight
    "Never Miss": "u1c49",                      # Calendar_Midnight
    "Sites Compared": "u1d73",                  # Inspect_Midnight
    "Audit-Ready": "u1dea",                     # PaperCheck_Midnight
}
SHAPES = ("Polygon", "Rectangle", "Oval", "GraphicLine")


def mat(el):
    return [float(v) for v in (el.get("ItemTransform") or "1 0 0 1 0 0").split()]


def mul(a, b):
    return [a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1], a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3],
            a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5]]


def ap(m, x, y):
    return m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5]


def anchors(el, m):
    out = []
    for p in el.iter("PathPointType"):
        out.append(ap(m, *map(float, p.get("Anchor").split())))
    return out


def new_id():
    NID[0] += 1
    return f"u{NID[0]:x}"


# ---------------------------------------------------------------- library icons, flattened to shapes in icon space
lib_items = {}
for f in glob.glob(os.path.join(LIB, "Spreads", "*.xml")):
    for el in etree.parse(f).iter():
        if el.get("Self") in TITLE_TO_ICON.values():
            lib_items[el.get("Self")] = el


def flatten(el, m=None):
    """Yield (shape element, cumulative matrix) for every leaf shape under el."""
    m = mul(m or [1, 0, 0, 1, 0, 0], mat(el))
    if el.tag in SHAPES:
        yield el, m
    for ch in el:
        if ch.tag in SHAPES + ("Group",):
            yield from flatten(ch, m)


def icon_shapes(sid):
    shapes = list(flatten(lib_items[sid]))
    pts = [p for el, m in shapes for p in anchors(el, m)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return shapes, (min(xs), min(ys), max(xs), max(ys))


def build_icon(sid, box, layer, name):
    """Group of copied library shapes, fitted into box (x0,y0,x1,y1) in spread coords."""
    shapes, (lx0, ly0, lx1, ly1) = icon_shapes(sid)
    bw, bh = box[2] - box[0], box[3] - box[1]
    s = min(bw / (lx1 - lx0), bh / (ly1 - ly0))
    ox = box[0] + (bw - (lx1 - lx0) * s) / 2 - lx0 * s
    oy = box[1] + (bh - (ly1 - ly0) * s) / 2 - ly0 * s
    fit = [s, 0, 0, s, ox, oy]
    grp = etree.Element("Group", Self=new_id(), ItemTransform="1 0 0 1 0 0", ItemLayer=layer, Visible="true",
                        Locked="false", Name=name, AppliedObjectStyle="ObjectStyle/$ID/[None]")
    for el, m in shapes:
        c = copy.deepcopy(el)
        full = mul(fit, m)
        for p in c.iter("PathPointType"):
            for k in ("Anchor", "LeftDirection", "RightDirection"):
                p.set(k, "%.4f %.4f" % ap(full, *map(float, p.get(k).split())))
        c.set("ItemTransform", "1 0 0 1 0 0")
        c.set("ItemLayer", layer)
        if c.get("StrokeColor") not in (None, "Swatch/None"):
            c.set("StrokeColor", "Color/Midnight")
            c.set("StrokeWeight", str(STROKE))
        if c.get("FillColor") not in (None, "Swatch/None"):
            c.set("FillColor", "Color/Midnight")
        for d in c.iter():
            if d.get("Self"):
                d.set("Self", new_id())
        grp.append(c)
    return grp


# ---------------------------------------------------------------- find old icon clusters + their titles, swap
def story_text(sid):
    p = os.path.join(TGT, "Stories", f"Story_{sid}.xml")
    if not os.path.exists(p):
        return ""
    return " ".join(c.text or "" for c in etree.parse(p).iter("Content")).replace(" ", " ")


swapped = []
for sp_path in glob.glob(os.path.join(TGT, "Spreads", "*.xml")):
    tree = etree.parse(sp_path)
    spread = tree.getroot().find("Spread")
    olds = [el for el in spread if (el.get("Name") or "").startswith("icon ")]
    if not olds:
        continue
    # cluster old icon shapes by proximity
    clusters = []
    for el in olds:
        pts = anchors(el, mat(el))
        bb = [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)]
        for c in clusters:
            if bb[0] < c["bb"][2] + 4 and bb[2] > c["bb"][0] - 4 and bb[1] < c["bb"][3] + 4 and bb[3] > c["bb"][1] - 4:
                c["els"].append(el)
                c["bb"] = [min(c["bb"][0], bb[0]), min(c["bb"][1], bb[1]), max(c["bb"][2], bb[2]), max(c["bb"][3], bb[3])]
                break
        else:
            clusters.append({"els": [el], "bb": bb, "layer": el.get("ItemLayer")})
    frames = []
    for tf in spread.iter("TextFrame"):
        pts = anchors(tf, mat(tf))
        frames.append((min(p[0] for p in pts), min(p[1] for p in pts), story_text(tf.get("ParentStory"))))
    for c in clusters:
        x0, y0, x1, y1 = c["bb"]
        best = None
        for fx, fy, txt in frames:
            title = next((t for t in TITLE_TO_ICON if txt.strip().startswith(t)), None)
            if title and x0 - 14 <= fx <= x1 + 60 and y0 - 10 <= fy <= y1 + 60:
                d = abs(fx - x0) + abs(fy - y0)
                if best is None or d < best[0]:
                    best = (d, title)
        if best is None:
            print("  no title match for cluster at", [round(v) for v in c["bb"]])
            continue
        title = best[1]
        side = SIDE  # consistent icon size, top-left aligned with where the old icon sat
        box = (x0, y0 + (y1 - y0 - side) / 2, x0 + side, y0 + (y1 - y0 - side) / 2 + side)
        idx = list(spread).index(c["els"][0])
        for el in c["els"]:
            spread.remove(el)
        spread.insert(idx, build_icon(TITLE_TO_ICON[title], box, c["layer"], f"icon: {title}"))
        swapped.append(title)
    tree.write(sp_path, xml_declaration=True, encoding="UTF-8", standalone=True)

if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, "w") as z:
    z.write(os.path.join(TGT, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
    for root, _, files in os.walk(TGT):
        for fn in sorted(files):
            full = os.path.join(root, fn)
            arc = os.path.relpath(full, TGT)
            if arc != "mimetype":
                z.write(full, arc, compress_type=zipfile.ZIP_DEFLATED)
print("swapped", len(swapped), ":", sorted(swapped))
