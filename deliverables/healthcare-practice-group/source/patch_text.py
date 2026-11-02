"""Replace exact text runs in an unpacked IDML's stories, then rezip. Leaves everything else untouched."""
import glob, os, sys, zipfile
from lxml import etree
src, out = sys.argv[1], sys.argv[2]
REPL = {
    "Renewals, options and expirations flagged automatically, so you can negotiate early.":
        "Renewals and options flagged automatically, so you negotiate early.",
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
