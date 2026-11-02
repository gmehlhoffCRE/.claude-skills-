"""Back page rework on the user's InDesign-saved bifold: logos to top, two case studies (Fresenius, DaVita),
no-conflicts section with chart, three contacts with smaller headshots, QR/CTA removed."""
import copy
import os
import re
import shutil
import sys
import zipfile

from lxml import etree

from idmlkit import Doc, IdmlWriter, Line, Placeholder, Rect, Text

SRC, OUT = sys.argv[1], sys.argv[2]
WORK = OUT + ".d"
shutil.rmtree(WORK, ignore_errors=True)
shutil.copytree(SRC, WORK)
SP = os.path.join(WORK, "Spreads", "Spread_u5c5.xml")
tree = etree.parse(SP)
spread = tree.getroot().find("Spread")
ITEMS = {el.get("Self"): el for el in spread if el.get("Self")}
PX, PY = -612.0, -396.0  # page -> spread offset (page 4 is the left page of its spread)


def mat(el):
    return [float(v) for v in el.get("ItemTransform").split()]


def translate(sid, dx, dy):
    el = ITEMS[sid]
    m = mat(el)
    m[4] += dx
    m[5] += dy
    el.set("ItemTransform", " ".join(repr(v) for v in m))


def set_box(sid, x0, y0, x1, y1):
    """Reshape a translation-only frame/line to page-coordinate box."""
    el = ITEMS[sid]
    m = mat(el)
    ix0, iy0, ix1, iy1 = x0 + PX - m[4], y0 + PY - m[5], x1 + PX - m[4], y1 + PY - m[5]
    pts = list(el.find("Properties").find("PathGeometry").iter("PathPointType"))
    anchors = [tuple(map(float, p.get("Anchor").split())) for p in pts]
    cx = sum(a[0] for a in anchors) / len(anchors)
    cy = sum(a[1] for a in anchors) / len(anchors)
    for p, (ax, ay) in zip(pts, anchors):
        nx = ix0 if (ax < cx or len(pts) == 2 and ax <= cx) else ix1
        ny = iy0 if ay < cy else iy1
        if len(pts) == 2:
            ny = iy0
            nx = ix0 if ax == min(a[0] for a in anchors) else ix1
        v = f"{nx} {ny}"
        for k in ("Anchor", "LeftDirection", "RightDirection"):
            p.set(k, v)


def remove(*sids):
    for s in sids:
        spread.remove(ITEMS.pop(s))


# ---------------------------------------------------------------- logo wall to the top
translate("u79c", 0, -298)          # eyebrow dash
translate("u7b0", 0, -298)          # "Trusted by healthcare leaders"
for s in "u7b3 u7b7 u7bc u7c1 u7c6 u7cb".split():
    translate(s, 0, -306)
for s in "u7cf u7d5 u7da u7df u7e3 u7e7".split():
    translate(s, 0, -328)
translate("u79b", 0, -172)          # divider under the wall

# ---------------------------------------------------------------- two case studies (Fresenius, DaVita)
CW = 258
CASES = [(36, 36, "u5fb u601 u615 u62b u641 u657 u66d u683".split()),
         (318, 408, "u70f u716 u72a u740 u756 u76c u782 u798".split())]
DY = 124
for x0, ox, (logo, rule, head, s1, c1, s2, c2, body) in CASES:
    translate(logo, x0 - ox, DY)
    set_box(rule, x0, 276, x0 + CW, 276)
    set_box(head, x0, 286, x0 + CW, 316)
    translate(s1, x0 - ox, DY)
    translate(c1, x0 - ox, DY)
    translate(s2, (x0 + 130) - (ox + 84), DY)
    translate(c2, (x0 + 130) - (ox + 84), DY)
    set_box(body, x0, 360, x0 + CW, 446)
DISPATCH_ITEMS = "u686 u68a u69e u6b4 u6ca u6e0 u6f6 u70c".split()
DISPATCH_STORIES = "u68c u6a2 u6b8 u6ce u6e4 u6fa".split()
remove(*DISPATCH_ITEMS)

# ---------------------------------------------------------------- footer: QR + CTA out, three contacts
remove("u85d", "u871", "u875", "u889", "u803", "u830", "u817", "u844")
CTA_STORIES = ["u85f", "u877", "u805", "u832"]
CONTACT_X = [36, 216, 396]
for sid, x0 in (("u82d", CONTACT_X[0]), ("u85a", CONTACT_X[1])):
    set_box(sid, x0 + 50, 682, x0 + 178, 742)

# clone Doug's frame + story for Anthony
new_story = "u7f01"
new_frame = copy.deepcopy(ITEMS["u82d"])
new_frame.set("Self", "u7f02")
new_frame.set("ParentStory", new_story)
spread.append(new_frame)
ITEMS["u7f02"] = new_frame
set_box("u7f02", CONTACT_X[2] + 50, 682, CONTACT_X[2] + 178, 742)
st = etree.parse(os.path.join(WORK, "Stories", "Story_u81b.xml"))
st.getroot().find("Story").set("Self", new_story)
for c, txt in zip(st.iter("Content"), ["Anthony Fritsche", "Exec Managing Principal", "832.515.7366",
                                       "afritsche@cresa.com"]):
    c.text = txt
for i, el in enumerate(st.iter()):
    if el.get("Self") and el.get("Self") != new_story:
        el.set("Self", f"u7f1{i:x}")
st.write(os.path.join(WORK, "Stories", f"Story_{new_story}.xml"), xml_declaration=True, encoding="UTF-8",
         standalone=True)

# ---------------------------------------------------------------- new items
items = []
for x0, name in zip(CONTACT_X, ("Doug McNee", "Jason Herbrich", "Anthony Fritsche")):
    items.append(Placeholder(x0, 684, 42, 42, "Photo", fill="Stadium Blue", dark=True, lpad=3, rpad=3, name=f"Headshot: {name}"))
# no-conflicts section
items += [Line(36, 458, 576, 458, stroke="Light Gray", sw=1, name="divider"),
          Rect(36, 477, 14, 2, fill="Goldenrod", name="eyebrow dash"),
          Text(56, 474, 240, 11, [("Eyebrow", "No conflicts. Ever.")]),
          Text(36, 490, CW, 52, [("H2 Small", [(None, "Occupier focused, so "),
                                               ("Emphasis Medium", "our only bias is you.")])]),
          Text(36, 546, CW, 74, [("Body Small", "Most full-service real estate firms represent both landlords and "
                                                "tenants, and estimate nearly 85% of their revenue comes from "
                                                "landlords. Cresa never represents landlords or developers, so there "
                                                "are no listings to steer you toward and every negotiation is on "
                                                "your side.")])]
cx = 318
# frame for the client-supplied square-footage graph (placed in InDesign)
items.append(Placeholder(cx, 474, CW, 146, "Graph: landlord-side square footage by firm (place in InDesign)",
                         fill="Light Gray", tint=45, lpad=16, rpad=16, name="No-conflicts graph"))

doc = Doc("edit", 612, 792, 4)
w = IdmlWriter(doc, None, None)
w.n = 0x8000
w.layer_ids = {"Art": "u142", "Placeholder Labels": "ub8"}
xml = "".join(w.item_xml(3, it) for it in items)
LOCAL = ('<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" FontStyle="45 Light" '
         'PointSize="8.5"><Properties><Leading type="unit">12</Leading></Properties>')
new_ids = [new_story]
for sid, sx in w.stories:
    sx = sx.replace('<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/Body Small">'
                    '<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]">',
                    '<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/Body Small">' + LOCAL)
    open(os.path.join(WORK, "Stories", f"Story_{sid}.xml"), "w", encoding="utf-8").write(sx)
    new_ids.append(sid)
frag = etree.fromstring(f"<r>{xml}</r>")
for el in list(frag):
    spread.append(el)
tree.write(SP, xml_declaration=True, encoding="UTF-8", standalone=True)

# ---------------------------------------------------------------- stories + designmap
gone = DISPATCH_STORIES + CTA_STORIES
for s in gone:
    os.remove(os.path.join(WORK, "Stories", f"Story_{s}.xml"))
dm_path = os.path.join(WORK, "designmap.xml")
dm = open(dm_path, encoding="utf-8").read()
for s in gone:
    dm = re.sub(rf'<idPkg:Story src="Stories/Story_{s}\.xml"\s*/>', "", dm)
m = re.search(r'StoryList="([^"]*)"', dm)
ids = [s for s in m.group(1).split() if s not in gone] + new_ids
dm = dm[:m.start(1)] + " ".join(ids) + dm[m.end(1):]
a = re.search(r'<idPkg:Story src="Stories/Story_[^"]+"\s*/>', dm)
dm = dm[:a.start()] + "".join(f'<idPkg:Story src="Stories/Story_{s}.xml" />' for s in new_ids) + dm[a.start():]
open(dm_path, "w", encoding="utf-8").write(dm)

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
print("ok: added", len(items), "items,", len(new_ids), "stories; removed", len(gone), "stories")
