"""V.04 bifold markup (11/08): back page rework, national cases + logos to back, map section to inside left,
native competitor chart, copy updates."""
import os
import re
import shutil
import sys
import zipfile
from xml.sax.saxutils import escape

from lxml import etree

from idmlkit import Doc, IdmlWriter, Image, Line, Rect, Text

SRC, OUT, LOGO = sys.argv[1], sys.argv[2], sys.argv[3]
WORK = OUT + ".d"
shutil.rmtree(WORK, ignore_errors=True)
shutil.copytree(SRC, WORK)
ST = os.path.join(WORK, "Stories")
PX, PY = -612.0, -396.0


def sp(name):
    p = os.path.join(WORK, "Spreads", name)
    t = etree.parse(p)
    return p, t, t.getroot().find("Spread")


IN_P, IN_T, INSIDE = sp("Spread_u1a0.xml")
BK_P, BK_T, BACK = sp("Spread_u6b7.xml")


def find(spread, sid):
    for el in spread:
        if el.get("Self") == sid:
            return el
    raise KeyError(sid)


def mat(el):
    return [float(v) for v in el.get("ItemTransform").split()]


def bbox(el):
    m = mat(el)
    pts = [tuple(map(float, p.get("Anchor").split())) for p in el.find("Properties/PathGeometry").iter("PathPointType")]
    xs = [x + m[4] - PX for x, _ in pts]
    ys = [y + m[5] - PY for _, y in pts]
    return min(xs), min(ys), max(xs), max(ys)


def move(el, dx=0.0, dy=0.0):
    m = mat(el)
    m[4] += dx
    m[5] += dy
    el.set("ItemTransform", " ".join(repr(v) for v in m))


def set_box(el, x0=None, y0=None, x1=None, y1=None):
    """Resize a translation-only frame to a page-coordinate box (None keeps that edge)."""
    bx0, by0, bx1, by1 = bbox(el)
    x0 = bx0 if x0 is None else x0
    y0 = by0 if y0 is None else y0
    x1 = bx1 if x1 is None else x1
    y1 = by1 if y1 is None else y1
    m = mat(el)
    for p in el.find("Properties/PathGeometry").iter("PathPointType"):
        for k in ("Anchor", "LeftDirection", "RightDirection"):
            x, y = map(float, p.get(k).split())
            px, py = x + m[4] - PX, y + m[5] - PY
            nx = x0 if abs(px - bx0) < abs(px - bx1) else x1
            ny = y0 if abs(py - by0) < abs(py - by1) else y1
            if bx0 == bx1:
                nx = x0
            if by0 == by1:
                ny = y0
            p.set(k, f"{nx - m[4] + PX} {ny - m[5] + PY}")


def place(el, x0, y0):
    """Move element so its bbox top-left lands at page (x0, y0)."""
    bx0, by0, _, _ = bbox(el)
    move(el, x0 - bx0, y0 - by0)


def set_text(sid, new):
    p = os.path.join(ST, f"Story_{sid}.xml")
    t = etree.parse(p)
    cs = list(t.iter("Content"))
    assert len(cs) == len(new), (sid, [c.text for c in cs])
    for c, txt in zip(cs, new):
        if txt is not None:
            c.text = txt
    t.write(p, xml_declaration=True, encoding="UTF-8", standalone=True)


gone_stories = []


def remove(spread, *sids):
    for s in sids:
        el = find(spread, s)
        if el.get("ParentStory"):
            gone_stories.append(el.get("ParentStory"))
        spread.remove(el)


def transfer(src, dst, sids, dy):
    for s in sids:
        el = find(src, s)
        src.remove(el)
        move(el, 0, dy)
        dst.append(el)


# ================================================================ inside: map section in, national cases + logos out
transfer(INSIDE, BACK, ["uc3d", "uc3f", "uc56", "uc58", "uae7", "ub1f"], 364 - 441.9)
transfer(INSIDE, BACK, ["uaee", "ub26"], 0)
transfer(INSIDE, BACK, ["ub06", "ub3e"], 0)
transfer(INSIDE, BACK, ["u236"], 0)
TILES1 = "u1a9 u1b3 u1bd u1c7 u1d0 u1da".split()
TILES2 = "u1e4 u1ee u1f8 u205 u20f u21a".split()
transfer(INSIDE, BACK, TILES1, 0)
transfer(INSIDE, BACK, TILES2, 0)
MAP_ITEMS = ["u6c0", "u930", "u946", "u95c", "u972"]
transfer(BACK, INSIDE, MAP_ITEMS, 470 - 385.8)

# ================================================================ back page copy
set_text("u801", ["Your lease is one of your practice’s largest expenses. Most physicians and healthcare executives "
                  "negotiate one only every 5 to 10 years, but your landlord does it every day. Cresa represents only "
                  "your interests, never landlords, so our advice has one goal: the right space on the right terms "
                  "for your practice."])
set_text("u854", ["No obligations to landlords or building owners"])
set_text("u881", ["Freedom to negotiate more aggressively on your behalf"])
set_text("u8ae", ["A platform solely dedicated to healthcare practices"])
set_text("u960", ["With 55 offices across North America, Cresa brings local market knowledge to wherever you deliver "
                  "care. Whether you’re entering a new metro or adding a clinic down the street, our advisors "
                  "already know the markets, the buildings and the deal terms on the ground."])

# ================================================================ back page layout
set_box(find(BACK, "u813"), y0=104, y1=230)
remove(BACK, "u839", "u8c3", "u8d7", "u8ed", "u8f0", "u904", "u91a")     # heading, items 04 and 05
COLW = (540 - 2 * 12) / 3
for k, (rule, num, title) in enumerate((("u83c", "u850", "u866"), ("u869", "u87d", "u893"), ("u896", "u8aa", "u8c0"))):
    x = 36 + k * (COLW + 12)
    set_box(find(BACK, rule), x0=x, x1=x + COLW, y0=262, y1=264.5)
    set_box(find(BACK, num), x0=x, x1=x + COLW, y0=270, y1=280)
    set_box(find(BACK, title), x0=x, x1=x + COLW, y0=286, y1=318)
set_box(find(BACK, "u7e9"), y0=334, y1=334)                              # divider above the national cases
for s in ("uc3d", "uc56"):
    el = find(BACK, s)
    move(el, 0, 344 - bbox(el)[1])
for lab, bg in (("uc3f", "uc3d"), ("uc58", "uc56")):
    el = find(BACK, lab)
    move(el, 0, bbox(find(BACK, bg))[1] + 4 - bbox(el)[1])
for s in ("uae7", "ub1f"):
    el = find(BACK, s)
    move(el, 0, 362 - bbox(el)[1])
for s in ("uaee", "ub26"):
    set_box(find(BACK, s), y0=404, y1=404)
for s in ("ub06", "ub3e"):
    set_box(find(BACK, s), y0=412, y1=494)
place(find(BACK, "u236"), 36, 506)
for row, ids in ((532, TILES1), (580, TILES2)):
    for s in ids:
        el = find(BACK, s)
        move(el, 0, row - bbox(el)[1])
# original library graphic: kept on the pasteboard, replaced by an editable chart
g = find(BACK, "u816")
g.set("Name", "Original no-conflicts graphic (pasteboard)")
move(g, -720, 0)
set_box(find(BACK, "u7d2"), y0=66.8, y1=250)

# ================================================================ inside left: map section placement
set_box(find(INSIDE, "u972"), y1=640)

# ================================================================ new items
w = IdmlWriter(Doc("x", 612, 792, 1), None, None)
w.n = 0xd000
w.layer_ids = {"Art": "u145", "Placeholder Labels": "u145"}
w._local, w._xf = True, "1 0 0 1 0 0"


def T(x, y, ww, hh, paras, **kw):
    return Text(x + PX, y + PY, ww, hh, paras, **kw)


inside_items = [Line(36 + PX, 452 + PY, 576 + PX, 452 + PY, stroke="Light Gray", sw=1, name="divider")]
back_items = [T(288, 78, 150, 74, [("H4", "Our competitors represent building owners across the country."),
                                   ("H4", [("Emphasis Bold", "We represent practices, not landlords.")])])]
BARS = [("Cresa", 0), ("STREAM", 89), ("COLLIERS", 358), ("NEWMARK", 400), ("CUSHMAN &\nWAKEFIELD", 611),
        ("JLL", 660), ("CBRE", 920)]
BASE, MAXH, BW, STEP, X0 = 222.0, 106.0, 30.0, 39.0, 292.0
for k, (name, v) in enumerate(BARS):
    x = X0 + k * STEP
    h = MAXH * v / 920
    if h:
        back_items.append(Rect(x + PX, BASE - h + PY, BW, h, fill="Midnight", name=f"bar {name}"))
    label = [("Chart Label", f"{v}"), ("Caption", "million SF" if v else "SF")]
    back_items.append(T(x - 6, BASE - h - 24, BW + 12, 22, label))
    if name == "Cresa":
        back_items.append(Image(x - 2 + PX, BASE + 7 + PY, BW + 4, 9, LOGO, name="bar label Cresa"))
    else:
        back_items.append(T(x - 6, BASE + 6, BW + 12, 18, [("Caption", name)]))
back_items.append(Line(286 + PX, BASE + PY, 566 + PX, BASE + PY, stroke="Midnight", sw=0.75, name="chart baseline"))

LOCAL = {'Chart Label': ('Chart Label', 'FontStyle="65 Medium" PointSize="9" Justification="CenterAlign"'),
         'Caption': ('Caption', 'PointSize="5.5" Justification="CenterAlign"'),
         'Chart Bar Label': ('Chart Bar Label', 'PointSize="7" Justification="CenterAlign"')}
new_stories = []


def emit(spread, items):
    xml = "".join(w.item_xml(0, it) for it in items)
    for sid, sx in w.stories:
        for style, (_, attrs) in LOCAL.items():
            sx = sx.replace(f'AppliedParagraphStyle="ParagraphStyle/{style}">',
                            f'AppliedParagraphStyle="ParagraphStyle/{style}" {attrs}>')
        sx = sx.replace('AppliedParagraphStyle="ParagraphStyle/H4">',
                        'AppliedParagraphStyle="ParagraphStyle/H4" PointSize="10.5" Leading="13">')
        open(os.path.join(ST, f"Story_{sid}.xml"), "w", encoding="utf-8").write(sx)
        new_stories.append(sid)
    w.stories = []
    for el in etree.fromstring(f"<r>{xml}</r>"):
        spread.append(el)


emit(INSIDE, inside_items)
emit(BACK, back_items)
for p, t in ((IN_P, IN_T), (BK_P, BK_T)):
    t.write(p, xml_declaration=True, encoding="UTF-8", standalone=True)

# ================================================================ designmap, links, zip
os.makedirs(os.path.join(WORK, "Links"), exist_ok=True)
for s in gone_stories:
    os.remove(os.path.join(ST, f"Story_{s}.xml"))
dm_path = os.path.join(WORK, "designmap.xml")
dm = open(dm_path, encoding="utf-8").read()
for s in gone_stories:
    dm = re.sub(rf'<idPkg:Story src="Stories/Story_{s}\.xml"\s*/>', "", dm)
m = re.search(r'StoryList="([^"]*)"', dm)
ids = [s for s in m.group(1).split() if s not in gone_stories] + new_stories
dm = dm[:m.start(1)] + " ".join(ids) + dm[m.end(1):]
a = re.search(r'<idPkg:Story src="Stories/Story_[^"]+"\s*/>', dm)
dm = dm[:a.start()] + "".join(f'<idPkg:Story src="Stories/Story_{s}.xml" />' for s in new_stories) + dm[a.start():]
open(dm_path, "w", encoding="utf-8").write(dm)
shutil.rmtree(os.path.join(WORK, "Links"), ignore_errors=True)
if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, "w") as z:
    z.write(os.path.join(WORK, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
    for root, _, files in os.walk(WORK):
        for fn in sorted(files):
            full = os.path.join(root, fn)
            arc = os.path.relpath(full, WORK)
            if arc != "mimetype":
                z.write(full, arc, compress_type=zipfile.ZIP_DEFLATED)
print("ok: +", len(new_stories), "stories, -", len(gone_stories))
