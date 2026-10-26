import os, sys
import idmlkit
from idmlkit import IdmlWriter, proof_html
from trifold import build_trifold
HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "..", "tpl", "a") if os.path.isdir(os.path.join(HERE, "..", "tpl", "a")) else os.path.join(HERE, "idml_base")
OUT = sys.argv[1]
fonts = os.path.join(HERE, "assets", "fonts")
for wt, f in ((400, "400"), (500, "400"), (700, "700"), (800, "800")):
    idmlkit.FONT_FACES.append("@font-face{font-family:'Roboto Condensed';font-weight:%d;"
                              "src:url('file://%s/roboto-condensed-latin-%s-normal.woff2') format('woff2')}" % (wt, fonts, f))
d = build_trifold()
folder = os.path.join(OUT, d.name)
os.makedirs(folder, exist_ok=True)
IdmlWriter(d, TPL, os.path.join(folder, "Links")).write(os.path.join(folder, d.name + ".idml"))
open(os.path.join(OUT, d.name + "_proof.html"), "w").write(proof_html(d, [[0], [1]]))
open(os.path.join(OUT, d.name + "_proof_bleed.html"), "w").write(proof_html(d, [[0], [1]], show_bleed=True))
print("ok", sum(len(p) for p in d.pages), "items")
