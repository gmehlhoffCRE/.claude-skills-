"""Replace exact text runs in an unpacked IDML's stories, then rezip. Leaves everything else untouched."""
import glob, os, sys, zipfile
from lxml import etree
src, out = sys.argv[1], sys.argv[2]
REPL = {
    "Sites weighed on patient access, drive times and clinical talent": "Sites evaluated around your patients and care model",
    "Consistent standards and reporting at every location": "Portfolio standards that keep each new site on budget",
    "Critical dates tracked, so you negotiate early with leverage": "Better rates and concessions on space you already occupy",
    "Lease-level diligence on every acquired location": "Lease-level diligence on acquired sites",
    ("Cresa Core™ is our occupier-focused intelligence platform. It brings your portfolio and market data into one "
     "source of truth, then applies enterprise-grade AI so your Cresa team can model scenarios faster and act with "
     "confidence at every location. Your data stays encrypted, fully governed and never trains outside AI models, so "
     "your data remains private and secure."):
    ("Cresa Core™ is our occupier-focused intelligence platform. It brings your portfolio and market data into one "
     "source of truth, then applies enterprise-grade AI so your Cresa team can model scenarios faster and act with "
     "confidence across your portfolio. All data is encrypted, fully governed and never used to train outside AI models."),
}
done = set()
for f in glob.glob(os.path.join(src, "Stories", "*.xml")):
    t = etree.parse(f); changed = False
    for c in t.iter("Content"):
        if c.text in REPL:
            done.add(c.text); c.text = REPL[c.text]; changed = True
    if changed:
        t.write(f, xml_declaration=True, encoding="UTF-8", standalone=True)
missing = set(REPL) - done
assert not missing, missing
if os.path.exists(out): os.remove(out)
with zipfile.ZipFile(out, "w") as z:
    z.write(os.path.join(src, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
    for root, _, files in os.walk(src):
        for fn in sorted(files):
            full = os.path.join(root, fn); arc = os.path.relpath(full, src)
            if arc != "mimetype": z.write(full, arc, compress_type=zipfile.ZIP_DEFLATED)
print("replaced", len(done), "runs")
