"""Edit the user's InDesign-saved bifold IDML in place: service lines + Cresa Core on the analytics page,
light copy changes elsewhere. Everything not listed here is left exactly as the user saved it."""
import math
import os
import re
import shutil
import sys
import zipfile

from lxml import etree

from idmlkit import Doc, IdmlWriter, Oval, Path, Rect, Text
from layouts import icon

SRC_DIR, OUT_IDML = sys.argv[1], sys.argv[2]
WORK = OUT_IDML + ".d"
shutil.rmtree(WORK, ignore_errors=True)
shutil.copytree(SRC_DIR, WORK)
SPREAD = os.path.join(WORK, "Spreads", "Spread_u189.xml")
ART, LABELS = "u142", "ub8"

# ---------------------------------------------------------------- 1. text-only edits (same run structure)
EDITS = {
    "u174": [None, None, None, None, "Conflict-free real estate advisory built  specifically with healthcare "
                                     "occupiers in mind."],
    "u230": [None, None, None, None, "Transaction Management", "Location Advisory", "Project & Development Services",
             "Portfolio Solutions", "Lease Administration", "Strategic Consulting", "Workplace Solutions",
             "Capital Strategies"],
    "u85f": [None, "Scan to schedule a conversation with our healthcare team."],
    "u399": ["Real estate built around care.\u2028", "One team for every site and stage."],
    "u3af": ["From the first market study to every renewal after, Cresa’s integrated service lines work as one "
             "team on your side. Here’s how each one helps healthcare organizations grow, operate and adapt "
             "with confidence."],
    "ua00": ["Cresa Core™"],
    "u568": [None, "Recommendations grounded in market data and Cresa Core™ insight that you can defend to "
                   "leadership and lenders."],
    "u580": [None, "Sites chosen for patient access, clinical talent and total occupancy cost, not just rooftops "
                   "and traffic counts."],
    "u5b0": [None, "Conflict-free guidance that carries the relationship beyond one transaction into ongoing "
                   "portfolio strategy."],
    "u276": ["Assess", "Review your markets and current portfolio"],
    "u2a3": [None, "Prioritize the ", "right markets"],
    "u2fd": [None, "Weigh access to ", "clinical talent"],
    "u32a": ["Negotiate", "Secure the best ", "terms and incentives"],
    "u357": ["Deliver", "Manage build-out through move-in"],
    "u36d": ["From first market study to move-in day. ",
             "One Cresa team manages every step, from location strategy and lease negotiation to project delivery "
             "and lease administration."],
}
for sid, new in EDITS.items():
    p = os.path.join(WORK, "Stories", f"Story_{sid}.xml")
    tree = etree.parse(p)
    contents = list(tree.iter("Content"))
    assert len(contents) == len(new), (sid, len(contents), [c.text for c in contents])
    for c, txt in zip(contents, new):
        if txt is not None:
            c.text = txt
    tree.write(p, xml_declaration=True, encoding="UTF-8", standalone=True)

# ---------------------------------------------------------------- 2. remove old analytics tiles + deliverable cards
REMOVE_ITEMS = set("""u3c4 u3c5 u3c6 u3da u3dd u3de u3f2 u3f5 u3f6 u40a u40d u40e u40f u410 u411 u412 u426 u429 u42a
u42b u42c u42d u42e u42f u430 u431 u432 u433 u434 u435 u436 u44a u44d u44e u462
ua14 ua15 ua16 ua17 ua18 ua19 ua1a ua31 ua33 ua34 ua35 ua36 ua37 ua38 ua39 ua50 ua51 ua52 ua53 ua54 ua55
ua6c ua6d ua6e ua6f ua70 ua71 ua72 ua73 ua8a ua8b ua8c ua8d ua8e ua8f ua90""".split())
REMOVE_STORIES = "u3c8 u3e0 u3f8 u414 u438 u450 ua1d ua3c ua58 ua76 ua93".split()
sp_tree = etree.parse(SPREAD)
spread = sp_tree.getroot().find("Spread")
removed = 0
for el in list(spread):
    if el.get("Self") in REMOVE_ITEMS:
        spread.remove(el)
        removed += 1
assert removed == len(REMOVE_ITEMS), (removed, len(REMOVE_ITEMS))
for sid in REMOVE_STORIES:
    os.remove(os.path.join(WORK, "Stories", f"Story_{sid}.xml"))


# ---------------------------------------------------------------- 3. new items
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


SERVICES = [
    ("key", "Transaction Management",
     "Leases negotiated for clinics and medical offices, from new sites to renewals, subleases and exits."),
    ("pin", "Location Advisory",
     "Site selection that weighs patient access, clinical talent, total occupancy cost and incentives."),
    ("building", "Project & Development Services",
     "Clinical build-outs, relocations and multi-site programs delivered on time and on budget."),
    ("network", "Portfolio Solutions",
     "Standards, benchmarking and scenario planning across every location you operate."),
    ("calendar", "Lease Administration",
     "Critical dates, invoice validation and lease audits across your entire clinic network."),
    ("target", "Strategic Consulting",
     "Operating models, cost reduction and M&A support as healthcare organizations combine and grow."),
    ("people", "Workplace Solutions",
     "Occupancy planning and test fits for clinical and administrative space before you commit."),
    ("dollar", "Capital Strategies",
     "Sale-leasebacks, financing and owner-occupied development that free capital for care."),
]
CORE = [
    ("pin", "Core Site Selection", "Weighted scoring, drive-time analysis and side-by-side site comparisons."),
    ("people", "Core Labor Analytics", "200M+ data points on talent, wages and commutes, down to street level."),
    ("rank", "Core Transaction Management", "Deal tracking, AI market briefs and portfolio impact reports."),
    ("grid", "Core Project Management", "Budgets, milestones and cash-flow forecasts that keep build-outs on track."),
    ("workbook", "Core Lease Administration & Accounting", "AI lease abstraction, critical-date alerts and ASC 842 "
                                                           "compliance."),
    ("chart", "Core Business Intelligence", "Custom dashboards, KPI alerts and interactive mapping across your "
                                             "portfolio."),
]

items = []
M = 36
cw4 = (612 - 2 * M - 3 * 12) / 4
for k, (ic, t, desc) in enumerate(SERVICES):
    col, row = k % 4, k // 4
    x, y = M + col * (cw4 + 12), 204 + row * 98
    items += extra_icon(ic, x, y + 1, 18)
    items.append(Text(x + 26, y, cw4 - 26, 94, [("H4", t), ("Body Small", desc)]))

items.append(Text(276, 418, 300, 12, [("Practice Label Right", "Powered by CresaAI  |  Built on OpenAI")]))
cw3 = (612 - 2 * M - 2 * 10) / 3
for k, (ic, t, desc) in enumerate(CORE):
    col, row = k % 3, k // 3
    x, y = M + col * (cw3 + 10), 440 + row * 80
    items += [Rect(x, y, cw3, 76, fill=None, stroke="Light Gray", sw=1, name="core card"),
              Rect(x, y, cw3, 3, fill="Goldenrod", name="core accent")]
    items += extra_icon(ic, x + 10, y + 14, 16)
    items.append(Text(x + 34, y + 10, cw3 - 42, 63, [("H4", t), ("Body Small", desc)]))

doc = Doc("edit", 612, 792, 4)
w = IdmlWriter(doc, None, None)
w.n = 0x5000
w.layer_ids = {"Art": ART, "Placeholder Labels": LABELS}
new_xml = "".join(w.item_xml(2, it) for it in items)

BODY_SMALL_OPEN = ('<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/Body Small">'
                   '<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]">')
BODY_SMALL_LOCAL = ('<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/Body Small">'
                    '<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" '
                    'FontStyle="45 Light" PointSize="8.5"><Properties><Leading type="unit">12</Leading></Properties>')
new_story_ids = []
for sid, xml in w.stories:
    xml = xml.replace(BODY_SMALL_OPEN, BODY_SMALL_LOCAL)
    with open(os.path.join(WORK, "Stories", f"Story_{sid}.xml"), "w", encoding="utf-8") as f:
        f.write(xml)
    new_story_ids.append(sid)

frag = etree.fromstring(f'<root xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging">{new_xml}</root>')
for el in list(frag):
    spread.append(el)
sp_tree.write(SPREAD, xml_declaration=True, encoding="UTF-8", standalone=True)

# ---------------------------------------------------------------- 4. designmap: story list + story refs
dm_path = os.path.join(WORK, "designmap.xml")
dm = open(dm_path, encoding="utf-8").read()
for sid in REMOVE_STORIES:
    dm = dm.replace(f'<idPkg:Story src="Stories/Story_{sid}.xml"/>', "").replace(
        f'<idPkg:Story src="Stories/Story_{sid}.xml" />', "")
m = re.search(r'StoryList="([^"]*)"', dm)
ids = [s for s in m.group(1).split() if s not in REMOVE_STORIES] + new_story_ids
dm = dm[:m.start(1)] + " ".join(ids) + dm[m.end(1):]
anchor = re.search(r'<idPkg:Story src="Stories/Story_[^"]+"\s*/>', dm)
dm = dm[:anchor.start()] + "".join(f'<idPkg:Story src="Stories/Story_{s}.xml" />' for s in new_story_ids) + \
    dm[anchor.start():]
open(dm_path, "w", encoding="utf-8").write(dm)

# ---------------------------------------------------------------- 5. zip
if os.path.exists(OUT_IDML):
    os.remove(OUT_IDML)
with zipfile.ZipFile(OUT_IDML, "w") as z:
    z.write(os.path.join(WORK, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
    for root, _, files in os.walk(WORK):
        for fn in sorted(files):
            full = os.path.join(root, fn)
            arc = os.path.relpath(full, WORK)
            if arc != "mimetype":
                z.write(full, arc, compress_type=zipfile.ZIP_DEFLATED)
print("edited", len(EDITS), "stories; removed", removed, "items; added", len(items), "items,", len(new_story_ids),
      "stories")
