import os, importlib
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import Color
from xml.sax.saxutils import escape
spec = importlib.import_module(os.environ.get("SPEC", "bpo_spec"))
LINKS = os.environ["LINKS"]
pdfmetrics.registerFont(TTFont("R", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("B", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"))
H = spec.H


def col(name, a=1.0):
    rgb = (255, 255, 255) if name == "Paper" else spec.COLORS[name]
    return Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, alpha=a)


def pstyle(name, j=None):
    fs, size, lead, c, jj, ex = spec.PSTYLES[name]
    return ParagraphStyle(name, fontName="B" if "Bold" in fs else "R", fontSize=size, leading=lead, textColor=col(c),
                          alignment={"LeftAlign": TA_LEFT, "CenterAlign": TA_CENTER, "RightAlign": TA_RIGHT}[j or jj], spaceAfter=ex.get("SpaceAfter", 0))


def flow(paras):
    out = []
    for st, runs in paras:
        j = None; html = ""
        for t, o in runs:
            j = o.get("Justification", j)
            s = escape(t).replace("\u2028", "<br/>").replace("\t", "&nbsp;&nbsp;&nbsp;")
            if "Bold" in o.get("FontStyle", ""): s = f'<font name="B">{s}</font>'
            if "PointSize" in o: s = f'<font size="{o["PointSize"]}">{s}</font>'
            html += s
        out.append(Paragraph(html or "&nbsp;", pstyle(st, j)))
    return out


def draw_text(c, it):
    x, y, w, h = it["x"], it["y"], it["w"], it["h"]
    if it.get("fill"): c.setFillColor(col(it["fill"])); c.rect(x, H - y - h, w, h, stroke=0, fill=1)
    t, l, b, r = it["inset"]; fl = flow(it["paras"]); n, g = it["cols"], it["gutter"]
    cw = (w - l - r - g * (n - 1)) / n
    if it["valign"] == "CenterAlign" and n == 1:
        tot = sum(p.wrap(cw, 1000)[1] + p.style.spaceAfter for p in fl) - fl[-1].style.spaceAfter
        yy = H - y - t - ((h - t - b) - tot) / 2
        for p in fl:
            ph = p.wrap(cw, 1000)[1]; p.drawOn(c, x + l, yy - ph); yy -= ph + p.style.spaceAfter
        return
    for k in range(n):
        fr = Frame(x + l + k * (cw + g), H - y - h + b, cw, h - t - b, 0, 0, 0, 0)
        while fl:
            if fr.add(fl[0], c): fl.pop(0); continue
            parts = fr.split(fl[0], c)
            if len(parts) >= 2 and fr.add(parts[0], c): fl[0:1] = parts[1:]
            break
    if fl: print("OVERSET in", it.get("name"))


def draw_table(c, it):
    y = it["y"]
    for row in it["rows"]:
        xx = it["x"]; ci = 0
        for cell in row["cells"]:
            span = cell.get("span", 1); w = sum(it["colw"][ci:ci + span]); h = row["h"]
            if cell.get("fill"): c.setFillColor(col(cell["fill"])); c.rect(xx, H - y - h, w, h, stroke=0, fill=1)
            if cell.get("bottom"):
                cc, sw = cell["bottom"]; c.setStrokeColor(col(cc)); c.setLineWidth(sw); c.line(xx, H - y - h, xx + w, H - y - h)
            t, l, b, r = cell.get("inset", (2, 4, 2, 4)); fl = flow(cell["paras"]); cw = w - l - r
            tot = sum(p.wrap(cw, 1000)[1] for p in fl)
            if tot > h - t - b + 0.5: print("CELL OVERFLOW", it.get("name"))
            yy = H - y - (h - tot) / 2
            for p in fl:
                ph = p.wrap(cw, 1000)[1]; p.drawOn(c, xx + l, yy - ph); yy -= ph
            xx += w; ci += span
        y += row["h"]


def render(path):
    c = canvas.Canvas(path, pagesize=(spec.W, spec.H))
    for items in spec.PAGES:
        for layer in ("Images", "Content", "Notes"):
            for it in items:
                if it["layer"] != layer: continue
                t = it["t"]
                if t in ("rect", "placeholder"):
                    c.setFillColor(col("Placeholder" if t == "placeholder" else it["fill"], it["opacity"] / 100))
                    c.rect(it["x"], H - it["y"] - it["h"], it["w"], it["h"], stroke=0, fill=1)
                elif t == "poly":
                    c.setFillColor(col(it["fill"])); p = c.beginPath(); pts = it["pts"]; p.moveTo(pts[0][0], H - pts[0][1])
                    for px, py in pts[1:]: p.lineTo(px, H - py)
                    p.close(); c.drawPath(p, stroke=0, fill=1)
                elif t == "line":
                    x1, y1, x2, y2 = it["p"]; c.setStrokeColor(col(it["color"])); c.setLineWidth(it["sw"]); c.line(x1, H - y1, x2, H - y2)
                elif t == "image":
                    fn = LINKS + it["file"]
                    if not os.path.exists(fn): fn = fn.rsplit(".", 1)[0] + ".jpg"
                    c.drawImage(fn, it["x"], H - it["y"] - it["h"], it["w"], it["h"], mask="auto")
                elif t == "text": draw_text(c, it)
                elif t == "table": draw_table(c, it)
        c.showPage()
    c.save()


if __name__ == "__main__":
    import sys; render(sys.argv[1])
