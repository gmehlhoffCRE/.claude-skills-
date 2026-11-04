"""V.03 bifold: case studies become bullet lists (stats + paragraph frames replaced)."""
import os
import re
import shutil
import sys
import zipfile
from xml.sax.saxutils import escape

from lxml import etree

SRC, OUT = sys.argv[1], sys.argv[2]
WORK = OUT + ".d"
shutil.rmtree(WORK, ignore_errors=True)
shutil.copytree(SRC, WORK)
SP = os.path.join(WORK, "Spreads", "Spread_u12c4.xml")
tree = etree.parse(SP)
spread = tree.getroot().find("Spread")
ITEMS = {el.get("Self"): el for el in spread if el.get("Self")}

CASES = {  # body frame/story: (lead-in or None, top y in page coords, bottom y, bullets)
    ("u1918", "u191b"): (None, 334, 404, ["Site selection for 2 new centers", "Favorable lease terms for the practice",
                                          "High-visibility signage"]),
    ("u19ac", "u19af"): (None, 334, 404, ["Site selection for a new location", "[XX]% annual rent savings",
                                          "Favorable lease terms for the practice",
                                          "Landlord funding of space improvements"]),
    ("u1a3e", "u1a41"): (None, 562, 628, ["Lease transactions across the U.S.",
                                          "Consulting, labor analytics, incentives and project management services"]),
    ("u1ace", "u1ad1"): (None, 562, 628, ["Transaction and project management services",
                                          "Downtown Denver headquarters relocation and expansion"]),
}
LEADS = {}   # descriptive titles stay as they are
REMOVE_FRAMES = []   # big-number callouts and titles stay


def set_y(el, y0, y1):
    m = [float(v) for v in el.get("ItemTransform").split()]
    pts = list(el.iter("PathPointType"))
    ys = sorted({float(p.get("Anchor").split()[1]) for p in pts})
    lo, hi = ys[0], ys[-1]
    for p in pts:
        for k in ("Anchor", "LeftDirection", "RightDirection"):
            x, y = map(float, p.get(k).split())
            y = (y0 - 396 - m[5]) if abs(y - lo) < 0.01 else (y1 - 396 - m[5])
            p.set(k, f"{x} {y}")


gone = []
for sid in REMOVE_FRAMES:
    el = ITEMS.pop(sid)
    gone.append(el.get("ParentStory"))
    spread.remove(el)

BULLET = ('<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/Bullet">'
          '<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" FontStyle="45 Light" '
          'PointSize="9.5"><Properties><Leading type="unit">13</Leading></Properties><Content>{}</Content>{}'
          '</CharacterStyleRange></ParagraphStyleRange>')
for (frame, story), (_, y0, y1, bullets) in CASES.items():
    set_y(ITEMS[frame], y0, y1)
    p = os.path.join(WORK, "Stories", f"Story_{story}.xml")
    xml = open(p, encoding="utf-8").read()
    body = "".join(BULLET.format(escape(b), "<Br />" if i < len(bullets) - 1 else "") for i, b in enumerate(bullets))
    xml = re.sub(r"<ParagraphStyleRange.*</ParagraphStyleRange>", lambda _: body, xml, flags=re.S)
    open(p, "w", encoding="utf-8").write(xml)
# typo fix in the MRI callout caption
cap = os.path.join(WORK, "Stories", "Story_u1904.xml")
ct = etree.parse(cap)
for c in ct.iter("Content"):
    c.text = (c.text or "").replace("secuired buildout allowance", "secured build-out allowance")
ct.write(cap, xml_declaration=True, encoding="UTF-8", standalone=True)
for story, lead in LEADS.items():
    p = os.path.join(WORK, "Stories", f"Story_{story}.xml")
    t = etree.parse(p)
    cs = list(t.iter("Content"))
    cs[0].text = lead
    for c in cs[1:]:
        c.getparent().remove(c)
    t.write(p, xml_declaration=True, encoding="UTF-8", standalone=True)
tree.write(SP, xml_declaration=True, encoding="UTF-8", standalone=True)

for s in gone:
    os.remove(os.path.join(WORK, "Stories", f"Story_{s}.xml"))
dm_path = os.path.join(WORK, "designmap.xml")
dm = open(dm_path, encoding="utf-8").read()
for s in gone:
    dm = re.sub(rf'<idPkg:Story src="Stories/Story_{s}\.xml"\s*/>', "", dm)
m = re.search(r'StoryList="([^"]*)"', dm)
dm = dm[:m.start(1)] + " ".join(s for s in m.group(1).split() if s not in gone) + dm[m.end(1):]
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
print("ok: removed", len(gone), "frames")
