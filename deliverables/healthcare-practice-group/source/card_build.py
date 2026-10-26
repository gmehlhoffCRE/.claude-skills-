import os, sys
import idmlkit
from idmlkit import IdmlWriter, proof_html
from card import build_cards
HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "..", "tpl", "a") if os.path.isdir(os.path.join(HERE, "..", "tpl", "a")) else os.path.join(HERE, "idml_base")
OUT = sys.argv[1]
fonts = os.path.join(HERE, "assets", "fonts")
for wt, f in ((400, "400"), (500, "400"), (700, "700"), (800, "800")):
    idmlkit.FONT_FACES.append("@font-face{font-family:'Roboto Condensed';font-weight:%d;"
                              "src:url('file://%s/roboto-condensed-latin-%s-normal.woff2') format('woff2')}" % (wt, fonts, f))
for d in build_cards():
    folder = os.path.join(OUT, d.name)
    os.makedirs(folder, exist_ok=True)
    IdmlWriter(d, TPL, os.path.join(folder, "Links")).write(os.path.join(folder, d.name + ".idml"))
    open(os.path.join(OUT, d.name + "_proof.html"), "w").write(proof_html(d, [[i] for i in range(len(d.pages))]))
    print(d.name)
