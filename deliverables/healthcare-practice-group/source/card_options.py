"""Three more business card directions (C, D, E), shown with Doug McNee's details."""
import math

from card import CH, CM, CW, add_card_styles
from idmlkit import Doc, Path, Placeholder, PStyle, Rect, Text
from layouts import B, CONTACTS, logo
from trifold import TAGLINE

ADDRESS = "Cresa Houston\n[Street address, suite]\nHouston, TX [ZIP]"


def add_option_styles(d):
    add_card_styles(d)
    P = d.add_pstyle
    P(PStyle("Card Name Reverse", "Medium", 11.5, 13.5, "Paper", -5))
    P(PStyle("Card Role Gold", "Roman", 7, 9, "Goldenrod"))
    P(PStyle("Card Contact Reverse", "Roman", 6.8, 9, "Paper"))
    P(PStyle("Card Address Reverse", "Roman", 6, 8, "Paper", align="right"))
    P(PStyle("Card Address Left", "Roman", 6, 8, "Dark Gray"))
    P(PStyle("Card Label Left", "Bold", 5, 7, "Bright Blue", 150, caps=True))
    P(PStyle("Card Kicker Right", "Bold", 5.2, 7, "Goldenrod", 150, caps=True, align="right"))
    P(PStyle("Card Headline Big Dark", "Light", 15, 17.5, "Midnight", -10))
    P(PStyle("Card Headline Tall", "Light", 15, 17.5, "Paper", -10))
    P(PStyle("Card Tagline Dark", "Medium", 7, 9, "Midnight"))


def contact_lines(style, contact):
    _, _, mobile, email = contact
    return [(style, [("Emphasis Medium", "M  "), (None, mobile)]), (style, email), (style, "cresa.com")]


def teardrop(cx, cy, r, fill, name="pin"):
    """Map-pin marker: circle head with a point below."""
    head = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(150, 391, 12)]
    return [Path(head + [(cx, cy + r * 2.3)], True, fill, None, 0, name=name),
            Path([(cx + r * 0.38 * math.cos(math.radians(a)), cy + r * 0.38 * math.sin(math.radians(a)))
                  for a in range(0, 360, 20)], True, "Paper", None, 0, name=name + " eye")]


def contours(cx, cy, n, step, stroke, sw=0.6, seed=0.0, r0=10):
    rings = []
    for k in range(n):
        r = r0 + k * step
        pts = []
        for i in range(72):
            th = 2 * math.pi * i / 72
            rr = r * (1 + 0.10 * math.sin(3 * th + seed + k * 0.35) + 0.06 * math.sin(5 * th + 1.7 + seed))
            pts.append((cx + rr * math.cos(th) * 1.25, cy + rr * math.sin(th)))
        rings.append(Path(pts, True, None, stroke, sw, name="contour"))
    return rings


# ------------------------------------------------------------------ Option C: bold navy front
def option_c(contact):
    name, title = contact[0], contact[1]
    d = Doc("Cresa_BusinessCard_OptionC_NavyFront", CW, CH, 2, bleed=B, margin=CM)
    add_option_styles(d)
    d.add(0, Rect(-B, -B, CW + 2 * B, CH + 2 * B, fill="Midnight", name="card front"),
          logo(CM, CM, 64, white=True),
          Text(CW - CM - 140, CM + 3, 140, 8, [("Card Kicker Right", "Healthcare Practice Group")]),
          Text(CM, 54, 180, 32, [("Card Name Reverse", name), ("Card Role Gold", title)]),
          Rect(CM, 86, 26, 2, fill="Goldenrod", name="name rule"),
          Text(CM, 94, 130, 40, contact_lines("Card Contact Reverse", contact)),
          Text(CW - CM - 110, 106, 110, 26, [("Card Address Reverse", ADDRESS)]))
    d.add(1, Rect(-B, -B, CW + 2 * B, CH + 2 * B, fill="Paper", name="card back"),
          Rect(-B, -B, 8 + B, CH + 2 * B, fill="Goldenrod", name="edge bar"),
          Text(CM + 12, 28, 180, 8, [("Card Label Left", "Healthcare Practice Group")]),
          Text(CM + 12, 42, 200, 40, [("Card Headline Big Dark", [(None, "A second opinion\n"),
                                                                  ("Emphasis Medium", "you can really trust.")])]),
          Rect(CM + 12, 88, 18, 1.5, fill="Goldenrod", name="tagline rule"),
          Text(CM + 12, 94, 200, 12, [("Card Tagline Dark", TAGLINE)]),
          logo(CW - CM - 58, CH - CM - 11, 58))
    return d


# ------------------------------------------------------------------ Option D: vertical
def option_d(contact):
    name, title = contact[0], contact[1]
    VW, VH = CH, CW  # 2 x 3.5 portrait
    d = Doc("Cresa_BusinessCard_OptionD_Vertical", VW, VH, 2, bleed=B, margin=CM)
    add_option_styles(d)
    d.add(0, Rect(-B, -B, VW + 2 * B, VH + 2 * B, fill="Paper", name="card front"),
          Rect(-B, 92, 5 + B, 96, fill="Goldenrod", name="side bar"),
          logo(CM, CM + 4, 74),
          Text(CM, 44, VW - 2 * CM, 8, [("Card Label Left", "Healthcare Practice Group")]),
          Text(CM, 96, VW - 2 * CM, 34, [("Card Name", name), ("Card Role", title)]),
          Rect(CM, 134, 22, 1.5, fill="Goldenrod", name="name rule"),
          Text(CM, 142, VW - 2 * CM, 40, contact_lines("Card Contact", contact)),
          Text(CM, VH - CM - 26, VW - 2 * CM, 26, [("Card Address Left", ADDRESS)]))
    d.add(1, Rect(-B, -B, VW + 2 * B, VH + 2 * B, fill="Midnight", name="card back"),
          Rect(CM, 32, 22, 2.5, fill="Goldenrod", name="top rule"),
          Text(CM, 42, VW - 2 * CM, 8, [("Card Kicker", "Healthcare Practice Group")]),
          Text(CM, 56, VW - 2 * CM, 76, [("Card Headline Tall", [(None, "A second\nopinion "),
                                                                 ("Emphasis Medium", "you can\nreally trust.")])]),
          Text(CM, 126, VW - 2 * CM, 26, [("Card Tagline", "The right diagnosis\nfor your next location.")]),
          Rect(CM, VH - CM - 44, 44, 44, fill="Paper", name="QR backing"),
          Placeholder(CM + 3, VH - CM - 41, 38, 38, "QR", fill="Paper"),
          logo(VW - CM - 52, VH - CM - 10, 52, white=True))
    return d


# ------------------------------------------------------------------ Option E: map contours
def hospital_sign(cx, cy, size=15):
    """Blue road-sign hospital marker: white-bordered square with a white H."""
    h = size / 2
    return [Rect(cx - h - 1.5, cy - h - 1.5, size + 3, size + 3, fill="Paper", name="hospital sign border"),
            Rect(cx - h, cy - h, size, size, fill="Bright Blue", name="hospital sign"),
            Text(cx - h, cy - h * 0.62, size, size, [("Hospital H", "H")], name="hospital H")]


def street_map(x_edge, minor, major, highway, top=-B, bottom=CH + B, right=CW + B, seed=0.0):
    """Street-grid texture: minor streets, two arterials, a parks block or two and a curving highway.
    Streets start at a wavy left edge x_edge(y) so the map fades in from the right."""
    items = []
    step = 12
    xmin = min(x_edge(y) for y in range(int(top), int(bottom)))
    # vertical streets (slight jog so it doesn't look like graph paper)
    x = xmin + 4
    k = 0
    while x < right:
        ys = [y for y in range(int(top), int(bottom) + 1, 3) if x >= x_edge(y)]
        if len(ys) > 1:
            jog = 2.5 * math.sin(k * 1.7 + seed)
            items.append(Path([(x, ys[0]), (x + jog, ys[-1])], False, None, minor, 0.5, name="street"))
        x += step + (3 if k % 3 == 2 else 0)
        k += 1
    # horizontal streets
    y = top + 6
    k = 0
    while y < bottom:
        x0 = x_edge(y)
        if x0 < right:
            items.append(Path([(x0, y), (right, y + 1.5 * math.sin(k + seed))], False, None, minor, 0.5,
                              name="street"))
        y += step + (2 if k % 4 == 1 else 0)
        k += 1
    # park blocks
    for (px, py) in ((xmin + 60, 24), (xmin + 98, 96)):
        items.insert(0, Rect(px, py, 22, 20, fill=minor, tint=55, name="park block"))
    # arterials
    for (p0, p1) in (((xmin + 10, bottom), (right, top + 30)), ((xmin + 44, top), (right - 30, bottom))):
        pts = [(p0[0] + (p1[0] - p0[0]) * t / 20, p0[1] + (p1[1] - p0[1]) * t / 20) for t in range(21)]
        pts = [p for p in pts if p[0] >= x_edge(p[1])]
        if len(pts) > 1:
            items.append(Path(pts, False, None, major, 1.3, name="arterial"))
    # curving highway
    P0, P1, P2, P3 = (xmin - 4, bottom - 20), (xmin + 70, 40), (xmin + 120, 120), (right, top + 10)
    hw = []
    for i in range(41):
        t = i / 40
        u = 1 - t
        px = u ** 3 * P0[0] + 3 * u * u * t * P1[0] + 3 * u * t * t * P2[0] + t ** 3 * P3[0]
        py = u ** 3 * P0[1] + 3 * u * u * t * P1[1] + 3 * u * t * t * P2[1] + t ** 3 * P3[1]
        if px >= x_edge(py):
            hw.append((px, py))
    items.append(Path(hw, False, None, highway, 2.2, name="highway"))
    return items


def option_e(contact):
    name, title = contact[0], contact[1]
    d = Doc("Cresa_BusinessCard_OptionE_StreetMap", CW, CH, 2, bleed=B, margin=CM)
    add_option_styles(d)
    d.add_pstyle(PStyle("Hospital H", "Bold", 10, 10, "Paper", align="center"))
    front_edge = lambda y: 132 + 12 * math.sin(y / 22)
    back_edge = lambda y: 182 + 8 * math.sin(y / 20 + 1)
    d.add(0, Rect(-B, -B, CW + 2 * B, CH + 2 * B, fill="Paper", name="card front"),
          *street_map(front_edge, "Light Gray", "Light Gray", "Goldenrod"),
          *hospital_sign(206, 58),
          logo(CM, CM, 64),
          Text(CM, CM + 22, 150, 8, [("Card Label Left", "Healthcare Practice Group")]),
          Text(CM, 48, 150, 32, [("Card Name", name), ("Card Role", title)]),
          Rect(CM, 79, 26, 2, fill="Goldenrod", name="name rule"),
          Text(CM, 86, 130, 28, contact_lines("Card Contact", contact)),
          Text(CM, 114, 104, 18, [("Card Address Left", "[Street address, suite]\nHouston, TX [ZIP]")]))
    d.add(1, Rect(-B, -B, CW + 2 * B, CH + 2 * B, fill="Midnight", name="card back"),
          *street_map(back_edge, "Stadium Blue", "Stadium Blue", "Goldenrod", seed=1.3),
          *hospital_sign(224, 70),
          Text(CM, 30, 160, 8, [("Card Kicker", "Healthcare Practice Group")]),
          Text(CM, 44, 160, 40, [("Card Headline", [(None, "The right diagnosis\n"),
                                                    ("Emphasis Medium", "for your next location.")])]),
          logo(CM, CH - CM - 11, 58, white=True))
    return d


def build_options():
    c = CONTACTS[0]
    return [option_c(c), option_d(c), option_e(c)]
