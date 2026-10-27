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
def option_e(contact):
    name, title = contact[0], contact[1]
    d = Doc("Cresa_BusinessCard_OptionE_Contour", CW, CH, 2, bleed=B, margin=CM)
    add_option_styles(d)
    pcx, pcy = 200, 62
    d.add(0, Rect(-B, -B, CW + 2 * B, CH + 2 * B, fill="Paper", name="card front"),
          *contours(pcx, pcy, 6, 8.5, "Light Gray", 0.7),
          *teardrop(pcx, pcy - 10, 6.5, "Goldenrod"),
          logo(CM, CM, 64),
          Text(CM, CM + 22, 150, 8, [("Card Label Left", "Healthcare Practice Group")]),
          Text(CM, 54, 150, 32, [("Card Name", name), ("Card Role", title)]),
          Rect(CM, 86, 26, 2, fill="Goldenrod", name="name rule"),
          Text(CM, 94, 130, 40, contact_lines("Card Contact", contact)),
          Text(CW - CM - 110, 112, 110, 20, [("Card Address", "Cresa Houston  ·  [Street address]\n"
                                                              "Houston, TX [ZIP]")]))
    d.add(1, Rect(-B, -B, CW + 2 * B, CH + 2 * B, fill="Midnight", name="card back"),
          *contours(pcx + 6, pcy + 8, 7, 9, "Stadium Blue", 0.8, seed=1.2),
          *teardrop(pcx + 6, pcy - 2, 7, "Goldenrod"),
          Text(CM, 30, 160, 8, [("Card Kicker", "Healthcare Practice Group")]),
          Text(CM, 44, 160, 40, [("Card Headline", [(None, "The right diagnosis\n"),
                                                    ("Emphasis Medium", "for your next location.")])]),
          logo(CM, CH - CM - 11, 58, white=True))
    return d


def build_options():
    c = CONTACTS[0]
    return [option_c(c), option_d(c), option_e(c)]
