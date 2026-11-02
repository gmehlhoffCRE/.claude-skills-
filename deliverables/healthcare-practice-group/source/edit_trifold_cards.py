"""Trifold: swap the six analytics deliverable cards under 'Easy To Follow Turn-By-Turn Directions'
for the six How We Help situations (text + icons). Everything else untouched."""
import os, re, shutil, sys, zipfile
from lxml import etree
from idmlkit import Doc, IdmlWriter
from icons_extra import extra_icon

SRC, OUT = sys.argv[1], sys.argv[2]
WORK = OUT + ".d"
shutil.rmtree(WORK, ignore_errors=True)
shutil.copytree(SRC, WORK)
SP = os.path.join(WORK, "Spreads", "Spread_u46e.xml")
tree = etree.parse(SP)
spread = tree.getroot().find("Spread")
CARDS = [  # story, card left x (spread), icon kind, title, text
    ("ud15", -482.0, "pin", "Opening a New Location", "Sites chosen around your patients."),
    ("ud32", -381.5, "network", "Growing Across Markets", "Multi-site rollouts run by one coordinated team."),
    ("ud4d", -281.0, "calendar", "Renewals & Rightsizing", "Better terms on space you already occupy."),
    ("ud6a", -144.5, "target", "Mergers & Integration", "Diligence and consolidation for acquired sites."),
    ("ud90", -44.0, "building", "Relocating Without Disruption", "Moves planned around patient care."),
    ("udac", 56.5, "dollar", "Freeing Up Capital", "Sale-leasebacks and financing for owned facilities."),
]
for sid, _, _, title, text in CARDS:
    p = os.path.join(WORK, "Stories", f"Story_{sid}.xml")
    t = etree.parse(p)
    cs = list(t.iter("Content"))
    # title may be split across runs (e.g. 'Drive-Time ' + line break); put the title in the first run
    for c in cs[:-1]:
        c.text = ""
    cs[0].text = title
    cs[-1].text = text
    for el in list(t.iter()):  # drop forced line breaks inside the title paragraph
        if el.tag == "Content" and el.text == "":
            el.getparent().remove(el)
    t.write(p, xml_declaration=True, encoding="UTF-8", standalone=True)
removed = 0
for el in list(spread):
    if (el.get("Name") or "").startswith("icon ") and el.get("ItemLayer") == "u15e":
        b = [float(v) for v in el.get("ItemTransform").split()]
        pts = [tuple(map(float, p.get("Anchor").split())) for p in el.iter("PathPointType")]
        ys = [b[1] * x + b[3] * y + b[5] for x, y in pts]
        if all(190 <= y <= 215 for y in ys):  # only the icons inside the turn-by-turn cards
            spread.remove(el)
            removed += 1
w = IdmlWriter(Doc("x", 612, 792, 1), None, None)
w.n = 0x9800
w.layer_ids = {"Art": "u15e", "Placeholder Labels": "ub8"}
w._local, w._xf = True, "1 0 0 1 0 0"
items = []
for _, cx, ic, _, _ in CARDS:
    items += extra_icon(ic, cx + 12, 196.8, 14.4)
frag = etree.fromstring("<r>" + "".join(w.item_xml(0, it) for it in items) + "</r>")
for el in list(frag):
    spread.append(el)
tree.write(SP, xml_declaration=True, encoding="UTF-8", standalone=True)
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
print("cards updated; removed", removed, "old icon shapes; added", len(items))
