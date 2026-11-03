"""Approximate renderer: draws each spread of an IDML package to HTML (SVG shapes + HTML text) for proofing."""
import html
import os
import sys
import zipfile

from lxml import etree

from idmlkit import SWATCHES

WEIGHT = {"thin": 200, "light": 300, "roman": 400, "regular": 400, "medium": 500, "bold": 700, "heavy": 800,
          "black": 900}


def font_css(style):
    s = (style or "55 Roman").lower()
    w = next((v for k, v in WEIGHT.items() if k in s), 400)
    fam = "'Roboto Condensed','Arial Narrow',sans-serif" if "cond" in s else "'Inter',Arial,sans-serif"
    return f"font-family:{fam};font-weight:{w};" + ("font-style:italic;" if "italic" in s else "")


class Idml:
    def __init__(self, path, assets):
        self.z = zipfile.ZipFile(path)
        self.assets = assets
        self.colors = self._colors()
        self.pstyles, self.cstyles = self._styles()

    def xml(self, name):
        return etree.fromstring(self.z.read(name))

    def _colors(self):
        cols = {"Swatch/None": None, "Color/Paper": "#FFFFFF", "Color/Black": "#1A1A1A"}
        for c in self.xml("Resources/Graphic.xml").iter("Color"):
            name = c.get("Name")
            if name in SWATCHES:
                cols[c.get("Self")] = SWATCHES[name][1]
                continue
            vals = [float(v) for v in (c.get("ColorValue") or "0 0 0 0").split()]
            if c.get("Space") == "RGB":
                r, g, b = vals[:3]
            else:
                cc, mm, yy, kk = [v / 100 for v in (vals + [0, 0, 0, 0])[:4]]
                r, g, b = [255 * (1 - x) * (1 - kk) for x in (cc, mm, yy)]
            cols[c.get("Self")] = f"#{int(r):02X}{int(g):02X}{int(b):02X}"
        return cols

    def color(self, ref, tint=None):
        hexc = self.colors.get(ref)
        if not hexc:
            return None
        if tint not in (None, "-1", "100", -1):
            t = float(tint) / 100
            r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
            hexc = "#%02X%02X%02X" % tuple(round(255 - (255 - v) * t) for v in (r, g, b))
        return hexc

    def _styles(self):
        st = self.xml("Resources/Styles.xml")

        def collect(tag):
            raw = {}
            for s in st.iter(tag):
                d = dict(s.attrib)
                props = s.find("Properties")
                if props is not None:
                    for p in props:
                        if p.tag in ("Leading", "BasedOn", "AppliedFont"):
                            d[p.tag] = p.text
                        if p.tag == "BulletChar":
                            d["BulletChar"] = p.get("BulletCharacterValue")
                        if p.tag == "BulletsCharacterStyle":
                            d["BulletsCharacterStyle"] = p.text
                raw[s.get("Self")] = d
            return raw
        return collect("ParagraphStyle"), collect("CharacterStyle")

    def resolve(self, table, ref, prefix):
        out, seen = {}, set()
        chain = []
        while ref and ref not in seen and ref in table:
            seen.add(ref)
            chain.append(table[ref])
            b = table[ref].get("BasedOn")
            ref = (prefix + b) if b and not b.startswith(prefix) else b
        for d in reversed(chain):
            out.update(d)
        return out


def mat(s):
    return [float(v) for v in (s or "1 0 0 1 0 0").split()]


def mul(a, b):
    return [a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1], a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3],
            a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5]]


def ap(m, x, y):
    return m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5]


def text_css(doc, attrs):
    css = font_css(attrs.get("FontStyle"))
    if attrs.get("PointSize"):
        css += f"font-size:{attrs['PointSize']}pt;"
    lead = attrs.get("Leading")
    if lead and lead != "Auto":
        css += f"line-height:{lead}pt;"
    col = doc.color(attrs.get("FillColor"), attrs.get("FillTint"))
    if col:
        css += f"color:{col};"
    if attrs.get("Tracking") not in (None, ""):
        css += f"letter-spacing:{float(attrs['Tracking']) / 1000}em;"
    cap = attrs.get("Capitalization")
    if cap == "AllCaps":
        css += "text-transform:uppercase;"
    elif cap == "Normal":
        css += "text-transform:none;"
    return css


def render_story(doc, sid):
    try:
        st = etree.fromstring(doc.z.read(f"Stories/Story_{sid}.xml"))
    except KeyError:
        return ""
    out = []
    for psr in st.iter("ParagraphStyleRange"):
        ps = doc.resolve(doc.pstyles, psr.get("AppliedParagraphStyle"), "ParagraphStyle/")
        ps.update({k: v for k, v in psr.attrib.items() if k != "AppliedParagraphStyle"})
        just = {"CenterAlign": "center", "RightAlign": "right"}.get(ps.get("Justification"), "left")
        pcss = text_css(doc, ps) + f"text-align:{just};margin:0 0 {ps.get('SpaceAfter', 0)}pt 0;" \
            f"padding-top:{ps.get('SpaceBefore', 0)}pt;padding-left:{ps.get('LeftIndent', 0)}pt;" \
            f"text-indent:{ps.get('FirstLineIndent', 0)}pt;"
        bullet = ""
        if ps.get("BulletsAndNumberingListType") == "BulletList":
            bcs = doc.resolve(doc.cstyles, ps.get("BulletsCharacterStyle"), "CharacterStyle/")
            bcol = doc.color(bcs.get("FillColor")) or "inherit"
            bullet = (f'<span style="display:inline-block;width:{ps.get("LeftIndent", 0)}pt;text-indent:0;'
                      f'color:{bcol}">{chr(int(ps.get("BulletChar", "8226")))}</span>')
        cur = []
        for csr in psr.iter("CharacterStyleRange"):
            cs = doc.resolve(doc.cstyles, csr.get("AppliedCharacterStyle"), "CharacterStyle/")
            local = {k: v for k, v in csr.attrib.items() if k != "AppliedCharacterStyle"}
            props = csr.find("Properties")
            if props is not None and props.find("Leading") is not None:
                local["Leading"] = props.find("Leading").text
            css = text_css(doc, {**cs, **local})
            for node in csr:
                if node.tag == "Content":
                    cur.append(f'<span style="{css}">{html.escape(node.text or "").replace(chr(0x2028), "<br>")}</span>')
                elif node.tag == "Br":
                    out.append(f'<p style="{pcss}">{bullet}{"".join(cur) or "&nbsp;"}</p>')
                    cur = []
        if cur:
            out.append(f'<p style="{pcss}">{bullet}{"".join(cur)}</p>')
    return "".join(out)


def path_d(el, m):
    d = []
    for gp in el.iter("GeometryPathType"):
        pts = []
        for p in gp.iter("PathPointType"):
            pts.append([ap(m, *map(float, p.get(k).split())) for k in ("Anchor", "LeftDirection", "RightDirection")])
        if not pts:
            continue
        d.append(f"M{pts[0][0][0]:.2f},{pts[0][0][1]:.2f}")
        segs = list(zip(pts, pts[1:]))
        if gp.get("PathOpen") == "false":
            segs.append((pts[-1], pts[0]))
        for a, b in segs:
            d.append(f"C{a[2][0]:.2f},{a[2][1]:.2f} {b[1][0]:.2f},{b[1][1]:.2f} {b[0][0]:.2f},{b[0][1]:.2f}")
        if gp.get("PathOpen") == "false":
            d.append("Z")
    return " ".join(d)


CLIP = [0]


def render_spread(doc, name, hidden_layers, show_labels):
    sp = doc.xml(name).find("Spread")
    pages = []
    for pg in sp.iter("Page"):
        pm = mat(pg.get("ItemTransform"))
        y0, x0, y1, x1 = map(float, pg.get("GeometricBounds").split())
        pages.append((ap(pm, x0, y0), ap(pm, x1, y1)))
    minx, miny = min(p[0][0] for p in pages), min(p[0][1] for p in pages)
    maxx, maxy = max(p[1][0] for p in pages), max(p[1][1] for p in pages)
    W, H = maxx - minx, maxy - miny
    svg, texts = [], []

    def walk(el, m):
        for ch in el:
            if ch.tag not in ("Rectangle", "Oval", "Polygon", "GraphicLine", "TextFrame", "Group"):
                continue
            if ch.get("ItemLayer") in hidden_layers or ch.get("Visible") == "false":
                continue
            if ch.get("ItemLayer") and not show_labels and ch.get("ItemLayer") == doc.label_layer:
                continue
            mm = mul(m, mat(ch.get("ItemTransform")))
            if ch.tag == "Group":
                walk(ch, mm)
                continue
            d = path_d(ch, mm)
            if ch.tag == "TextFrame":
                xs, ys = [], []
                for p in ch.iter("PathPointType"):
                    x, y = ap(mm, *map(float, p.get("Anchor").split()))
                    xs.append(x)
                    ys.append(y)
                ins = [0, 0, 0, 0]
                tfp = ch.find("TextFramePreference")
                vj = "flex-start"
                if tfp is not None:
                    vj = {"CenterAlign": "center", "BottomAlign": "flex-end"}.get(tfp.get("VerticalJustification"),
                                                                                  "flex-start")
                    lst = tfp.find("Properties/InsetSpacing")
                    if lst is not None:
                        ins = [float(i.text) for i in lst]
                texts.append(f'<div class="t" style="left:{min(xs) - minx}pt;top:{min(ys) - miny}pt;'
                             f'width:{max(xs) - min(xs)}pt;height:{max(ys) - min(ys)}pt;padding:{ins[0]}pt {ins[3]}pt '
                             f'{ins[2]}pt {ins[1]}pt;justify-content:{vj}"><div>{render_story(doc, ch.get("ParentStory"))}'
                             f'</div></div>')
                continue
            fill = doc.color(ch.get("FillColor"), ch.get("FillTint"))
            stroke = doc.color(ch.get("StrokeColor"))
            sw = float(ch.get("StrokeWeight", "1") or 1)
            svg.append(f'<path d="{d}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}" '
                       f'stroke-linecap="round" stroke-linejoin="round" transform="translate({-minx},{-miny})"/>')
            img = ch.find("Image")
            if img is not None:
                link = img.find("Link")
                fn = os.path.basename((link.get("LinkResourceURI") if link is not None else "") or "")
                src = os.path.join(doc.assets, fn.replace("%20", " "))
                gb = img.find("Properties/GraphicBounds")
                if os.path.exists(src) and gb is not None:
                    im = mul(mm, mat(img.get("ItemTransform")))
                    gw, gh = float(gb.get("Right")) - float(gb.get("Left")), float(gb.get("Bottom")) - float(gb.get("Top"))
                    CLIP[0] += 1
                    clip = f"clip{CLIP[0]}"
                    svg.append(f'<clipPath id="{clip}"><path d="{d}" transform="translate({-minx},{-miny})"/></clipPath>'
                               f'<g clip-path="url(#{clip})"><image href="file://{src}" x="0" y="0" width="{gw}" '
                               f'height="{gh}" preserveAspectRatio="none" transform="translate({-minx},{-miny}) '
                               f'matrix({" ".join(f"{v:.5f}" for v in im)})"/></g>')
    walk(sp, [1, 0, 0, 1, 0, 0])
    return W, H, (f'<section class="sheet" style="width:{W}pt;height:{H}pt">'
                  f'<svg width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0">'
                  f'{"".join(svg)}</svg>{"".join(texts)}</section>')


def main(path, assets, out_html, fonts_dir, show_labels=True):
    doc = Idml(path, assets)
    dm = doc.xml("designmap.xml")
    doc.label_layer = None
    hidden = set()
    for lay in dm.iter("Layer"):
        if lay.get("Visible") == "false":
            hidden.add(lay.get("Self"))
        if "Placeholder" in (lay.get("Name") or ""):
            doc.label_layer = lay.get("Self")
    spreads = [e.get("src") for e in dm if (e.get("src") or "").startswith("Spreads/")]
    css = ["*{box-sizing:border-box}body{margin:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}",
           ".sheet{position:relative;overflow:hidden;background:#fff;break-after:page}",
           ".t{position:absolute;display:flex;flex-direction:column}.t p{margin:0}"]
    for wt, f in ((400, "400"), (500, "400"), (700, "700"), (800, "800")):
        css.append("@font-face{font-family:'Roboto Condensed';font-weight:%d;src:url('file://%s/roboto-condensed-latin-%s-normal.woff2')}"
                   % (wt, fonts_dir, f))
    body = []
    for k, s in enumerate(spreads):
        W, H, sec = render_spread(doc, s, hidden, show_labels)
        css.append(f"@page p{k}{{size:{W}pt {H}pt;margin:0}} .s{k}{{page:p{k}}}")
        body.append(sec.replace('class="sheet"', f'class="sheet s{k}"', 1))
    open(out_html, "w").write(f'<!doctype html><html><head><meta charset="utf-8"><style>{"".join(css)}</style>'
                              f'</head><body>{"".join(body)}</body></html>')


if __name__ == "__main__":
    main(*sys.argv[1:5])
