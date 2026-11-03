"""V.02 bifold: MRI Centers of Texas + Aveanna case drafts (inside), back page = no conflicts on top + office map."""
import os
import re
import shutil
import sys
import zipfile

from lxml import etree

from idmlkit import Doc, IdmlWriter, Image, Text

SRC, OUT, MAP = sys.argv[1], sys.argv[2], sys.argv[3]
WORK = OUT + ".d"
shutil.rmtree(WORK, ignore_errors=True)
shutil.copytree(SRC, WORK)
ST = os.path.join(WORK, "Stories")
PX, PY = -612.0, -396.0     # both edited pages are left-hand pages: page coords -> spread coords


def set_text(sid, new):
    p = os.path.join(ST, f"Story_{sid}.xml")
    t = etree.parse(p)
    cs = list(t.iter("Content"))
    assert len(cs) == len(new), (sid, [c.text for c in cs])
    for c, txt in zip(cs, new):
        if txt is not None:
            c.text = txt
    t.write(p, xml_declaration=True, encoding="UTF-8", standalone=True)


def load(name):
    path = os.path.join(WORK, "Spreads", name)
    tree = etree.parse(path)
    return path, tree, tree.getroot().find("Spread")


def translate(el, dx, dy):
    m = [float(v) for v in el.get("ItemTransform").split()]
    m[4] += dx
    m[5] += dy
    el.set("ItemTransform", " ".join(repr(v) for v in m))


def writer(n0):
    w = IdmlWriter(Doc("x", 612, 792, 1), None, None)
    w.n = n0
    w.layer_ids = {"Art": "u142", "Placeholder Labels": "ub8"}
    w._local, w._xf = True, "1 0 0 1 0 0"
    return w


LOCAL = ('<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" FontStyle="45 Light" '
         'PointSize="8.5"><Properties><Leading type="unit">12</Leading></Properties>')
new_stories, gone_stories = [], []


def emit(spread, w, items):
    xml = "".join(w.item_xml(0, it) for it in items)
    for sid, sx in w.stories:
        sx = sx.replace('<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/Body Small">'
                        '<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]">',
                        '<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/Body Small">' + LOCAL)
        open(os.path.join(ST, f"Story_{sid}.xml"), "w", encoding="utf-8").write(sx)
        new_stories.append(sid)
    w.stories = []
    for el in etree.fromstring(f"<r>{xml}</r>"):
        spread.append(el)


def T(x, y, w, h, paras, **kw):   # page coords -> spread coords
    return Text(x + PX, y + PY, w, h, paras, **kw)


# ================================================================ inside: top-row case studies
set_text("u12dc", ["Two new imaging centers, built to be seen"])
set_text("u12f3", ["2"]); set_text("u130a", ["new MRI centers"])
set_text("u1321", ["14.5K"]); set_text("u1339", ["SF across two sites"])
set_text("u1350", ["To expand in Southeast Texas, MRI Centers of Texas opened centers in Katy and near the Texas "
                   "Medical Center, with long-term leases, significant landlord-funded improvements and standout "
                   "signage, including a high-rise pole sign on US-59."])
set_text("u136b", ["Leverage that turned a renewal into a better move"])
set_text("u1382", ["$500K"]); set_text("u1399", ["rent savings over 5 years"])
set_text("u13b0", ["10"]); set_text("u13c7", ["old HVAC units avoided"])
set_text("u13de", ["Aveanna needed to shed 5,000 SF of its 15,000 SF clinic, including a therapy pool, while facing "
                   "aging HVAC and a proposed rent increase. Touring alternatives created leverage, but the best "
                   "answer was a turnkey relocation with all-new HVAC and $500K in rent savings."])
path, tree, spread = load("Spread_u12c4.xml")
labels = []
for el in spread:
    if el.get("Self") in ("u134d", "u13db"):
        pts = list(el.iter("PathPointType"))
        ymax = max(float(p.get("Anchor").split()[1]) for p in pts)
        for p in pts:
            for k in ("Anchor", "LeftDirection", "RightDirection"):
                x_, y_ = map(float, p.get(k).split())
                if abs(y_ - ymax) < 0.01:
                    p.set(k, f"{x_} {y_ + 14}")
    if el.get("Self") in ("u12d5", "u1364"):
        for ch in list(el):
            if ch.tag in ("Image", "PDF", "EPS"):
                el.remove(ch)
        name = "MRI Centers of Texas" if el.get("Self") == "u12d5" else "Aveanna Healthcare"
        el.set("Name", f"Logo: {name}")
        x0 = -576.0 if el.get("Self") == "u12d5" else -294.0
        labels.append(Text(x0, 205.3 + PY, 121, 36, [("zz Placeholder Label", f"Logo: {name}")], valign="center",
                           layer="Placeholder Labels"))
emit(spread, writer(0x9a00), labels)
tree.write(path, xml_declaration=True, encoding="UTF-8", standalone=True)

# ================================================================ back page
path, tree, spread = load("Spread_u189.xml")
REMOVE = set("""uf28 uf3f uf48 uf49 uf60 uf78 uf8f ufa6 ufbd ufd4 ufda ufdb uff2 u1009 u1020 u1037 u104e u1065
u115f u1165 u116c u1174 u117b u1182 u1188 u1190 u1197 u119e u11a4 u11ab u11d7""".split())
REMOVE_STORIES = "uf2b uf4c uf64 uf7b uf92 ufa9 ufc0 ufde uff5 u100c u1023 u103a u1051 u11da".split()
for el in list(spread):
    if el.get("Self") in REMOVE:
        spread.remove(el)
        REMOVE.discard(el.get("Self"))
assert not REMOVE, REMOVE
gone_stories += REMOVE_STORIES
DY = 64 - 471.9                      # no-conflicts block to the top of the page
for el in spread:
    if el.get("Self") in ("u112f", "u1146", "u115e", "u120c"):
        translate(el, 0, DY)
    if el.get("Self") == "u1116":    # divider under no-conflicts
        translate(el, 0, 338 - 451.6)

from idmlkit import Rect
items = [T(36, 236, 300, 18, [("H3", "Why It Matters to You")])]
WHY = ["No obligations to landlords", "Freedom to negotiate more aggressively", "A platform solely dedicated to occupiers",
       "Unbiased, objective client representation", "Consistent cost savings for our clients"]
cw5 = (540 - 4 * 12) / 5
for k, t in enumerate(WHY):
    x = 36 + k * (cw5 + 12)
    items += [Rect(x + PX, 260 + PY, cw5, 2.5, fill="Goldenrod", name="why rule"),
              T(x, 268, cw5, 10, [("Eyebrow", f"{k + 1:02d}")]),
              T(x, 282, cw5, 46, [("H4", t)])]
# offices: map left, copy right
items += [
    Image(36 + PX, 356 + PY, 336, 219, MAP, align="l", valign="t", name="Map: Cresa offices, North America"),
    T(304, 522, 76, 50, [("Stat Number", "55+")]),
    T(304, 562, 72, 26, [("Stat Label", "Cresa offices in North America")]),
    T(390, 354, 186, 54, [("H2 Small", [(None, "We think\n"), ("Emphasis Medium", "beyond space.")])]),
    T(390, 414, 186, 210, [
        ("Body Small", "By aligning real estate decisions with business needs, Cresa helps you discover unseen "
                       "opportunities, reduce risk, improve outcomes and secure a competitive edge for your people "
                       "and your organization, anywhere around the globe."),
        ("Body Small", " "),
        ("Body Small", "Each of our services is fully scalable, so your team can move quickly as your needs evolve, "
                       "regardless of location. By integrating every service line through a single point of "
                       "contact, we connect the dots so you don\u2019t have to, and you can focus on what matters "
                       "most: your patients and your organization."),
    ]),
]
emit(spread, writer(0x9b00), items)
tree.write(path, xml_declaration=True, encoding="UTF-8", standalone=True)

# ================================================================ designmap + links + zip
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
print("ok: +", len(new_stories), "stories, -", len(gone_stories), "stories")
