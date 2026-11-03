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
set_text("u12dc", ["Expanding imaging access across Texas"])
set_text("u12f3", ["[XX]"]); set_text("u130a", ["imaging centers"])
set_text("u1321", ["[XX]"]); set_text("u1339", ["markets served"])
set_text("u1350", ["Site selection, lease negotiation and build-out oversight as MRI Centers of Texas [expanded] its "
                   "outpatient imaging network across [markets], with leases built around equipment, shielding and "
                   "power needs. [Add result: savings, timeline or centers opened.]"])
set_text("u136b", ["A national care network, managed as one"])
set_text("u1382", ["[XX]"]); set_text("u1399", ["locations"])
set_text("u13b0", ["[XX]"]); set_text("u13c7", ["states"])
set_text("u13de", ["Transaction management and portfolio support across Aveanna Healthcare’s [branch] locations in "
                   "[X] states, with consistent lease terms, every critical date tracked and one point of contact. "
                   "[Add result: savings, renewals completed or portfolio change.]"])
path, tree, spread = load("Spread_u12c4.xml")
labels = []
for el in spread:
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
        translate(el, 0, 236 - 451.6)

items = [
    T(36, 252, 540, 30, [("H2 Small", [(None, "Local expertise. "), ("Emphasis Medium", "National reach.")])]),
    Image(36 + PX, 292 + PY, 340, 222, MAP, align="l", valign="t", name="Map: Cresa offices, North America"),
    T(396, 296, 180, 40, [("Stat Number", "55+")]),
    T(396, 338, 180, 26, [("Stat Label", "Cresa offices across North America")]),
    T(396, 376, 180, 140, [("Body Small",
                            "Your Houston team brings local market knowledge, backed by Cresa’s national "
                            "healthcare experience and offices across North America. Through "
                            "Knight Frank Cresa, that reach extends to more than 300 offices worldwide, so we’re "
                            "where you need us.")]),
]
for k, (n, lab) in enumerate((("1,350+", "Team members"), ("720+", "Cities served worldwide"),
                              ("300+", "Global offices with Knight Frank"))):
    x = 36 + k * 180
    items += [T(x, 562, 170, 26, [("Stat Number Small", n)]), T(x, 588, 170, 12, [("Caption", lab)])]
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
