import os, sys
from idmlkit import IdmlWriter, proof_html
from layouts import build_onepager, build_bifold
HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "..", "tpl", "a") if os.path.isdir(os.path.join(HERE, "..", "tpl", "a")) else os.path.join(HERE, "idml_base")
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
for houston in (False, True):
    for d, sheets in ((build_onepager(houston), [[0], [1]]), (build_bifold(houston), [[0], [1, 2], [3]])):
        folder = os.path.join(OUT, d.name)
        os.makedirs(folder, exist_ok=True)
        IdmlWriter(d, TPL, os.path.join(folder, "Links")).write(os.path.join(folder, d.name + ".idml"))
        open(os.path.join(OUT, d.name + "_proof.html"), "w").write(proof_html(d, sheets))
        if "Bifold" in d.name:
            # print imposition: outside = back + cover, inside = 2-3
            open(os.path.join(OUT, d.name + "_imposed.html"), "w").write(proof_html(d, [[3, 0], [1, 2]], show_bleed=True))
print("ok")
