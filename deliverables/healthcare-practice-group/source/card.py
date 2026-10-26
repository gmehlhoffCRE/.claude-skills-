"""Healthcare Practice Group business cards (3.5 x 2 in), matched to the bifold system."""
from idmlkit import Doc, Placeholder, PStyle, Rect, Text
from layouts import B, CONTACTS, add_styles, logo
from trifold import shield

CW, CH = 252, 144
CM = 14


def add_card_styles(d):
    add_styles(d)
    P = d.add_pstyle
    P(PStyle("Card Label", "Bold", 5, 7, "Bright Blue", 150, caps=True, align="right"))
    P(PStyle("Card Name", "Medium", 11.5, 13.5, "Midnight", -5))
    P(PStyle("Card Role", "Roman", 7, 9, "Dark Gray", after=0))
    P(PStyle("Card Contact", "Roman", 6.8, 9, "Midnight"))
    P(PStyle("Card Address", "Roman", 6, 8, "Dark Gray", align="right"))
    P(PStyle("Card Kicker", "Bold", 5.2, 7, "Goldenrod", 150, caps=True))
    P(PStyle("Card Headline", "Light", 14, 16.5, "Paper", -10))
    P(PStyle("Card Headline Dark", "Light", 13, 15.5, "Midnight", -10))
    P(PStyle("Card Body", "Roman", 6.3, 8.5, "Paper"))
    P(PStyle("Card Body Dark", "Roman", 6.3, 8.5, "Dark Gray"))
    P(PStyle("Card Shield Top", "BoldCond", 4.2, 5, "Midnight", 150, caps=True, align="center"))
    P(PStyle("Card Shield Line", "BoldCond", 8, 8.6, "Paper", 10, caps=True, align="center"))
    P(PStyle("zz Card Label", "Medium", 5, 6, "Dark Gray", 40, caps=True, align="center"))


def front(d, page, contact):
    name, title, mobile, email = contact
    d.add(page, Rect(-B, -B, CW + 2 * B, CH + 2 * B, fill="Paper", name="card front"),
          logo(CM, CM, 64),
          Text(CW - CM - 140, CM + 3, 140, 8, [("Card Label", "Healthcare Practice Group")]),
          Text(CM, 54, 180, 32, [("Card Name", name), ("Card Role", title)]),
          Rect(CM, 86, 26, 2, fill="Goldenrod", name="name rule"),
          Text(CM, 94, 130, 40, [("Card Contact", [("Emphasis Medium", "M  "), (None, mobile)]),
                                 ("Card Contact", email), ("Card Contact", "cresa.com")]),
          Text(CW - CM - 110, 106, 110, 26, [("Card Address", "Cresa Houston\n[Street address, suite]\n"
                                                              "Houston, TX [ZIP]")]),
          Rect(-B, CH - 4, 96 + B, 4 + B, fill="Goldenrod", name="card accent"))


def back_navy(d, page):
    d.add(page, Rect(-B, -B, CW + 2 * B, CH + 2 * B, fill="Midnight", name="card back"),
          Rect(CM, 28, 2.5, 74, fill="Goldenrod", name="callout bar"),
          Text(CM + 12, 30, 160, 8, [("Card Kicker", "Healthcare Practice Group")]),
          Text(CM + 12, 42, 170, 38, [("Card Headline", [(None, "A second opinion\n"),
                                                         ("Emphasis Medium", "you can really trust.")])]),
          Text(CM + 12, 82, 160, 22, [("Card Body", "Occupier-only real estate advisory and healthcare "
                                                    "analytics. Never landlords or developers.")]),
          Rect(CW - CM - 40, 26, 40, 40, fill="Paper", name="QR backing"),
          Placeholder(CW - CM - 37, 29, 34, 34, "QR", fill="Paper"),
          logo(CW - CM - 58, CH - CM - 11, 58, white=True))


def back_atlas(d, page):
    d.add(page, Rect(-B, -B, CW + 2 * B, CH + 2 * B, fill="Paper", name="card back"),
          *shield(CM + 2, 22, 76, 82, ("Card Shield Top", "Healthcare"),
                  [("Card Shield Line", "Where will\nyou grow\nnext?")], name="card badge", border=1.4, inset=3),
          Text(108, 34, 130, 36, [("Card Headline Dark", [(None, "Let’s map\n"),
                                                         ("Emphasis Medium", "your next market.")])]),
          Text(108, 72, 130, 30, [("Card Body Dark", "Healthcare analytics and occupier-only advisory, "
                                                     "from first market screen to signed lease.")]),
          Rect(-B, CH - 18, CW + 2 * B, 18 + B, fill="Midnight", name="card band"),
          Rect(-B, CH - 20, CW + 2 * B, 2, fill="Goldenrod", name="card band rule"),
          logo(CW - CM - 48, CH - 13, 48, white=True))


def build_cards():
    docs = []
    for (name, title, mobile, email) in CONTACTS:
        last = name.split()[-1]
        d = Doc(f"Cresa_BusinessCard_{last}", CW, CH, 2, bleed=B, margin=CM)
        add_card_styles(d)
        front(d, 0, (name, title, mobile, email))
        back_navy(d, 1)
        docs.append(d)
    alt = Doc("Cresa_BusinessCard_AltBack_RoadAtlas", CW, CH, 1, bleed=B, margin=CM)
    add_card_styles(alt)
    back_atlas(alt, 0)
    docs.append(alt)
    return docs
