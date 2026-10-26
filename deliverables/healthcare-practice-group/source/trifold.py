"""Cresa Healthcare 'Road Atlas' trifold self-mailer, legal size (14 x 8.5 in), letter fold."""
import json
import math
import os

from idmlkit import (CStyle, Doc, Image, Line, Oval, Path, Placeholder, PStyle, Rect, Rotated, Text)
from layouts import (B, CONTACTS, SERVICE_LINES, add_styles, client_logo, eyebrow_with_dash, icon, logo)

HERE = os.path.dirname(os.path.abspath(__file__))
MAP = json.load(open(os.path.join(HERE, "assets", "us_map.json")))

W, H = 1008, 612                       # legal, landscape
FLAP, PANEL = 333, 337.5               # fold-in panel is 1/16" narrower
# outside (page 0): flap | mailer back | cover
OX_FLAP, OX_BACK, OX_COVER = 0, FLAP, FLAP + PANEL
# inside (page 1): left | middle | right (back of the flap)
IX_L, IX_M, IX_R = 0, PANEL, 2 * PANEL
PM = 22                                # panel margin
COMPANY = "[Company Name]"

STATE_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
    "Connecticut": "", "Delaware": "", "District of Columbia": "", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY",
    "Louisiana": "LA", "Maine": "ME", "Maryland": "", "Massachusetts": "", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "",
    "New Jersey": "", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND",
    "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}
LABEL_AT = {"Michigan": "MI label", "Louisiana": "LA label", "Florida": "FL label"}

INTERSTATES = [
    ("5", ["San Diego", "Los Angeles", "Bakersfield", "Sacramento", "Medford", "Portland", "Seattle"], 3),
    ("10", ["Los Angeles", "Phoenix", "Tucson", "El Paso", "San Antonio", "Houston", "New Orleans", "Mobile",
            "Tallahassee", "Jacksonville"], 3),
    ("40", ["Barstow", "Flagstaff", "Albuquerque", "Amarillo", "Oklahoma City", "Little Rock", "Memphis",
            "Nashville", "Knoxville", "Raleigh", "Wilmington"], 3),
    ("80", ["San Francisco", "Sacramento", "Reno", "Salt Lake City", "Cheyenne", "Omaha", "Des Moines", "Chicago",
            "Toledo", "Cleveland", "New York"], 4),
    ("90", ["Seattle", "Spokane", "Missoula", "Billings", "Rapid City", "Sioux Falls", "Madison", "Chicago",
            "Toledo", "Cleveland", "Buffalo", "Syracuse", "Albany", "Boston"], 3),
    ("35", ["Laredo", "San Antonio", "Austin", "Dallas", "Oklahoma City", "Wichita", "Kansas City", "Des Moines",
            "Minneapolis", "Duluth"], 5),
    ("70", ["Denver", "Kansas City", "St. Louis", "Indianapolis", "Columbus", "Pittsburgh", "Baltimore"], 1),
    ("95", ["Miami", "Jacksonville", "Savannah", "Raleigh-Durham", "Richmond", "Washington", "Baltimore",
            "Philadelphia", "New York", "Hartford", "Boston", "Portland ME"], 2),
    ("75", ["Tampa", "Atlanta", "Chattanooga", "Knoxville", "Lexington", "Cincinnati", "Toledo", "Detroit"], 2),
    ("25", ["El Paso", "Albuquerque", "Denver", "Cheyenne"], 1),
]
CITY_LABELS = ["Seattle", "San Francisco", "Los Angeles", "Phoenix", "Denver", "Dallas", "Houston", "Minneapolis",
               "Chicago", "St. Louis", "Atlanta", "Miami", "New York", "Boston", "Washington"]
# Sample footprint so the layout reads; replace per prospect.
SAMPLE_EXISTING = ["Houston", "Dallas", "Austin", "San Antonio", "Oklahoma City", "Tulsa", "Shreveport", "Denver",
                   "Phoenix", "Atlanta", "Nashville", "Tampa", "Orlando", "Charlotte"]
SAMPLE_TARGET = ["Raleigh", "Columbia SC", "Jacksonville", "Birmingham", "Kansas City"]
SAMPLE_GROWTH = ["Las Vegas", "Salt Lake City", "Boise"]
TAGS = [("Next location", "Raleigh", "Warm Orange", "Paper", (28, -30)),
        ("Expansion", "Atlanta", "Stadium Blue", "Paper", (-70, 26)),
        ("Relocation", "Dallas", "Midnight", "Paper", (-84, 12)),
        ("Future market", "Salt Lake City", "Goldenrod", "Midnight", (-30, -42))]
STATE_FILLS = [("Goldenrod", 30), ("Warm Orange", 18), ("Atlas Cream", 100), ("Goldenrod", 12)]


# ------------------------------------------------------------------ helpers
def simplify(pts, tol):
    """Douglas-Peucker."""
    if len(pts) < 4:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1e-9
        best, bi = -1, -1
        for i in range(a + 1, b):
            d = abs(dy * pts[i][0] - dx * pts[i][1] + x2 * y1 - y2 * x1) / L
            if d > best:
                best, bi = d, i
        if best > tol:
            keep[bi] = True
            stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]


def color_states(states):
    order = sorted(range(len(states)), key=lambda i: -len(states[i]["neighbors"]))
    col = {}
    for i in order:
        used = {col[n] for n in states[i]["neighbors"] if n in col}
        col[i] = next(c for c in range(4) if c not in used)
    return col


def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def shield_outline(x, y, w, h, n=14):
    """Interstate-style shield as a polygon (unit shape mapped to box)."""
    top = [(i / n, 0.05 + 0.07 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    right = [(1.0, 0.05), (1.0, 0.42)] + [bezier((1, .42), (1, .78), (.82, .93), (.5, 1.0), i / n)
                                         for i in range(1, n + 1)]
    left = [bezier((.5, 1.0), (.18, .93), (0, .78), (0, .42), i / n) for i in range(1, n + 1)] + [(0, 0.05)]
    unit = top + right[1:] + left
    return [(x + px * w, y + py * h) for px, py in unit], unit


def shield(x, y, w, h, top_text, lines, num_style=None, name="shield", border=2.0, inset=None):
    """Full badge: white rim, gold top band, navy body. Returns items."""
    inset = inset if inset is not None else max(2.5, w * 0.035)
    outer, _ = shield_outline(x, y, w, h)
    ix, iy, iw, ih = x + inset, y + inset, w - 2 * inset, h - 2 * inset
    inner, unit = shield_outline(ix, iy, iw, ih)
    yb = 0.27
    n = 14
    band = [(ix + px * iw, iy + py * ih) for px, py in unit[:n + 1]] + [(ix + iw, iy + yb * ih), (ix, iy + yb * ih)]
    body = [(ix, iy + yb * ih), (ix + iw, iy + yb * ih)] + [
        (ix + px * iw, iy + py * ih) for px, py in unit if py > yb]
    items = [Path(outer, True, "Paper", "Midnight", border, name=name + " rim"),
             Path(band, True, "Goldenrod", None, 0, name=name + " band"),
             Path(body, True, "Midnight", None, 0, name=name + " body")]
    if top_text:
        items.append(Text(ix, iy + ih * 0.075, iw, ih * 0.2, [top_text], valign="center"))
    if lines:
        items.append(Text(ix + iw * 0.08, iy + ih * 0.3, iw * 0.84, ih * 0.52, lines, valign="center"))
    return items


def mini_shield(cx, cy, num, size=13):
    w, h = size, size * 1.05
    x, y = cx - w / 2, cy - h / 2
    outer, unit = shield_outline(x, y, w, h, n=8)
    band = [(x + px * w, y + py * h) for px, py in unit[:9]] + [(x + w, y + .3 * h), (x, y + .3 * h)]
    return [Path(outer, True, "Midnight", "Paper", 0.6, name=f"I-{num} shield"),
            Path(band, True, "Warm Orange", None, 0, name=f"I-{num} shield band"),
            Text(x, y + h * 0.3, w, h * 0.5, [("Shield Num", num)], valign="center")]


def pin(cx, cy, fill, r=3.4, name="pin"):
    return [Oval(cx - r - 1, cy - r - 1, 2 * r + 2, 2 * r + 2, fill="Paper", name=name + " halo"),
            Oval(cx - r, cy - r, 2 * r, 2 * r, fill=fill, name=name)]


def add_trifold_styles(d):
    add_styles(d)
    P, C = d.add_pstyle, d.add_cstyle
    P(PStyle("Atlas Kicker", "BoldCond", 8, 10, "Midnight", 220, caps=True))
    P(PStyle("Atlas Kicker Right", "BoldCond", 8, 10, "Midnight", 220, caps=True, align="right"))
    P(PStyle("Atlas Kicker Gold", "BoldCond", 8.5, 10, "Goldenrod", 220, caps=True))
    P(PStyle("Atlas Kicker Center", "BoldCond", 8.5, 11, "Midnight", 200, caps=True, align="center"))
    P(PStyle("Atlas Title", "BoldCond", 21, 22, "Midnight", 10, caps=True))
    P(PStyle("Atlas Title Reverse", "BoldCond", 24, 25, "Paper", 10, caps=True))
    P(PStyle("Atlas Band", "BoldCond", 15, 16, "Goldenrod", 160, caps=True))
    P(PStyle("Shield Top", "BoldCond", 12, 13, "Midnight", 180, caps=True, align="center"))
    P(PStyle("Shield Line", "BoldCond", 25, 25, "Paper", 10, caps=True, align="center"))
    P(PStyle("Shield Num", "BoldCond", 5.2, 5.5, "Paper", align="center"))
    P(PStyle("State Label", "MediumCond", 6, 6.5, "Dark Gray", 160, caps=True, align="center"))
    P(PStyle("City Label", "MediumCond", 5.6, 6.2, "Midnight", 20))
    P(PStyle("Tag", "BoldCond", 6.5, 7, "Paper", 100, caps=True, align="center"))
    P(PStyle("Tag Dark", "BoldCond", 6.5, 7, "Midnight", 100, caps=True, align="center"))
    P(PStyle("Legend", "Roman", 7, 9, "Dark Gray"))
    P(PStyle("Scale Label", "MediumCond", 5.5, 6, "Midnight", 60))
    P(PStyle("Compass N", "BoldCond", 8, 9, "Midnight", align="center"))
    P(PStyle("Return Address", "Roman", 7.5, 9.5, "Dark Gray"))
    P(PStyle("Indicia", "BoldCond", 6.5, 8, "Midnight", 60, caps=True, align="center"))
    P(PStyle("Mailer Teaser", "BoldCond", 19, 20, "Midnight", 10, caps=True))
    P(PStyle("Mini Name", "Bold", 8, 10, "Midnight"))
    P(PStyle("Mini Detail", "Roman", 7.5, 9.5, "Dark Gray"))
    P(PStyle("Body Small Reverse Plain", "Roman", 8.5, 12, "Paper", after=8))
    P(PStyle("H4 Gold", "Medium", 9.5, 12, "Goldenrod", after=2))
    P(PStyle("Flap Head", "Bold", 8, 10, "Goldenrod", 150, caps=True))
    P(PStyle("Headline Sync", "Light", 21, 24, "Midnight", -10))
    P(PStyle("Headline Sync Reverse", "Light", 26, 30, "Paper", -10))
    P(PStyle("Card Title", "Medium", 8.5, 10.5, "Midnight", after=3))
    P(PStyle("Card Text", "Roman", 7.5, 9.5, "Dark Gray"))
    P(PStyle("Flap Item", "Medium", 9, 11, "Paper", after=1))
    P(PStyle("Footer Gold", "BoldCond", 9, 10, "Goldenrod", 160, caps=True))
    C(CStyle("Gold Text", color="Goldenrod"))


# ------------------------------------------------------------------ map
def us_map(x0, y0, width):
    s = width / MAP["width"]
    h = MAP["height"] * s
    T = lambda p: (x0 + p[0] * s, y0 + p[1] * s)
    items = [Rect(x0, y0, width, h, fill="Bright Blue", tint=14, name="map water"),
             Rect(x0 - 4, y0 - 4, width + 8, h + 8, fill=None, stroke="Midnight", sw=1.2, name="map frame"),
             Rect(x0 - 1.5, y0 - 1.5, width + 3, h + 3, fill=None, stroke="Midnight", sw=0.4, name="map frame inner")]
    cols = color_states(MAP["states"])
    for i, st in enumerate(MAP["states"]):
        fill, tint = STATE_FILLS[cols[i]]
        for ring in st["rings"]:
            pts = simplify([tuple(p) for p in ring[:-1]], 0.7)
            if len(pts) < 3:
                continue
            items.append(Path([T(p) for p in pts], True, fill, "Dark Gray", 0.35, tint=tint, name=st["name"]))
    # interstates: white casing then colored line
    shields = []
    for num, route, k in INTERSTATES:
        pts = [T(MAP["cities"][c]) for c in route]
        items.append(Path(pts, False, None, "Paper", 2.6, name=f"I-{num} casing"))
        items.append(Path(pts, False, None, "Warm Orange", 1.2, name=f"I-{num}"))
        a, b = pts[k - 1], pts[k]
        shields += mini_shield((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, num)
    # state labels
    for st in MAP["states"]:
        ab = STATE_ABBR.get(st["name"], "")
        if not ab:
            continue
        c = MAP["cities"][LABEL_AT[st["name"]]] if st["name"] in LABEL_AT else st["centroid"]
        cx, cy = T(c)
        items.append(Text(cx - 12, cy - 3.5, 24, 8, [("State Label", ab)], name=f"label {ab}"))
    # cities
    for c in CITY_LABELS:
        cx, cy = T(MAP["cities"][c])
        items.append(Oval(cx - 1.3, cy - 1.3, 2.6, 2.6, fill="Midnight", name=f"city {c}"))
        items.append(Text(cx + 2.5, cy - 7.5, 60, 7, [("City Label", c)], name=f"label {c}"))
    items += shields
    # client footprint (sample)
    for c in SAMPLE_EXISTING:
        items += pin(*T(MAP["cities"][c]), "Midnight", name=f"existing {c}")
    for c in SAMPLE_TARGET:
        items += pin(*T(MAP["cities"][c]), "Bright Blue", name=f"target {c}")
    for c in SAMPLE_GROWTH:
        items += pin(*T(MAP["cities"][c]), "Warm Orange", name=f"growth {c}")
    for label, c, fill, txt, (dx, dy) in TAGS:
        cx, cy = T(MAP["cities"][c])
        tw, th = 56, 13
        tx, ty = cx + dx, cy + dy
        items += [Line(cx, cy, tx + tw / 2, ty + th / 2, stroke=fill, sw=0.8, name=f"tag leader {label}"),
                  Rect(tx, ty, tw, th, fill=fill, stroke="Paper", sw=0.8, name=f"tag {label}"),
                  Text(tx, ty + 3.2, tw, 8, [("Tag Dark" if txt == "Midnight" else "Tag", label)])]
        items += pin(cx, cy, fill, r=4.2, name=f"tag pin {label}")
    # compass rose (Atlantic)
    ccx, ccy = T((925, 395))
    r = 15
    items += [Oval(ccx - r, ccy - r, 2 * r, 2 * r, fill="Paper", stroke="Midnight", sw=0.6, name="compass ring"),
              Path([(ccx, ccy - r - 4), (ccx + 3.5, ccy), (ccx, ccy + r + 4), (ccx - 3.5, ccy)], True,
                   "Midnight", None, 0, name="compass NS"),
              Path([(ccx - r - 4, ccy), (ccx, ccy - 3), (ccx + r + 4, ccy), (ccx, ccy + 3)], True,
                   "Goldenrod", None, 0, name="compass EW"),
              Text(ccx - 6, ccy - r - 15, 12, 10, [("Compass N", "N")])]
    # scale bar: 1 projected unit ~ 3.04 miles at this projection
    sx0, sy0 = T((560, 590))
    seg = 250 / 3.04 * s / 2
    for i in range(4):
        items.append(Rect(sx0 + i * seg, sy0, seg, 3, fill="Midnight" if i % 2 == 0 else "Paper",
                          stroke="Midnight", sw=0.4, name="scale bar"))
    items += [Text(sx0 - 4, sy0 + 4.5, 20, 7, [("Scale Label", "0")]),
              Text(sx0 + 2 * seg - 8, sy0 + 4.5, 24, 7, [("Scale Label", "250")]),
              Text(sx0 + 4 * seg - 8, sy0 + 4.5, 50, 7, [("Scale Label", "500 MILES")])]
    return items, h


# ------------------------------------------------------------------ build
def build_trifold():
    d = Doc("Cresa_Healthcare_RoadAtlas_Trifold", W, H, 2, bleed=B, margin=PM)
    add_trifold_styles(d)
    OUT, IN = 0, 1

    # ================= OUTSIDE =================
    # --- flap: what we do / what you gain / service lines, navy
    d.add(OUT, Rect(-B, -B, FLAP + B, H + 2 * B, fill="Midnight", name="flap background"))
    x, w = OX_FLAP + PM, FLAP - 2 * PM
    d.add(OUT, Text(x, 30, w, 12, [("Flap Head", "Healthcare Practice Group")]),
          Text(x, 46, w, 64, [("Headline Sync Reverse", [(None, "Every mile,\n"), ("Emphasis Medium", "on your side.")])]),
          Rect(x, 112, 60, 3, fill="Goldenrod", name="flap accent"))
    # what we do
    d.add(OUT, Text(x, 130, w, 12, [("Flap Head", "What We Do")]),
          Text(x, 146, w, 28, [("Body Small Reverse Plain",
                                "We turn demand, competition and access data into defensible site decisions.")]))
    analytics = ["Market Demand Modeling", "Competitive Saturation", "Drive-Time & Access",
                 "Site Ranking & Selection", "Referral Network Mapping", "Payer Mix Analysis"]
    for k, col in enumerate((analytics[:3], analytics[3:])):
        d.add(OUT, Text(x + k * (w / 2), 174, w / 2 - 4, 50, [("Bullet Reverse Tight", t) for t in col]))
    # what you gain
    d.add(OUT, Line(x, 230, x + w, 230, stroke="Stadium Blue", sw=0.6, name="flap rule"),
          Text(x, 242, w, 12, [("Flap Head", "What You Gain")]))
    gains = [("Confidence in the decision", "Every recommendation traces back to a 100-point opportunity score you "
                                            "can defend to leadership and lenders."),
             ("Clinical strategy aligned to the market", "Sites chosen on service-line demand, payer mix and referral "
                                                         "patterns, not just rooftops and traffic counts."),
             ("Reduced risk, faster approvals", "Answers ready before your board asks, so decisions move from "
                                                "analysis to approval without rework."),
             ("A long-term strategic advisor", "Analytics that carry the relationship beyond one transaction into "
                                               "ongoing portfolio strategy.")]
    y = 262
    for t, desc in gains:
        d.add(OUT, Oval(x, y + 1, 13, 13, fill="Goldenrod", name="gain dot"),
              Path([(x + 3.2, y + 7.5), (x + 5.8, y + 10.1), (x + 10, y + 4.8)], False, None, "Midnight", 1.2,
                   name="gain check"),
              Text(x + 21, y, w - 21, 44, [("Flap Item", t), ("Body Small Reverse", desc)]))
        y += 46
    # service lines
    d.add(OUT, Line(x, y + 6, x + w, y + 6, stroke="Stadium Blue", sw=0.6, name="flap rule"),
          Text(x, y + 16, w, 12, [("Flap Head", "Service Lines")]))
    for k, col in enumerate((SERVICE_LINES[:4], SERVICE_LINES[4:])):
        d.add(OUT, Text(x + k * (w / 2), y + 34, w / 2 - 4, 90, [("Bullet Reverse Tight", t) for t in col]))
    d.add(OUT, Text(x, H - 40, w, 12, [("Footer Gold", "Think beyond space.")]))

    # --- back panel: self-mailer (rotated so the address reads along the 8.5" length)
    d.add(OUT, Rect(OX_BACK, -B, PANEL, H + 2 * B, fill="Paper", name="mailer background"))
    lw, lh = H, PANEL
    m = 24
    mail = [
        logo(m, m, 84),
        Text(m, m + 22, 200, 40, [("Return Address", "Cresa\n[Street address, suite]\n[City, State ZIP]")]),
        Rect(lw - m - 84, m, 84, 58, fill=None, stroke="Midnight", sw=0.75, name="indicia box"),
        Text(lw - m - 84, m + 12, 84, 40, [("Indicia", "PRSRT STD\nU.S. Postage\nPaid\n[Permit #]")]),
        Text(m, 112, 250, 50, [("Mailer Teaser", f"Where will {COMPANY}\ngrow next?")]),
        Text(m, 160, 240, 30, [("Body Small", "Your personalized healthcare road atlas is inside.")]),
        Placeholder(296, 116, lw - m - 296, 92, "Recipient address (variable data)", fill="Light Gray", tint=45),
        Line(m, 214, 268, 214, stroke="Goldenrod", sw=1.2, name="mailer rule"),
        Text(m, 224, 240, 12, [("Atlas Kicker", "Your Cresa healthcare team")]),
    ]
    for k, (nm, title, mobile, email) in enumerate(CONTACTS):
        cx = m + k * 132
        mail += [Placeholder(cx, 242, 34, 34, "Photo", fill="Light Gray", tint=60),
                 Text(cx + 40, 242, 92, 46, [("Mini Name", nm), ("Mini Detail", title),
                                             ("Mini Detail", f"M {mobile}"), ("Mini Detail", email)])]
    mail.append(Text(296, lh - m - 40, lw - m - 296, 36,
                     [("zz Placeholder Label", "Keep clear: USPS barcode zone (bottom 5/8\")")],
                     valign="bottom", layer="Placeholder Labels"))
    d.add(OUT, Rotated(OX_BACK, 0, PANEL, H, -90, mail))

    # --- cover
    cx0, cw = OX_COVER, PANEL
    d.add(OUT, Rect(cx0, -B, cw + B, H + 2 * B, fill="Paper", name="cover background"))
    # topo lines behind the badge
    for k in range(9):
        yy = 112 + k * 30
        pts = [(cx0 + t * (cw + B) / 40, yy + 9 * math.sin(t / 40 * 2 * math.pi * 1.3 + k * 0.8)
                + 5 * math.sin(t / 40 * 2 * math.pi * 3.1 + k)) for t in range(41)]
        d.add(OUT, Path(pts, False, None, "Light Gray", 0.8, name="topo line"))
    d.add(OUT, Rect(cx0, -B, cw + B, 96 + B, fill="Midnight", name="cover band"),
          Rect(cx0, 92, cw + B, 4, fill="Goldenrod", name="cover band rule"),
          logo(cx0 + PM, 28, 92, white=True),
          Text(cx0 + PM, 58, cw - 2 * PM, 18, [("Atlas Band", "Healthcare Road Atlas")]),
          Text(cx0 + cw - PM - 170, 36, 170, 12, [("Practice Label Reverse Right", "Healthcare Practice Group")]))
    bw, bh = 236, 252
    bx, by = cx0 + (cw - bw) / 2, 118
    d.add(OUT, *shield(bx, by, bw, bh, ("Shield Top", "Healthcare"),
                       [("Shield Line", [(None, "Where will\n"), ("Gold Text", f"{COMPANY}\n"),
                                         (None, "grow next?")])], name="cover badge", border=2.4, inset=8))
    d.add(OUT, Text(cx0 + PM, 380, cw - 2 * PM, 12, [("Atlas Kicker Center", "Real insight. Better locations.")]))
    # road scene
    gy = 470
    mountains = [[(cx0, gy), (cx0, gy - 8), (cx0 + 70, gy - 52), (cx0 + 150, gy)],
                 [(cx0 + 120, gy), (cx0 + 215, gy - 68), (cx0 + 320, gy)],
                 [(cx0 + 250, gy), (cx0 + 310, gy - 40), (cx0 + cw + B, gy - 8), (cx0 + cw + B, gy)]]
    for mt in mountains:
        d.add(OUT, Path(mt, True, "Stadium Blue", None, 0, tint=35, name="mountain"))
    d.add(OUT, Path([(cx0 + 199, gy - 57), (cx0 + 215, gy - 68), (cx0 + 231, gy - 57), (cx0 + 222, gy - 54),
                     (cx0 + 215, gy - 58), (cx0 + 207, gy - 53)], True, "Paper", None, 0, name="snowcap"))

    def hill(y_base, amp, phase, fill, tint, name):
        pts = [(cx0 + t * (cw + B) / 30, y_base - amp * math.sin(t / 30 * math.pi * 1.2 + phase))
               for t in range(31)]
        return Path(pts + [(cx0 + cw + B, H + B), (cx0, H + B)], True, fill, None, 0, tint=tint, name=name)
    d.add(OUT, hill(gy + 2, 10, 0.4, "Goldenrod", 38, "hill back"),
          hill(gy + 46, 16, 2.0, "Warm Orange", 28, "hill mid"),
          hill(gy + 96, 12, 1.0, "Goldenrod", 22, "hill front"))
    # winding road with perspective
    P0, P1, P2, P3 = (cx0 + 180, gy + 4), (cx0 + 250, gy + 60), (cx0 + 40, gy + 90), (cx0 + 120, H + B + 4)
    N = 60
    cl = [bezier(P0, P1, P2, P3, i / N) for i in range(N + 1)]
    left, right = [], []
    for i, (px, py) in enumerate(cl):
        t = i / N
        a, b_ = cl[max(i - 1, 0)], cl[min(i + 1, N)]
        dx, dy = b_[0] - a[0], b_[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        half = (2 + 92 * t ** 1.7) / 2
        left.append((px + nx * half, py + ny * half))
        right.append((px - nx * half, py - ny * half))
    d.add(OUT, Path(left + right[::-1], True, "Midnight", None, 0, name="road"))
    for i in range(2, N - 1, 4):
        t = i / N
        a, b_ = cl[i], cl[i + 2]
        d.add(OUT, Path([a, b_], False, None, "Goldenrod", 0.5 + 3.2 * t ** 1.5, name="road centerline"))
    for tx_, ty_, sz in [(cx0 + 18, gy + 30, 16), (cx0 + 36, gy + 26, 12), (cx0 + 285, gy + 40, 18),
                         (cx0 + 305, gy + 46, 13), (cx0 + 262, gy + 96, 22)]:
        d.add(OUT, Path([(tx_, ty_ - sz), (tx_ + sz * 0.45, ty_), (tx_ - sz * 0.45, ty_)], True, "Midnight", None,
                        0, tint=80, name="tree"))
    d.add(OUT, *pin(P0[0], P0[1] - 9, "Warm Orange", r=5, name="destination"))

    # ================= INSIDE =================
    d.add(IN, Rect(-B, -B, W + 2 * B, H + 2 * B, fill="Paper", name="inside background"))
    # --- map spread (left + middle panels)
    sx0, sw = IX_L + PM, 2 * PANEL - 2 * PM
    d.add(IN, Line(sx0, 26, sx0 + sw, 26, stroke="Midnight", sw=1.0, name="header rule"),
          Line(sx0, 28.5, sx0 + sw, 28.5, stroke="Midnight", sw=0.35, name="header rule thin"),
          Text(sx0, 33, 300, 10, [("Atlas Kicker", "Plate 1  ·  United States")]),
          Text(sx0 + sw - 300, 33, 300, 10, [("Practice Label Right", "Healthcare Practice Group")]),
          Text(sx0, 48, sw, 26, [("Headline Sync", [(None, f"{COMPANY} today: "),
                                                     ("Emphasis Medium", "your footprint, your next market.")])]),
          Text(sx0, 74, sw, 16, [("Body Small", "We map every location you operate today against patient demand, "
                                               "competition and access, so you can see where the next one belongs.")]))
    mitems, mh = us_map(sx0 + (sw - 500) / 2, 96, 500)
    d.add(IN, *mitems)
    ly = 96 + mh + 8
    legend = [("Midnight", "Current location"), ("Bright Blue", "Target market"),
              ("Warm Orange", "High-growth market")]
    lx = sx0
    for fill, lab in legend:
        d.add(IN, *pin(lx + 4, ly + 4.5, fill, r=3.4, name="legend " + lab),
              Text(lx + 12, ly, 90, 10, [("Legend", lab)]))
        lx += 98
    d.add(IN, Path([(lx, ly + 4.5), (lx + 18, ly + 4.5)], False, None, "Warm Orange", 1.4, name="legend interstate"),
          Text(lx + 24, ly, 80, 10, [("Legend", "Interstate")]),
          Text(sx0 + sw - 260, ly, 260, 24, [("zz Placeholder Label",
                                              "Sample locations shown: replace with client footprint")]))
    d.pages[IN][-1].layer = "Placeholder Labels"
    # what we deliver
    sy = ly + 18
    d.add(IN, Line(sx0, sy, sx0 + sw, sy, stroke="Midnight", sw=0.6, name="strip rule"),
          Text(sx0, sy + 7, 300, 16, [("H3", "What We Deliver")]))
    deliver = [("scorecard", "Opportunity Scorecards", "Scores ranking every market in your footprint."),
               ("workbook", "Analytics/KPI Workbooks", "The full data and methodology behind every finding."),
               ("map", "Drive-Time Access Maps", "Patient and labor catchments by site and submarket."),
               ("grid", "Site Ranking Matrices", "Candidate buildings scored against your growth criteria."),
               ("network", "Labor & Referral Network Maps", "Where clinical talent lives and referrals originate."),
               ("deck", "Board-Ready Executive Decks", "A clear narrative for leadership, lenders and your board.")]
    pw_ = PANEL - 2 * PM
    cw3 = (pw_ - 2 * 8) / 3
    for k, (ic, t, desc) in enumerate(deliver):
        px0 = (IX_L if k < 3 else IX_M) + PM
        xx, yy0 = px0 + (k % 3) * (cw3 + 8), sy + 28
        d.add(IN, Rect(xx, yy0, cw3, 110, fill="Paper", stroke="Light Gray", sw=1, name="deliverable card"),
              Rect(xx, yy0, cw3, 3, fill="Goldenrod", name="deliverable accent"),
              *icon(ic, xx + 10, yy0 + 13, 16),
              Text(xx + 10, yy0 + 38, cw3 - 18, 68, [("Card Title", t), ("Card Text", desc)]))

    # --- right panel: proof
    rx, rw = IX_R + PM, FLAP - 2 * PM
    d.add(IN, Line(rx, 26, rx + rw, 26, stroke="Midnight", sw=1.0, name="header rule"),
          Line(rx, 28.5, rx + rw, 28.5, stroke="Midnight", sw=0.35, name="header rule thin"),
          Text(rx, 33, rw, 10, [("Atlas Kicker", "Plate 2  ·  Proven routes")]),
          Text(rx, 48, rw, 26, [("Headline Sync", [(None, "Success "), ("Emphasis Medium", "Stories")])]))
    cases = [("Fresenius", [("2,235", "transactions"), ("$186.3M", "gross savings")],
              "A 14-year national partnership across one of the world’s largest healthcare portfolios, with "
              "planning that starts 3.5 years before lease expiration."),
             ("DispatchHealth", [("42", "transactions in 2022"), ("38", "markets")],
              "Rapid growth in new and existing markets. Every transaction closed ahead of schedule and within "
              "budget, through a single point of contact.")]
    yy = 82
    for lg, stats, body in cases:
        d.add(IN, Rect(rx, yy - 4, 132, 36, fill="Paper", name="logo tile"),
              Image(rx + 6, yy, 120, 28, client_logo(lg), align="l"),
              Line(rx, yy + 36, rx + rw, yy + 36, stroke="Goldenrod", sw=1.2, name="case rule"))
        for j, (n, lab) in enumerate(stats):
            d.add(IN, Text(rx + j * 120, yy + 44, 116, 24, [("Stat Number Small", n)]),
                  Text(rx + j * 120, yy + 68, 116, 10, [("Caption", lab)]))
        d.add(IN, Text(rx, yy + 84, rw, 48, [("Body Small", body)]))
        yy += 142
    # no-conflicts callout
    ny = yy + 2
    d.add(IN, Rect(rx - 6, ny, rw + 12, 104, fill="Midnight", name="no conflicts box"),
          Rect(rx - 6, ny, 3, 104, fill="Goldenrod", name="no conflicts accent"),
          Text(rx + 10, ny + 14, rw - 20, 84, [("Eyebrow Gold", "No conflicts. Ever."),
                                               ("Body Small Reverse", " "),
                                               ("Body Small Reverse Plain",
                                                "Most full-service firms earn the bulk of their revenue from "
                                                "landlords. Cresa never represents landlords or developers, so every "
                                                "recommendation, negotiation and dollar saved works for you.")]))
    ly2 = ny + 118
    d.add(IN, Text(rx, ly2 - 4, rw, 18, [("H3", "Trusted by Healthcare Leaders")]))
    wall = ["DaVita", "ChenMed", "Hanger", "Sharecare", "Modivcare", "SyneosHealth"]
    gw = (rw - 2 * 10) / 3
    for k, lg in enumerate(wall):
        c, r = k % 3, k // 3
        d.add(IN, Rect(rx + c * (gw + 10), ly2 + 14 + r * 38, gw, 32, fill="Paper", name="logo tile"),
              Image(rx + c * (gw + 10) + 6, ly2 + 17 + r * 38, gw - 12, 26, client_logo(lg),
                    name=f"client logo {lg}"))

    # fold marks (non-printing)
    for pg, xs in ((OUT, (OX_BACK, OX_COVER)), (IN, (IX_M, IX_R))):
        for fx in xs:
            ln = Line(fx, -B, fx, H + B, stroke="Bright Blue", sw=0.5, name="FOLD")
            ln.layer = "Placeholder Labels"
            d.add(pg, ln)
    return d
