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
TILES1 = "u1a9 u1b3 u1bd u1c7 u1d0 u1da".split()
TILES2 = "u1e4 u1ee u1f8 u205 u20f u21a".split()
transfer(INSIDE, BACK, ["u236"] + TILES1 + TILES2, 0)


def scale_to(el, s, x0, y0):
    """Uniformly scale an element (frame + contents) and put its top-left at page (x0, y0)."""
    m = mat(el)
    pts = [tuple(map(float, p.get("Anchor").split())) for p in el.find("Properties/PathGeometry").iter("PathPointType")]
    lx0, ly0 = min(x for x, _ in pts), min(y for _, y in pts)
    el.set("ItemTransform", f"{s} 0 0 {s} {PX + x0 - s * lx0} {PY + y0 - s * ly0}")


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
set_box(find(BACK, "u813"), y0=104, y1=212)
remove(BACK, "u839", "u8c3", "u8d7", "u8ed", "u8f0", "u904", "u91a")     # heading, items 04 and 05
remove(BACK, "u83c", "u850", "u866", "u869", "u87d", "u893", "u896", "u8aa", "u8c0")   # stacked under the text instead
set_box(find(BACK, "u7e9"), y0=334, y1=334)                              # divider above the map section
MS = 0.78
scale_to(find(BACK, "u6c0"), MS, 36, 344)                                  # map, 0.78 scale
place(find(BACK, "u930"), 250, 466)                                        # "55" over the Atlantic
place(find(BACK, "u946"), 250, 491)
set_box(find(BACK, "u95c"), x0=328, x1=576, y0=350, y1=404)
set_box(find(BACK, "u972"), x0=328, x1=576, y0=414, y1=536)
place(find(BACK, "u236"), 36, 546)
TS = 0.85
TW = 82 * TS
GAP = (540 - 6 * TW) / 5
for row, ids in ((564, TILES1), (603, TILES2)):
    for k, sid in enumerate(ids):
        scale_to(find(BACK, sid), TS, 36 + k * (TW + GAP), row)
# original library graphic: kept on the pasteboard, replaced by an editable chart
g = find(BACK, "u816")
g.set("Name", "Original no-conflicts graphic (pasteboard)")
move(g, -720, 0)
set_box(find(BACK, "u7d2"), y0=66.8, y1=316)


# ================================================================ new items
w = IdmlWriter(Doc("x", 612, 792, 1), None, None)
w.n = 0xd000
w.layer_ids = {"Art": "uchart", "Placeholder Labels": "ub8"}
w._local, w._xf = True, "1 0 0 1 0 0"


def T(x, y, ww, hh, paras, **kw):
    return Text(x + PX, y + PY, ww, hh, paras, **kw)


inside_items = []
BASE = 270.0
back_items = [T(36, 222, 228, 90, [("Bullet", t) for t in (
    "No obligations to landlords or building owners",
    "Freedom to negotiate more aggressively on your behalf",
    "A platform solely dedicated to healthcare practices")]),
    Rect(276 + PX, 66.8 + PY, 300, BASE - 66.8, fill="Paper", stroke="Light Gray", sw=0.5, name="chart area"),
    T(290, 80, 150, 74, [("H4", "Our competitors represent building owners across the country."),
                         ("H4", [("Emphasis Bold", "We represent practices, not landlords.")])])]
# name, value, fill, tint
BARS = [("Cresa", 0, None, None), ("Stream", 89, "Dark Gray", None), ("Colliers", 358, "Bright Blue", 55),
        ("Newmark", 400, "Bright Blue", None), ("Cushman & Wakefield", 611, "Stadium Blue", None),
        ("JLL", 660, "Midnight", 75), ("CBRE", 920, "Midnight", None)]
BASE, MAXH, BW, STEP, X0 = 270.0, 176.0, 34.0, 39.0, 290.0
for k, (name, v, fill, tint) in enumerate(BARS):
    x = X0 + k * STEP
    h = MAXH * v / 920
    if h:
        back_items.append(Rect(x + PX, BASE - h + PY, BW, h, fill=fill, tint=tint, name=f"bar {name}"))
    if h >= 30:
        back_items.append(T(x, BASE - h + 4, BW, 24, [("Chart Bar Label", f"{v}"), ("Caption", "million SF")]))
    else:
        back_items.append(T(x - 4, BASE - h - 24, BW + 8, 22, [("Chart Label", f"{v}"),
                                                                ("Caption Dark", "million SF" if v else "SF")]))
    if name != "Cresa":
        back_items.append(T(x - 2, BASE + 8, BW + 4, 22, [("zz Placeholder Label", f"{name} logo")],
                            valign="center", layer="Placeholder Labels"))
back_items.append(Line(276 + PX, BASE + PY, 576 + PX, BASE + PY, stroke="Midnight", sw=0.75, name="chart baseline"))
back_items.append(Image(X0 + PX, BASE + 12 + PY, BW, 10, LOGO, name="bar label Cresa"))

LOCAL = {'Chart Label': 'FontStyle="65 Medium" PointSize="10" Justification="CenterAlign" FillColor="Color/Midnight"',
         'Caption': 'PointSize="5.5" Leading="7" Justification="CenterAlign" FillColor="Color/Paper"',
         'Caption Dark': 'PointSize="5.5" Leading="7" Justification="CenterAlign" FillColor="Color/Midnight"',
         'Chart Bar Label': 'FontStyle="65 Medium" PointSize="10" Leading="12" Justification="CenterAlign"',
         'Bullet': 'FontStyle="65 Medium" PointSize="10" FillColor="Color/Midnight" SpaceAfter="7"'}
new_stories = []


def emit(spread, items):
    xml = "".join(w.item_xml(0, it) for it in items)
    for sid, sx in w.stories:
        sx = sx.replace('ParagraphStyle/Caption Dark"', 'ParagraphStyle/Caption" DARK="1"')
        for style, attrs in LOCAL.items():
            if style == "Caption Dark":
                sx = sx.replace('AppliedParagraphStyle="ParagraphStyle/Caption" DARK="1">',
                                f'AppliedParagraphStyle="ParagraphStyle/Caption" {attrs}>')
            else:
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
dm = dm.replace('<Layer Self="u145" Name="Art"',
                '<Layer Self="uchart" Name="No-conflicts chart + bullets" Visible="true" Locked="false" IgnoreWrap="false" '
                'ShowGuides="true" LockGuides="false" UI="true" Expendable="true" Printable="true"><Properties>'
                '<LayerColor type="enumeration">Green</LayerColor></Properties></Layer><Layer Self="u145" Name="Art"', 1)
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
