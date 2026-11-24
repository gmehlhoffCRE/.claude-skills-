"""Cresa BPO page layout. Content comes from the property JSON (env PROPERTY) and map geometry (env GEOM).
All units are points, origin top-left, letter landscape 792 x 612. A "\\n" inside any table/callout string becomes a
forced line break (U+2028) in InDesign."""
import os, json

W, H = 792, 612
LOGO, LOGO_AR = "cresa_logo.png", 1500 / 260
RIGHT = 42.4 + 708.6  # right edge of the content area (page gutter); interior logos align to it
COLORS = {"Navy": (0, 30, 90), "Gold": (255, 182, 0), "Blue": (0, 86, 218), "Cell Gray": (233, 233, 233), "Text": (51, 51, 51),
          "Rule": (205, 205, 205), "Rule Light": (140, 155, 192), "Navy Dark": (29, 38, 87), "Placeholder": (213, 218, 227), "Disclaimer Gray": (110, 110, 110)}
PSTYLES = {  # name: (Helvetica Neue LT Pro style, size, leading, color, justification, extras)
    "Cover Address": ("45 Light", 30, 34, "Paper", "LeftAlign", {}), "Cover City": ("45 Light", 16, 20, "Gold", "LeftAlign", {}),
    "Cover Label": ("45 Light", 16, 20, "Paper", "LeftAlign", {}), "Tag": ("75 Bold", 12, 14, "Navy", "LeftAlign", {}),
    "Page Title": ("45 Light", 36, 40, "Navy", "LeftAlign", {}), "Page Title White": ("45 Light", 36, 40, "Paper", "LeftAlign", {}),
    "Body": ("55 Roman", 9.5, 13.8, "Text", "LeftAlign", {"SpaceAfter": 10}),
    "Stat Value": ("75 Bold", 17, 20, "Paper", "CenterAlign", {}), "Stat Label": ("55 Roman", 11, 14, "Gold", "CenterAlign", {}),
    "Table Header": ("75 Bold", 11, 13, "Paper", "CenterAlign", {}), "Table Label": ("75 Bold", 9, 11.5, "Text", "LeftAlign", {}),
    "Table Value": ("55 Roman", 9, 11.5, "Text", "LeftAlign", {}), "Table Cell": ("55 Roman", 9, 11.5, "Text", "CenterAlign", {}),
    "Comp Head": ("75 Bold", 8, 10, "Paper", "CenterAlign", {}), "Comp Address": ("75 Bold", 8.5, 10.5, "Paper", "CenterAlign", {}),
    "Comp Label": ("55 Roman", 8, 10, "Text", "LeftAlign", {}), "Comp Cell": ("55 Roman", 8, 10, "Text", "CenterAlign", {}),
    "Value Head": ("75 Bold", 14, 17, "Paper", "CenterAlign", {}), "Value Label": ("55 Roman", 15, 18, "Text", "LeftAlign", {}),
    "Value Cell": ("55 Roman", 15, 18, "Text", "CenterAlign", {}), "Disclaimer": ("45 Light", 10.5, 17, "Disclaimer Gray", "LeftAlign", {}),
    "Source Note": ("45 Light", 8, 11, "Disclaimer Gray", "LeftAlign", {}),
    "Callout Title": ("75 Bold", 9, 11, "Paper", "LeftAlign", {}), "Callout Text": ("55 Roman", 7.5, 9.5, "Paper", "LeftAlign", {}),
    "Map Key Title": ("75 Bold", 11, 14, "Navy", "LeftAlign", {"SpaceAfter": 6}), "Map Key Item": ("55 Roman", 8.5, 15, "Text", "LeftAlign", {"Tab": 14}),
    "Back Headline": ("75 Bold", 40, 44, "Paper", "LeftAlign", {}), "Back Head": ("75 Bold", 11, 14, "Gold", "LeftAlign", {}),
    "Back Body": ("55 Roman", 8.5, 13, "Paper", "LeftAlign", {}), "Back Name": ("75 Bold", 9, 13, "Paper", "LeftAlign", {}),
    "Back Contact": ("55 Roman", 9, 13, "Paper", "LeftAlign", {}), "Placeholder Note": ("75 Bold", 10, 13, "Navy", "CenterAlign", {}),
    "North": ("75 Bold", 16, 18, "Paper", "CenterAlign", {}),
    "Traffic Count": ("75 Bold", 9.5, 11, "Navy", "CenterAlign", {}), "Road Label": ("75 Bold", 8.5, 10, "Paper", "CenterAlign", {}),
}
B = {"FontStyle": "75 Bold"}
LS = "\u2028"
EMPTY = [("", {})]
ABOUT = ("For more than 25 years, Cresa has served as an objective, stable business partner to commercial tenants. We join our clients\u2019 teams, "
         "working to align their business plans and their real estate needs, increase their productivity, and consistently save them money, results "
         "that have earned us numerous industry awards along the way. Our team of real estate advisors, project managers, strategic planners, analysts, "
         "and space planners listen to occupiers\u2019 needs, meticulously research market conditions, firmly negotiate terms, and manage the design and "
         "construction of projects to customize the best possible occupancy solutions.")
DISCLAIMER = ("The purpose of this report is to help determine a fair market value of the fee simple estate. This opinion is based upon our knowledge "
              "of the marketplace as real estate brokers and should not be relied upon as a real estate appraisal prepared by professional appraisers.")

D = json.load(open(os.environ["PROPERTY"]))
G = json.load(open(os.environ["GEOM"])) if os.environ.get("GEOM") and os.path.exists(os.environ["GEOM"]) else {}


def ls(s): return (s or "").replace("\n", LS)
def rect(x, y, w, h, fill="Navy", opacity=100, layer="Content", name=None, rot=0):
    return dict(t="rect", x=x, y=y, w=w, h=h, fill=fill, stroke=None, sw=0, opacity=opacity, layer=layer, name=name, rot=rot)
def poly(pts, fill="Paper", layer="Content"): return dict(t="poly", pts=pts, fill=fill, layer=layer)
def line(x1, y1, x2, y2, color="Rule", sw=0.75, layer="Content"): return dict(t="line", p=(x1, y1, x2, y2), color=color, sw=sw, layer=layer)
def image(x, y, w, h, file, layer="Images", name=None): return dict(t="image", x=x, y=y, w=w, h=h, file=file, layer=layer, name=name)
def text(x, y, w, h, paras, valign="TopAlign", inset=(0, 0, 0, 0), cols=1, gutter=18, fill=None, layer="Content", name=None, rot=0):
    return dict(t="text", x=x, y=y, w=w, h=h, paras=paras, valign=valign, inset=inset, cols=cols, gutter=gutter, fill=fill, layer=layer, name=name, rot=rot)
def table(x, y, colw, rows, layer="Content", name=None): return dict(t="table", x=x, y=y, colw=colw, rows=rows, layer=layer, name=name)
def P(style, *runs): return (style, [(ls(r), {}) if isinstance(r, str) else (ls(r[0]), r[1]) for r in runs])
def cellp(style, v): return [P(style, v)] if v not in (None, "") else [(style, EMPTY)]
def money(v): return "${:,.0f}".format(v)


def placeholder(x, y, w, h, note, opacity=100, note_box=True):
    items = [dict(t="placeholder", x=x, y=y, w=w, h=h, opacity=opacity, layer="Images", name="PLACEHOLDER: " + note)]
    if note_box:
        bw = min(300, w - 20)
        items.append(text(x + (w - bw) / 2, y + h / 2 - 22, bw, 44, [P("Placeholder Note", note)], valign="CenterAlign",
                          inset=(6, 8, 6, 8), fill="Paper", layer="Notes", name="Placeholder note"))
    return items


def tag():
    return [rect(0, 36.6, 176.6, 25.7, fill="Gold", name="Tag"), text(44, 36.6, 132, 25.7, [P("Tag", "Broker Price Opinion")], valign="CenterAlign", name="Tag text")]


def header(title):
    return tag() + [text(42.4, 64, 420, 46, [P("Page Title", title)], name="Page title"), image(RIGHT - 134, 39, 134, 134 / LOGO_AR, LOGO, layer="Content", name="Cresa logo")]


import bpo_spec_sort
COMPS = bpo_spec_sort.sort(D.get("comps") or [])
SF_TXT = "{:,}".format(D["building_sf"]) if D.get("building_sf") else "TBD"
AC_TXT = "{:.2f}".format(D["land_ac"]) if D.get("land_ac") else "TBD"


def photo_note(key, right, bottom):
    """Small caption in the photo's bottom-right corner, e.g. to label a rendering."""
    spec = D.get(key)
    note = spec.get("note") if isinstance(spec, dict) else None
    if not note: return []
    w = min(330, 22 + 3.9 * len(note)); h = 16
    return [rect(right - w - 8, bottom - h - 8, w, h, opacity=85, name="Photo note box"),
            text(right - w - 8, bottom - h - 8, w, h, [P("Callout Text", note)], valign="CenterAlign", inset=(2, 6, 2, 6), name="Photo note")]


def text_width(t, size):
    """Width in points of t at size, measured with Arial metrics (wider than Helvetica Neue Light, so it errs safe)."""
    from PIL import ImageFont
    f = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 1000)
    return f.getlength(t) * size / 1000


def p_cover():
    it = placeholder(335, 65, 457, 392, "faded backdrop", opacity=40, note_box=False) + placeholder(0, 385, 457, 227, "faded backdrop", opacity=40, note_box=False)
    if D.get("cover_photo_file"):
        it.append(image(36.6, 102, 718.8, 473.5, D["cover_photo_file"], name="Cover photo")); it += photo_note("cover_photo", 36.6 + 718.8, 102 + 473.5)
    else: it += placeholder(36.6, 102, 718.8, 473.5, "PLACE PHOTO: Cover image of property")
    it.append(image(36, 36, 114.5, 114.5 / LOGO_AR, LOGO, layer="Content", name="Cresa logo"))
    size = D.get("cover_point_size", 30 if len(D["address"]) <= 16 else 26)
    bw = max(307, round(36 + text_width(D["address"], size) + 30))  # widen the box so the street address stays on one line
    it += [rect(0, 140, bw, 106.6, opacity=92, name="Cover title box"), rect(0, 246.6, bw, 43.1, name="Cover label bar")]
    it.append(text(36, 152, bw - 45, 90, [P("Cover Address", (D["address"], {"PointSize": str(size)})), P("Cover City", D["city_line"])], valign="CenterAlign", name="Cover address"))
    it.append(text(36, 246.6, bw - 45, 43.1, [P("Cover Label", "Broker Price Opinion")], valign="CenterAlign"))
    for cx in (bw - 26, bw - 10, bw + 6):
        for cy in (128, 144): it.append(rect(cx, cy, 2.2, 2.2, fill="Gold", name="dot"))
    for i, cx in enumerate(range(682, 763, 16)):
        for j, cy in enumerate(range(486, 583, 16)):
            if not (i == 0 and j in (0, 6)): it.append(rect(cx, cy, 2.2, 2.2, fill="Gold", name="dot"))
    return it


def p_intro():
    if D.get("intro_photo_file"): it = [image(0, 0, W, 327, D["intro_photo_file"], name="Intro photo")] + photo_note("intro_photo", W, 327) + tag()
    else: it = placeholder(0, 0, W, 327, D.get("intro_photo_note", "PLACE PHOTO: Street-level view of property")) + tag()
    it.append(rect(0, 307, 207.5, 305, name="Stat panel"))
    labels = D.get("stat_labels", {})
    stats = ((D.get("property_type", "Industrial"), "Property Type"), (SF_TXT + " SF", labels.get("sf", "Total Building Area")), (AC_TXT + " AC", labels.get("ac", "Total Land Area")))
    for (v, l), y in zip(stats, (338, 427, 516)):
        it += [text(24, y, 160, 26, [P("Stat Value", v)], valign="CenterAlign"), line(34, y + 34, 174, y + 34, color="Rule Light"),
               text(24, y + 38, 160, 18, [P("Stat Label", l)], valign="CenterAlign"), line(34, y + 60, 174, y + 60, color="Rule Light")]
    it.append(text(238, 345, 517, 240, [P("Body", p) for p in D["intro"]], cols=2, gutter=20, name="Intro body"))
    return it


def p_summary():
    it = header("Property Summary")
    data = D["summary_rows"]
    rows = [dict(h=28, cells=[dict(paras=[P("Table Header", "Property Information")], fill="Navy", span=2)])]
    for k, v in data:
        rows.append(dict(h=416 / len(data), cells=[dict(paras=[P("Table Label", k)], inset=(3, 14, 3, 6), bottom=("Rule", 0.75)),
                                                   dict(paras=cellp("Table Value", v), inset=(3, 6, 3, 8), bottom=("Rule", 0.75))]))
    it += [table(42.4, 129, [140, 240.2], rows, name="Property table"), line(442, 110, 442, 578),
           image(460.5, 110, 294.2, 468, "map_site_parcels.png", name="Parcel map")]
    return it


def p_location():
    it = header("Location")
    it += [image(42.4, 127, 183.6, 153.7, "map_inset.png", name="Regional inset map"),
           text(42.4, 300, 183.6, 276, [P("Body", p) for p in D["location_text"]], name="Location body"),
           image(250.5, 112.4, 500.5, 463.1, "map_location.png", name="Location map")]
    return it


DEMO_DEFAULT = ["Population (2025)", "Projected Population (2030)", "Annual Growth (2025-2030)", "Households (2025)", "Median Age",
                "Median Household Income", "Average Household Income", "Daytime Employees", "Total Businesses", "Goods-Producing Employees", "Manufacturing Employees"]


def p_demo():
    dm = D.get("demographics") or {}
    rows_in = dm.get("rows") or [[l, "", "", ""] for l in DEMO_DEFAULT]
    it = header("Demographics")
    it.append(image(42.4, 112, 358, 466, "map_demographics_rings.png", name="Demographic rings map"))
    rows = [dict(h=32, cells=[dict(paras=[("Table Header", EMPTY)], fill="Navy")] + [dict(paras=[P("Table Header", r)], fill="Navy") for r in ("1 Mile", "3 Miles", "5 Miles")])]
    rh = min(30, 330 / len(rows_in))
    for lab, *vals in rows_in:
        rows.append(dict(h=rh, cells=[dict(paras=[P("Table Label", lab)], inset=(2, 10, 2, 4), bottom=("Rule", 0.75))] +
                                     [dict(paras=cellp("Table Cell", v), bottom=("Rule", 0.75)) for v in (vals + ["", "", ""])[:3]]))
    it.append(table(420, 112, [150, 60, 60, 60], rows, name="Demographics table"))
    ty = 112 + 32 + rh * len(rows_in) + 8
    it.append(text(420, ty, 330, 562 - ty, [P("Body", dm.get("summary") or "[Demographic summary to come.]")], name="Demographics body"))
    it.append(text(420, 564, 330, 14, [P("Source Note", dm.get("source", "Source: CoStar; 2025 estimates and 2030 projections."))], name="Demographics source"))
    return it


def callout(x, y, title, lines, w=158):
    h = 22 + 9.5 * len(lines)
    return [rect(x, y, w, h, name="Callout"), rect(x, y, 6, h, fill="Gold", name="Callout bar"),
            text(x + 6, y, w - 6, h, [P("Callout Title", title)] + [P("Callout Text", l) for l in lines], valign="CenterAlign", inset=(4, 9, 4, 6), name="Callout text")], h


def p_aerial():
    it = [image(0, 0, W, H, "aerial_overhead.png", name="Overhead aerial")] + tag()
    it.append(text(42.4, 64, 420, 46, [P("Page Title White", "Overhead Aerial")], name="Page title"))
    cents = G.get("centroids", [])
    callouts = D.get("aerial_callouts") or [{"title": D["address"], "lines": [f"\u00b1{SF_TXT} SF", f"\u00b1{AC_TXT} AC"], "parcel": "all"}]
    minx, maxx = G.get("minx", 300), G.get("maxx", 500)
    for i, co in enumerate(callouts):
        p = co.get("parcel", "all")
        ax, ay = G.get("center", (W / 2, H / 2)) if p == "all" or not cents else cents[int(p)]
        side = co.get("side") or ("left" if minx > 230 else "right")
        w = co.get("width", 158)
        parts, h = callout(0, 0, ls(co["title"]), [ls(l) for l in co.get("lines", [])], w)
        x = 60 if side == "left" else min(W - w - 30, maxx + 50)
        y = max(120, min(H - h - 40, ay - h / 2))
        for q in parts:
            q["x"] += x; q["y"] += y
        it.append(line(x + w if side == "left" else x, y + h / 2, ax, ay, color="Gold", sw=1))
        it += parts
    it += traffic_badges()
    it += [poly([(32, 562), (38, 554), (44, 562)]), text(24, 562, 28, 22, [P("North", "N")])]
    return it


def traffic_badges():
    """Road-name labels and traffic-count boxes on the aerial, each centered on its road and rotated to the road's angle.
    Positions and angles come from build.py (geom.json 'labels'), which snaps each item's points to the road."""
    out = []
    for lb in G.get("labels", []):
        cx, cy, ang = lb["x"], lb["y"], lb["angle"]
        if lb["kind"] == "traffic":
            txt = f"{lb['vpd']:,} VPD"; w, h = 14 + 5.6 * len(txt), 17
            out += [rect(cx - w / 2, cy - h / 2, w, h, fill="Gold", rot=ang, name="Traffic count"),
                    text(cx - w / 2, cy - h / 2, w, h, [P("Traffic Count", txt)], valign="CenterAlign", rot=ang, name="Traffic count text")]
        else:
            txt = lb["name"]; w, h = 12 + 4.7 * len(txt), 15
            out += [rect(cx - w / 2, cy - h / 2, w, h, fill="Navy", opacity=80, rot=ang, name="Road label"),
                    text(cx - w / 2, cy - h / 2, w, h, [P("Road Label", txt)], valign="CenterAlign", rot=ang, name="Road label text")]
    if any(lb["kind"] == "traffic" for lb in G.get("labels", [])):
        src = D.get("traffic_source", "Traffic counts: CoStar 2026, vehicles per day (VPD)"); sw = max(214, text_width(src, 7.5) + 14)
        out += [rect(W - 18 - sw, H - 28, sw, 14, opacity=80, name="Traffic source box"),
                text(W - 18 - sw, H - 28, sw, 14, [P("Callout Text", src)], valign="CenterAlign", inset=(1, 6, 1, 6), name="Traffic source")]
    return out

def p_buildings():
    bd = D["buildings"]
    it = header(bd.get("title", "Building Summary"))
    heads = bd["heads"]; n = len(heads)
    colw = bd.get("colw") or [708.6 / n] * n
    rows = [dict(h=32, cells=[dict(paras=[P("Comp Head", h_)], fill="Navy", inset=(2, 3, 2, 3)) for h_ in heads])]
    rh = min(48, 250 / max(1, len(bd["rows"])))
    for r in bd["rows"]:
        rows.append(dict(h=rh, cells=[dict(paras=cellp("Comp Cell", v), bottom=("Rule", 0.75), inset=(2, 3, 2, 3)) for v in r]))
    if bd.get("total"):
        rows.append(dict(h=28, cells=[dict(paras=cellp("Comp Cell", (v, B) if v else ""), fill="Cell Gray") for v in bd["total"]]))
    it.append(table(42.4, 122, colw, rows, name="Building table"))
    if bd.get("site"):
        site = [dict(h=24, cells=[dict(paras=[P("Table Header", "Site Improvements")], fill="Navy", span=4)])]
        for l1, v1, l2, v2 in bd["site"]:
            site.append(dict(h=29, cells=[dict(paras=[P("Table Label", l1)], inset=(2, 10, 2, 4), bottom=("Rule", 0.75)), dict(paras=cellp("Table Value", v1), bottom=("Rule", 0.75)),
                                         dict(paras=[P("Table Label", l2)], inset=(2, 10, 2, 4), bottom=("Rule", 0.75)), dict(paras=cellp("Table Value", v2), bottom=("Rule", 0.75))]))
        it.append(table(42.4, 566 - 24 - 29 * len(bd["site"]), [120, 234.3, 120, 234.3], site, name="Site improvements table"))
    if bd.get("note"):
        it.append(text(42.4, 572, 708.6, 14, [P("Source Note", bd["note"])]))
    return it


def p_compmap():
    it = header(D.get("comps_title", "Recent Sales Comps"))
    it.append(image(0, 131.7, W, 480.3, "map_comps.png", name="Comps map"))
    items = [c["addr"] for c in COMPS] or ["[Comp address]"] * 5
    h = 32 + 15 * len(items) + 12
    y = 580 - h
    it += [rect(27, y, 168, h, fill="Paper", name="Map key box"), line(39, y + 24, 183, y + 24, color="Gold", sw=1),
           text(27, y, 168, h, [P("Map Key Title", "Map Key")] + [P("Map Key Item", (f"{i+1}\t", B), a) for i, a in enumerate(items)], inset=(9, 12, 6, 8), name="Map key")]
    return it


COMP_FIELDS = D.get("comp_fields") or [["City", "city"], ["Close Date", "date"], ["Building Area SF", "sf"], ["Sale Price", "price"], ["Price/SF", "psf"],
                                       ["Cap Rate", "cap"], ["Sale Type", "type"], ["Clear Height", "clear"], ["Buyer", "buyer"], ["Seller", "seller"],
                                       ["Buyer Broker", "bb"], ["Seller Broker", "sb"]]


def comp_layout(n):
    c0 = 92.5; return 42.4, c0, (708.6 - c0) / n


def p_comptable(chunk, start):
    it = header(D.get("comps_title", "Recent Sales Comps"))
    n = len(chunk) if chunk else 5
    x0, c0, cw = comp_layout(n)
    for i in range(n):
        c = chunk[i] if chunk else {}
        if c.get("photo"):
            it.append(image(x0 + c0 + i * cw + 2, 123, cw - 4, 80, c["photo"], name=f"Comp {start+i} photo"))
        else:
            it += placeholder(x0 + c0 + i * cw + 2, 123, cw - 4, 80, f"PHOTO {start+i}", note_box=False)
            it.append(text(x0 + c0 + i * cw + 2, 153, cw - 4, 20, [P("Placeholder Note", f"Comp {start+i} photo")], layer="Notes", valign="CenterAlign"))
    rows = [dict(h=16, cells=[dict(paras=[P("Comp Head", "Comp")], fill="Navy", inset=(2, 8, 2, 4))] + [dict(paras=[P("Comp Head", str(start + i))], fill="Navy") for i in range(n)]),
            dict(h=32.7, cells=[dict(paras=[P("Comp Address", ("Address", {"Justification": "LeftAlign"}))], fill="Blue", inset=(2, 8, 2, 4))] +
                               [dict(paras=[P("Comp Address", (chunk[i]["addr"] if chunk else "[Address]"))], fill="Blue") for i in range(n)])]
    for lab, key in COMP_FIELDS:
        rows.append(dict(h=322.3 / len(COMP_FIELDS), cells=[dict(paras=[P("Comp Label", lab)], inset=(2, 8, 2, 4), bottom=("Rule", 0.75))] +
                                                           [dict(paras=cellp("Comp Cell", (chunk[i].get(key) or "N/A") if chunk else ""), bottom=("Rule", 0.75)) for i in range(n)]))
    it.append(table(x0, 205, [c0] + [cw] * n, rows, name="Comps table"))
    return it


def p_value():
    it = header("Market Value")
    pr = D.get("pricing") or {}
    LEASE = pr.get("mode") == "lease"
    sf = pr.get("sf_basis") or D.get("building_sf")
    paras = pr.get("narrative") or [pr.get("placeholder", "[Market commentary and pricing rationale to come once comparable sales are finalized.]")]
    it.append(text(45, 116, 705, 140, [P("Body", p) for p in paras], cols=2, gutter=27, name="Market value body"))
    def row(label, v):
        if LEASE:
            vals = (f"${v:,.2f}", f"{sf:,}", money(round(v * sf))) if v and sf else ("$TBD", f"{sf:,}" if sf else "TBD", "$TBD")
        else:
            vals = (f"${v/sf:,.2f}", f"{sf:,}", money(v)) if v and sf else ("$TBD", f"{sf:,}" if sf else "TBD", "$TBD")
        return dict(h=80, cells=[dict(paras=[P("Value Label", label)], fill="Cell Gray", inset=(4, 22, 4, 8), bottom=("Rule", 0.75))] +
                                [dict(paras=[P("Value Cell", x)], bottom=("Rule", 0.75)) for x in vals])
    hdr = dict(h=46, cells=[dict(paras=[("Value Head", EMPTY)], fill="Navy")] + [dict(paras=[P("Value Head", s_)], fill="Navy") for s_ in (("Rent/SF/Yr", "SF", "Annual Rent") if LEASE else ("Price/SF", "SF", "Total Value"))])
    it.append(table(45, 266, [188, 172.3, 172.3, 172.4], [hdr, row(pr.get("ask_label", "Suggested Asking"), pr.get("ask")), row(pr.get("trade_label", "Expected Trade"), pr.get("trade"))], name="Value table"))
    it.append(text(45, 530, 705, 44, [P("Disclaimer", D.get("disclaimer", DISCLAIMER))], name="Disclaimer"))
    return it


def p_back():
    it = [rect(0, 0, W, H, fill="Navy Dark", name="Background"), text(42, 176, 500, 52, [P("Back Headline", "Beyond Space")]),
          text(42, 421, 336, 18, [P("Back Head", "About Cresa")]), text(42, 450, 336, 120, [P("Back Body", ABOUT)]),
          text(477, 421, 250, 18, [P("Back Head", "Cresa")])]
    brokers = D.get("brokers") or [{"name": "[Broker Name]", "phone": "[Phone]", "email": "[Email]"}] * 2
    for i, b in enumerate(brokers[:4]):
        x, y = (477, 614)[i % 2], 450 + 68 * (i // 2)
        it.append(text(x, y, 140, 66, [P("Back Name", b["name"])] + ([P("Back Contact", b["title"])] if b.get("title") else []) + [P("Back Contact", b.get("phone", "")), P("Back Contact", b.get("email", ""))], name="Broker contact"))
    return it


def p_lease_summary():
    ls_ = D["lease"]
    it = header("Lease Summary")
    it.append(text(42.4, 109, 300, 12, [P("Source Note", "As of " + ls_.get("as_of", "TBD"))], name="As of"))
    rows = [dict(h=26, cells=[dict(paras=[P("Table Header", ls_.get("table_title", "Current Lease"))], fill="Navy", span=2)])]
    srows = ls_["summary_rows"]; extra = sum(str(v).count("\n") for _, v in srows)
    rh = min(24, (400 - 11.5 * extra) / len(srows))
    for k, v in srows:
        bold = k.isupper()
        rows.append(dict(h=rh + 11.5 * str(v).count("\n"), cells=[dict(paras=[P("Table Label", k)], inset=(2, 10, 2, 6), bottom=("Rule", 0.75), fill="Cell Gray" if bold else None),
                                      dict(paras=cellp("Table Cell", (v, B) if bold else v), bottom=("Rule", 0.75), fill="Cell Gray" if bold else None)]))
    it.append(table(42.4, 128, [230, 150], rows, name="Lease summary table"))
    paras = [P("Map Key Title", "Lease Notes")] + [P("Body", "\u2022  " + n) for n in ls_.get("notes", [])]
    paras += [P("Map Key Title", "Lease Opinion of Value"), P("Body", ls_.get("opinion", "[Lease opinion to come once lease comparables are finalized.]"))]
    if D.get("skip_value"):  # Market Value page dropped: the opinion lives here, so carry the disclaimer too
        it.append(text(452, 128, 298, 380, paras, name="Lease notes"))
        it.append(text(42.4, 536, 708.6, 40, [P("Source Note", D.get("disclaimer", DISCLAIMER))], name="Disclaimer"))
    else:
        it.append(text(452, 128, 298, 446, paras, name="Lease notes"))
    return it


def p_proforma():
    ls_ = D["lease"]
    it = header("Cash Flow Pro Forma")
    it.append(text(42.4, 109, 300, 12, [P("Source Note", "As of " + ls_.get("as_of", "TBD"))], name="As of"))
    heads = ["Period", "From", "To", "Months", "Base Rent\n/ RSF", "Base Rent", "Additional\nExpenses", "Total Cash\nCost", "Avg Monthly\nCost", "Annual Cost\n/ RSF"]
    colw = [40, 70, 70, 50, 75, 85, 85, 85, 75, 73.6]
    rows = [dict(h=30, cells=[dict(paras=[P("Comp Head", h_)], fill="Navy", inset=(2, 3, 2, 3)) for h_ in heads])]
    pf = ls_.get("pf_rows") or [[str(i)] + ["TBD"] * 9 for i in range(1, 6)]
    rh = min(48, (400 - 30 - 28) / len(pf))  # fill the page down to the footnote; long schedules shrink to fit
    for i, r in enumerate(pf):
        rows.append(dict(h=rh, cells=[dict(paras=cellp("Comp Cell", v), bottom=("Rule", 0.75), fill="Cell Gray" if i % 2 else None, inset=(2, 3, 2, 3)) for v in r]))
    tot = ls_.get("pf_total") or ["Total", "", "", "TBD", "", "TBD", "TBD", "TBD", "", ""]
    rows.append(dict(h=28, cells=[dict(paras=cellp("Comp Cell", (v, B) if v else ""), fill="Cell Gray", inset=(2, 3, 2, 3)) for v in tot]))
    it.append(table(42.4, 128, colw, rows, name="Pro forma table"))
    ny = min(540, 128 + sum(r["h"] for r in rows) + 14)
    it.append(text(42.4, ny, 708.6, 34, [P("Source Note", ls_.get("pf_note", ""))], name="Pro forma note"))
    return it


def build_pages():
    pages = [p_cover(), p_intro(), p_summary(), p_location(), p_demo()]
    if not D.get("skip_aerial"): pages.append(p_aerial())
    if D.get("buildings"): pages.append(p_buildings())
    pages.append(p_compmap())
    chunks = [COMPS[i:i + 5] for i in range(0, len(COMPS), 5)] or [[]]
    for k, ch in enumerate(chunks): pages.append(p_comptable(ch, 1 + 5 * k))
    if D.get("lease"): pages += [p_lease_summary(), p_proforma()]
    if not D.get("skip_value"): pages.append(p_value())
    pages.append(p_back())
    return pages


PAGES = build_pages()
