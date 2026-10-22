"""Cresa Healthcare Practice Group: one-pager (front/back) and 11x17 bifold."""
import math
import os

from idmlkit import (CStyle, Doc, Image, Line, Oval, Path, Placeholder, PStyle, Rect, Text)

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
LOGO = os.path.join(ASSETS, "Cresa_Logo_Primary_wide.png")
LOGO_W = os.path.join(ASSETS, "Cresa_Logo_White_wide.png")
LOGO_RATIO = 2003 / 346
W, H, M = 612, 792, 36
B = 9  # bleed

CONTACTS = [
    ("Doug McNee", "Advisor", "713.882.6631", "dmcnee@cresa.com"),
    ("Jason Herbrich", "Senior Advisor", "713.885.8462", "jherbrich@cresa.com"),
]


def client_logo(name):
    return os.path.join(ASSETS, f"Logo_{name}.png")


# ------------------------------------------------------------------ styles
def add_styles(d):
    P = d.add_pstyle
    C = d.add_cstyle
    P(PStyle("Practice Label", "Roman", 10, 12, "Bright Blue"))
    P(PStyle("Practice Label Right", "Roman", 10, 12, "Bright Blue", align="right"))
    P(PStyle("Practice Label Reverse Right", "Roman", 10, 12, "Paper", align="right"))
    P(PStyle("Eyebrow", "Bold", 7.5, 9, "Midnight", 150, caps=True))
    P(PStyle("Eyebrow Gold", "Bold", 7.5, 9, "Goldenrod", 150, caps=True))
    P(PStyle("Hero", "Light", 31, 34, "Paper", -10))
    P(PStyle("Hero Cover", "Light", 31, 35, "Paper", -10, after=4))
    P(PStyle("Hero Sub", "Light", 13, 17, "Goldenrod", before=12))
    P(PStyle("Headline Reverse", "Light", 27, 31, "Paper", -10))
    P(PStyle("H2", "Light", 26, 30, "Midnight", -10))
    P(PStyle("H2 Small", "Light", 20, 24, "Midnight", -10))
    P(PStyle("H3", "Medium", 13, 16, "Midnight", after=4))
    P(PStyle("H4", "Medium", 9.5, 12, "Midnight", after=2))
    P(PStyle("H4 Reverse", "Medium", 9.5, 12, "Paper", after=2))
    P(PStyle("Body", "Roman", 9.5, 14, "Dark Gray", after=7))
    P(PStyle("Body Reverse", "Light", 10.5, 15, "Paper", after=6))
    P(PStyle("Body Small", "Roman", 8, 11, "Dark Gray", after=4))
    P(PStyle("Body Small Reverse", "Roman", 8, 11, "Paper", after=4))
    P(PStyle("Bullet", "Roman", 9, 12, "Dark Gray", after=4, bullet="▪", bullet_color="Goldenrod",
             left_indent=11, first_indent=-11))
    P(PStyle("Bullet Reverse", "Roman", 9, 12.5, "Paper", after=8, bullet="▪", bullet_color="Goldenrod",
             left_indent=12, first_indent=-12))
    P(PStyle("Stat Number", "Light", 34, 36, "Midnight", -20))
    P(PStyle("Stat Number Reverse", "Light", 34, 36, "Paper", -20))
    P(PStyle("Stat Number Small", "Light", 19, 22, "Midnight", -10))
    P(PStyle("Stat Label", "Roman", 8, 10.5, "Dark Gray"))
    P(PStyle("Stat Label Reverse", "Roman", 8, 10.5, "Paper", after=12))
    P(PStyle("Step Number", "Bold", 9, 11, "Paper", align="center"))
    P(PStyle("Step Title", "Medium", 9, 11, "Midnight", align="center", after=2))
    P(PStyle("Step Text", "Roman", 7.5, 9.5, "Dark Gray", align="center"))
    P(PStyle("Card Timing", "Medium", 7.5, 9, "Bright Blue", 20, before=4))
    P(PStyle("Contact Name", "Bold", 9.5, 12, "Paper"))
    P(PStyle("Contact Title", "Roman", 8.5, 11, "Goldenrod", after=3))
    P(PStyle("Contact Detail", "Roman", 8.5, 11, "Paper"))
    P(PStyle("CTA Head", "Medium", 10.5, 13, "Paper", after=4))
    P(PStyle("CTA Body", "Roman", 8.5, 11.5, "Paper"))
    P(PStyle("Footer Line", "Roman", 7.5, 9, "Paper", 40))
    P(PStyle("Footer Line Right", "Roman", 7.5, 9, "Paper", 40, align="right"))
    P(PStyle("Chart Label", "Medium", 8, 10, "Midnight"))
    P(PStyle("Chart Bar Label", "Medium", 8, 10, "Paper"))
    P(PStyle("Chart Bar Label Right", "Medium", 8, 10, "Paper", align="right"))
    P(PStyle("Caption", "Roman", 6.5, 8.5, "Dark Gray"))
    P(PStyle("Caption Right", "Roman", 6.5, 8.5, "Dark Gray", align="right"))
    P(PStyle("Outcome", "Medium", 8.5, 11, "Midnight"))
    P(PStyle("Submarkets", "Medium", 9, 14, "Midnight"))
    P(PStyle("Question", "Medium", 10, 13, "Midnight", after=4))
    P(PStyle("Bullet Reverse Tight", "Roman", 9, 12, "Paper", after=4, bullet="\u25AA", bullet_color="Goldenrod",
             left_indent=12, first_indent=-12))
    C(CStyle("Emphasis Medium", weight="Medium"))
    C(CStyle("Emphasis Gold", color="Goldenrod"))
    C(CStyle("Emphasis Bold", weight="Bold"))


# ------------------------------------------------------------------ icons
def _arc(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def icon(kind, x, y, s, color="Midnight", sw=1.3):
    """Simple line icons drawn as native shapes (editable in InDesign)."""
    def P(pts, closed=False):
        return Path([(x + px * s, y + py * s) for px, py in pts], closed, None, color, sw, name=f"icon {kind}")

    def O(px, py, pw, ph, fill=None):
        return Oval(x + px * s, y + py * s, pw * s, ph * s, fill=fill, stroke=None if fill else color, sw=sw,
                    name=f"icon {kind}")
    if kind == "chart":
        return [P([(0.05, 0.05), (0.05, 0.95), (0.95, 0.95)]),
                P([(0.2, 0.72), (0.42, 0.48), (0.6, 0.6), (0.88, 0.25)]),
                P([(0.7, 0.25), (0.88, 0.25), (0.88, 0.43)])]
    if kind == "search":
        return [O(0.06, 0.06, 0.6, 0.6), P([(0.6, 0.6), (0.93, 0.93)])]
    if kind == "pin":
        pts = _arc(0.5, 0.4, 0.32, 150, 390, 20)
        return [P(pts + [(0.5, 0.97)], True), O(0.39, 0.29, 0.22, 0.22)]
    if kind == "rank":
        out = []
        for k, yy in enumerate((0.2, 0.5, 0.8)):
            out.append(O(0.04, yy - 0.07, 0.14, 0.14))
            out.append(P([(0.32, yy), (0.95 - 0.15 * k, yy)]))
        return out
    if kind == "network":
        nodes = [(0.18, 0.2), (0.82, 0.2), (0.5, 0.55), (0.2, 0.85), (0.82, 0.85)]
        out = [P([nodes[2], n]) for n in (nodes[0], nodes[1], nodes[3], nodes[4])]
        out += [O(nx - 0.1, ny - 0.1, 0.2, 0.2, fill="Paper" if color != "Paper" else "Midnight") for nx, ny in nodes]
        out += [O(nx - 0.1, ny - 0.1, 0.2, 0.2) for nx, ny in nodes]
        return out
    if kind == "pie":
        return [O(0.05, 0.05, 0.9, 0.9), P([(0.5, 0.05), (0.5, 0.5), (0.93, 0.62)])]
    if kind == "shield":
        return [P([(0.5, 0.03), (0.9, 0.18), (0.86, 0.58), (0.5, 0.97), (0.14, 0.58), (0.1, 0.18)], True),
                P([(0.32, 0.5), (0.46, 0.64), (0.7, 0.37)])]
    if kind == "pulse":
        return [P([(0.0, 0.55), (0.24, 0.55), (0.34, 0.3), (0.48, 0.85), (0.6, 0.12), (0.7, 0.55), (1.0, 0.55)])]
    if kind == "cycle":
        a = _arc(0.5, 0.5, 0.42, 200, 470, 30)
        end = a[-1]
        return [P(a), P([(end[0] - 0.2, end[1] - 0.04), end, (end[0] - 0.02, end[1] - 0.22)])]
    if kind == "building":
        return [P([(0.15, 0.95), (0.15, 0.1), (0.62, 0.1), (0.62, 0.95)], False),
                P([(0.62, 0.4), (0.88, 0.4), (0.88, 0.95)]), P([(0.05, 0.95), (0.95, 0.95)]),
                P([(0.3, 0.3), (0.47, 0.3)]), P([(0.3, 0.5), (0.47, 0.5)]), P([(0.3, 0.7), (0.47, 0.7)])]
    raise ValueError(kind)


# ------------------------------------------------------------------ shared blocks
def logo(x, y, w, white=False):
    return Image(x, y, w, w / LOGO_RATIO, LOGO_W if white else LOGO, align="l", name="Cresa logo")


def eyebrow_with_dash(x, y, w, text, gold=False):
    style = "Eyebrow Gold" if gold else "Eyebrow"
    return [Rect(x, y + 3, 14, 2, fill="Goldenrod", name="eyebrow dash"),
            Text(x + 20, y, w - 20, 11, [(style, text)])]


def contact_block(d, page, x, y, c):
    name, title, mobile, email = c
    d.add(page,
          Placeholder(x, y, 52, 52, f"Headshot: {name}", fill="Stadium Blue", dark=True),
          Text(x + 60, y + 1, 112, 60, [("Contact Name", name), ("Contact Title", title),
                                        ("Contact Detail", [("Emphasis Medium", "M  "), (None, mobile)]),
                                        ("Contact Detail", email)]))


def footer(d, page, y0, with_logo, bleed_right=True, bleed_left=True, houston=False):
    """Navy 'Let's Discuss' band: contacts + QR call to action."""
    x0 = -B if bleed_left else 0
    x1 = W + B if bleed_right else W
    d.add(page, Rect(x0, y0, x1 - x0, H + B - y0, fill="Midnight", name="footer band"))
    d.add(page, *eyebrow_with_dash(M, y0 + 22, 200, "Let’s Discuss", gold=True))
    contact_block(d, page, M, y0 + 44, CONTACTS[0])
    contact_block(d, page, M + 178, y0 + 44, CONTACTS[1])
    # call to action
    d.add(page,
          Rect(396, y0 + 22, 1, 76, fill="Goldenrod", name="CTA divider"),
          Text(408, y0 + 20, 104, 86, [("CTA Head", "See where your next site should be."),
                                      ("CTA Body", "Scan to request a complimentary Healthcare Market Screen.")]),
          Rect(W - M - 54 - 4, y0 + 22, 62, 62, fill="Paper", name="QR backing"),
          Placeholder(W - M - 54, y0 + 26, 54, 54, "QR code: landing page URL TBD", fill="Paper"))
    fy = H - 30
    d.add(page, Line(M, fy - 10, W - M, fy - 10, stroke="Stadium Blue", sw=0.5, name="footer rule"))
    if with_logo:
        d.add(page, logo(M, fy - 1, 70, white=True))
    else:
        d.add(page, Text(M, fy, 260, 10, [("Footer Line", footer_name(houston))]))
    d.add(page, Text(W - M - 220, fy, 220, 10, [("Footer Line Right", [("Emphasis Gold", "Think beyond space."),
                                                                         (None, "   cresa.com")])]))


def process_steps(d, page, x, y, w):
    steps = [("Analyze", "Run the composite market analysis"),
             ("Target", "Pinpoint priority ZIP codes"),
             ("Specify", "Define building and site requirements"),
             ("Staff", "Map the available labor pool"),
             ("Refer", "Identify referral networks"),
             ("Contract", "Surface payer mix to start contracting")]
    n = len(steps)
    cw = w / n
    cy = y + 11
    d.add(page, Line(x + cw / 2, cy, x + w - cw / 2, cy, stroke="Goldenrod", sw=1.5, name="process line"))
    for k, (t, s) in enumerate(steps):
        cx = x + cw * k + cw / 2
        d.add(page, Oval(cx - 11, cy - 11, 22, 22, fill="Midnight", name=f"step {k + 1}"),
              Text(cx - 11, cy - 6, 22, 12, [("Step Number", str(k + 1))]),
              Text(x + cw * k + 3, y + 30, cw - 6, 50, [("Step Title", t), ("Step Text", s)]))


CAPABILITIES = [
    ("chart", "Market Demand Modeling",
     "Disease prevalence, addressable patients and growth projections by ZIP and service line."),
    ("search", "Competitive Saturation",
     "Provider density, capacity and cannibalization risk measured against unmet demand."),
    ("pin", "Drive-Time & Access",
     "Patient and labor catchments built from real travel times, not radius circles."),
    ("rank", "Site Ranking & Selection",
     "Weighted scoring that ranks buildings and submarkets against your criteria."),
    ("network", "Referral Network Mapping",
     "Referring-physician relationships and patient flow that show where demand originates."),
    ("pie", "Payer Mix Analysis",
     "Commercial, Medicare and Medicaid mix by market, so you can model reimbursement early."),
]

WHO_WE_SERVE = (["Health Systems", "Physician Networks", "Outpatient & Ambulatory", "Long-Term Care"],
                ["Laboratories", "Insurers & Administrators", "Home Healthcare", "Medical Devices & Health Tech"])

STATS = [("180+", "Industry-related local and national clients"),
         ("38", "States and Washington, DC served"),
         ("500+", "Occupier-only transactions nationally")]

def footer_name(houston):
    return "Cresa Houston  |  Healthcare Practice Group" if houston else "Cresa Healthcare Practice Group"


def practice_label(houston):
    return "Healthcare Practice Group  |  Houston" if houston else "Healthcare Practice Group"


HOUSTON_SUBMARKETS = "\u00a0\u00b7  ".join(n.replace(" ", "\u00a0") for n in (
    "Texas Medical Center", "Inner Loop", "Energy Corridor", "Katy", "Cypress", "The Woodlands",
    "Sugar Land", "Pearland", "Clear Lake"))
HOUSTON_LINE = ("We know where Houston\u2019s patients are moving and where clinical demand is outpacing supply. "
                "Locally led by Doug McNee and Jason Herbrich, and backed by Cresa\u2019s national Healthcare "
                "Practice Group.")


QUESTIONS = [
    ("\u201cIs this the right location for our next clinic?\u201d",
     "A site-level study tests each candidate space against patient demand, competition and drive times."),
    ("\u201cShould we expand, consolidate or exit?\u201d",
     "A multi-site study benchmarks every location and shows where to invest, hold or exit."),
    ("\u201cOur board needs to approve this.\u201d",
     "A board-ready market and strategy deck gives your leadership the full story."),
]


def intro(houston):
    return INTRO.replace("healthcare company, ", "healthcare company in Houston, ") if houston else INTRO


INTRO = ("Whether you lead a health system, physician group, outpatient network or healthcare company, "
         "industry disruption is changing not only how you deliver care, but where. Our specialists help you "
         "align real estate with your mission — building strategies with the economic and functional "
         "flexibility to grow.")
OCCUPIER_LINE = ("We work exclusively for occupiers — never landlords or developers — so every "
                 "recommendation is made in your best interest.")


# ================================================================== ONE-PAGER
def build_onepager(houston=False):
    d = Doc("Cresa_Healthcare_OnePager" + ("_Houston" if houston else ""), W, H, 2, bleed=B, margin=M)
    add_styles(d)
    F, BK = 0, 1

    # ---------- FRONT
    d.add(F, logo(M, 32, 96),
          Text(W - M - 300, 34, 300, 14, [("Practice Label Right", practice_label(houston))]))
    d.add(F, Placeholder(286, 66, W + B - 286, 322,
                         "Photo: clinician with patient in a bright, modern outpatient setting. "
                         "Vertical crop, subject right of center", lpad=52))
    d.add(F, Rect(-B, 104, 330 + B, 206, fill="Midnight", name="hero block"),
          Rect(-B, 306, 130, 4, fill="Goldenrod", name="hero accent"),
          Text(M, 132, 280, 190, [("Hero", [(None, "Like you,\n"), ("Emphasis Medium", "we’re specialists.")]),
                                  ("Hero Sub", ("Houston healthcare real estate strategy that supports your mission, "
                                                if houston else "Real estate strategy that supports your mission, ")
                                               + "your clinicians and your patients.")]))
    d.add(F, Text(M, 340, 230, 180, [("Body", intro(houston)), ("Body", [("Emphasis Medium", OCCUPIER_LINE)])]))
    d.add(F, Text(300, 404, 276, 18, [("H3", "Who we serve")]))
    for k, col in enumerate(WHO_WE_SERVE):
        d.add(F, Text(300 + k * 140, 426, 134, 80, [("Bullet", t) for t in col]))
    if houston:
        d.add(F, *eyebrow_with_dash(M, 520, 300, "Questions we help you answer"))
        for k, (q, ans) in enumerate(QUESTIONS):
            x = M + k * 184
            d.add(F, Rect(x, 540, 24, 2, fill="Goldenrod", name="question rule"),
                  Text(x, 548, 168, 66, [("Question", q), ("Body Small", ans)]))
    else:
        d.add(F, *eyebrow_with_dash(M, 528, 300, "2024 Healthcare Experience"))
        for k, (n, lab) in enumerate(STATS):
            x = M + k * 184
            d.add(F, Text(x, 548, 170, 38, [("Stat Number", n)]),
                  Text(x, 588, 150, 24, [("Stat Label", lab)]))
    # why band
    d.add(F, Rect(-B, 630, W + 2 * B, H + B - 630, fill="Light Gray", tint=60, name="why band"))
    d.add(F, Text(M, 650, 400, 18, [("H3", "Why healthcare occupiers choose Cresa")]))
    why = [("shield", "Conflict-free advocacy",
            "We never represent landlords or developers. Our only bias is you — your growth, your budget, your terms."),
           ("pulse", "Clinical demand fluency",
            "We model true patient demand from prevalence, payer mix and procedure-level data — not just rooftops."),
           ("cycle", "One team, every stage",
            "From market entry to renewals and portfolio rightsizing, a single point of contact manages every location.")]
    for k, (ic, t, s) in enumerate(why):
        x = M + k * 184
        d.add(F, *icon(ic, x, 680, 22))
        d.add(F, Text(x + 32, 680, 140, 80, [("H4", t), ("Body Small", s)]))
    d.add(F, Line(M, H - 24 - 8, W - M, H - 24 - 8, stroke="Dark Gray", sw=0.25, name="front footer rule"),
          Text(M, H - 24, 300, 10, [("Caption", footer_name(houston))]),
          Text(W - M - 200, H - 24, 200, 10, [("Caption Right", "cresa.com")]))

    # ---------- BACK (mirrors the front: white top, navy block over an image, gold accent)
    d.add(BK, logo(M, 32, 96),
          Text(W - M - 300, 34, 300, 14, [("Practice Label Right", "Healthcare Analytics  |  Portfolio Solutions")]))
    d.add(BK, Placeholder(-B, 66, 326 + B, 196,
                          "Image: sample analytics output, e.g. market heat map or drive-time map", lpad=36, rpad=60),
          Rect(286, 90, W + B - 286, 160, fill="Midnight", name="hero block"),
          Rect(W + B - 130, 246, 130, 4, fill="Goldenrod", name="hero accent"),
          Text(312, 112, 264, 130, [("Hero", [(None, "Where to grow is\n"), ("Emphasis Medium", "a data problem.")]),
                                    ("Hero Sub", "We solve it before you sign the lease.")]))
    d.add(BK, Text(M, 278, W - 2 * M, 34, [("Body",
          "Our healthcare analytics turn demand, competition and access data into defensible site decisions "
          + ("across Greater Houston " if houston else "") + "\u2014 "
          "so your real estate strategy is built on evidence, not instinct, and your board gets answers before it asks.")]))
    d.add(BK, *eyebrow_with_dash(M, 324, 300, "Capabilities"))
    for k, (ic, t, s) in enumerate(CAPABILITIES):
        col, row = k % 2, k // 2
        x, y = M + col * 176, 346 + row * 62
        d.add(BK, *icon(ic, x, y, 20))
        d.add(BK, Text(x + 30, y, 136, 60, [("H4", t), ("Body Small", s)]))
    # what you receive panel
    px, py, pw, ph = 400, 320, W - M - 400, 206
    d.add(BK, Rect(px, py, pw, ph, fill="Light Gray", tint=60, name="receive panel"),
          Rect(px, py, 3, ph, fill="Goldenrod", name="receive accent"),
          Text(px + 16, py + 16, pw - 28, ph - 24,
               [("Eyebrow", "What you receive"), ("Body Small", " "),
                ("Bullet", "100-point opportunity scorecards ranking every market in your footprint"),
                ("Bullet", "Demand and competition workbooks with full methodology"),
                ("Bullet", "Drive-time access maps by site and submarket"),
                ("Bullet", "Site ranking matrices tied to your growth criteria"),
                ("Bullet", "Board-ready executive decks for leadership and lenders")]))
    # process
    d.add(BK, Rect(M, 540, W - 2 * M, 94, fill="Light Gray", tint=60, name="process panel"))
    d.add(BK, *eyebrow_with_dash(M + 16, 550, 300, "Our Process"))
    process_steps(d, BK, M + 8, 566, W - 2 * M - 16)
    footer(d, BK, 646, with_logo=False, houston=houston)
    return d


# ================================================================== BIFOLD
def build_bifold(houston=False):
    d = Doc("Cresa_Healthcare_Bifold" + ("_Houston" if houston else ""), W, H, 4, bleed=B, margin=M)
    add_styles(d)
    COVER, IL, IR, BACK = 0, 1, 2, 3

    # ---------- COVER (right-hand page of outside spread)
    d.add(COVER, Placeholder(0, -B, W + B, H + 2 * B,
                             "Full-bleed photo: healthcare team or modern medical facility. Keep lower left calm "
                             "for title block", fill="Light Gray"))
    d.add(COVER, Rect(0, -B, 200, 90 + B, fill="Paper", name="logo tab"),
          logo(M, 34, 120),
          Rect(0, 456, 440, 226, fill="Midnight", name="title block"),
          Rect(0, 678, 170, 4, fill="Goldenrod", name="title accent"),
          Text(M, 480, 390, 190, [("Eyebrow Gold", practice_label(houston)), ("Body Small Reverse", " "),
                                  ("Hero Cover", [(None, "Real estate strategy\n"),
                                                  ("Emphasis Medium", "as specialized\nas your care.")]),
                                  ("Hero Sub", "Conflict-free advisory and data-driven analytics for "
                                               + ("Houston " if houston else "") + "healthcare occupiers.")]))

    # ---------- INSIDE LEFT
    d.add(IL, Text(M, 34, 300, 14, [("Practice Label", practice_label(houston))]),
          Text(M, 60, 540, 34, [("H2", [(None, "Like you, "), ("Emphasis Medium", "we’re specialists.")])]),
          Text(M, 106, 296, 130, [("Body", intro(houston)), ("Body", [("Emphasis Medium", OCCUPIER_LINE)])]))
    d.add(IL, Text(M, 238, 296, 18, [("H3", "Who we serve")]))
    for k, col in enumerate(WHO_WE_SERVE):
        d.add(IL, Text(M + k * 150, 260, 144, 70, [("Bullet", t) for t in col]))
    # stats panel
    sx, sy, sw_, sh = 364, 100, W - M - 364, 240
    d.add(IL, Rect(sx, sy, sw_, sh, fill="Midnight", name="stats panel"),
          Rect(sx, sy, 3, sh, fill="Goldenrod", name="stats accent"),
          Text(sx + 20, sy + 18, sw_ - 34, sh - 26,
               [("Eyebrow Gold", "Houston, covered"), ("Body Small Reverse", " "),
                ("Body Small Reverse", HOUSTON_LINE), ("Body Small Reverse", " ")] +
               [("Bullet Reverse Tight", t) for t in ("Texas Medical Center", "Inner Loop & Greater Heights",
                                                       "Energy Corridor & Katy", "Cypress & The Woodlands",
                                                       "Sugar Land & Fort Bend", "Pearland & Clear Lake")]
               if houston else
               [("Eyebrow Gold", "2024 by the numbers")] +
               sum([[("Stat Number Reverse", n), ("Stat Label Reverse", lab)] for n, lab in STATS], [])))
    d.add(IL, Line(M, 356, W - M, 356, stroke="Light Gray", sw=1, name="divider"))
    d.add(IL, Text(M, 372, 540, 28, [("H2 Small", [(None, "Occupier focused — "),
                                                    ("Emphasis Medium", "so our only bias is you.")])]),
          Text(M, 410, 256, 170, [
              ("Body", "Most full-service real estate firms represent both landlords and occupiers — and they "
                       "estimate nearly 85% of their revenue comes from landlords. When a broker owes duties to both "
                       "sides, something has to give, and the advantage typically goes to the landlord."),
              ("Body", "Cresa never represents landlords or developers. No listings to steer you toward, freedom "
                       "to negotiate aggressively, and savings that stay with you.")]))
    # revenue chart
    cx, cw = 318, W - M - 318
    d.add(IL, Text(cx, 414, cw, 12, [("Eyebrow", "Where the revenue comes from")]))
    bars = [("Typical full-service firm", 85), ("Cresa", 0)]
    for k, (lab, landlord) in enumerate(bars):
        y = 440 + k * 52
        d.add(IL, Text(cx, y, cw, 12, [("Chart Label", lab)]))
        lw = cw * landlord / 100
        if landlord:
            d.add(IL, Rect(cx, y + 14, lw, 22, fill="Dark Gray", name="bar landlord"),
                  Text(cx + 8, y + 20, lw - 16, 12, [("Chart Bar Label", f"{landlord}% landlord")]))
        d.add(IL, Rect(cx + lw, y + 14, cw - lw, 22, fill="Midnight", name="bar occupier"),
              Text(cx + lw + 4, y + 20, cw - lw - 10, 12,
                   [("Chart Bar Label Right", f"{100 - landlord}%" if landlord else "100% occupier")]))
    d.add(IL, Rect(cx, 548, 8, 8, fill="Dark Gray", name="legend"),
          Text(cx + 12, 547, 80, 10, [("Caption", "Landlord services")]),
          Rect(cx + 96, 548, 8, 8, fill="Midnight", name="legend"),
          Text(cx + 108, 547, 100, 10, [("Caption", "Occupier representation")]),
          Text(cx, 562, cw, 20, [("Caption", "Share of revenue by client type. Full-service firm figure "
                                             "reflects industry estimates.")]))
    # band across the spread (left half)
    by = 600
    d.add(IL, Rect(-B, by, W + B, H + B - by, fill="Light Gray", tint=60, name="spread band L"))
    d.add(IL, *eyebrow_with_dash(M, by + 22, 300, "Integrated services, one point of contact"))
    d.add(IL, Text(M, by + 42, 240, 120, [
        ("H4", "Every site, every stage of the life cycle."),
        ("Body Small", "Our healthcare specialists bring Cresa’s full platform to your portfolio, assessing it "
                       "holistically to uncover efficiencies and cost savings — from the first market study "
                       "to move-in day and every renewal after.")]))
    svc = (["Portfolio Strategy", "Transaction Management", "Project Management", "Lease Administration"],
           ["Location Strategy", "Labor Analytics", "Incentives Negotiation", "Strategic Consulting"])
    for k, col in enumerate(svc):
        d.add(IL, Text(300 + k * 140, by + 44, 134, 90, [("Bullet", t) for t in col]))

    # ---------- INSIDE RIGHT
    d.add(IR, Text(W - M - 300, 34, 300, 14, [("Practice Label Right", "Healthcare Analytics  |  Portfolio Solutions")]),
          Text(M, 60, 540, 64, [("H2", [(None, "Where to grow is a data problem.\n"),
                                        ("Emphasis Medium", "We solve it before you sign the lease.")])]),
          Text(M, 132, 540, 44, [("Body", "Our healthcare analytics turn demand, competition and access data into "
                                          "defensible site decisions. Instead of gut-feel recommendations and generic "
                                          "market narratives, you get scored, data-backed answers — and the "
                                          "confidence to move faster with less risk.")]))
    for k, (ic, t, s) in enumerate(CAPABILITIES):
        col, row = k % 3, k // 3
        x, y = M + col * 184, 190 + row * 66
        d.add(IR, *icon(ic, x, y, 18))
        d.add(IR, Text(x + 28, y, 144, 60, [("H4", t), ("Body Small", s)]))
    d.add(IR, Text(M, 336, 540, 18, [("H3", "Analytics matched to your decision")]))
    journey = [("Explore markets", "Healthcare Market Screening",
                "Rank and tier markets across your footprint by demand, supply, access and health burden.", "About 1 week"),
               ("Shortlist", "Single Market or Regional Opportunity Study",
                "Compare markets side by side to show which deserve investment.", "1–2 weeks"),
               ("Validate the site", "Facility or Service Line Utilization Study",
                "Confirm patient demand at the site and tie clinical volume to the real estate decision.",
                "1–1.5 weeks"),
               ("Win approval", "Executive-Ready Market & Strategy Deck",
                "A board-ready narrative for leadership, lenders and your board.", "1–2 weeks")]
    cw4 = (W - 2 * M - 3 * 12) / 4
    for k, (stage, prod, desc, timing) in enumerate(journey):
        x = M + k * (cw4 + 12)
        d.add(IR, Rect(x, 362, cw4, 150, fill=None, stroke="Light Gray", sw=1, name="journey card"),
              Rect(x, 362, cw4, 3, fill="Goldenrod", name="journey accent"),
              Oval(x + 12, 378, 20, 20, fill="Midnight", name="journey number"),
              Text(x + 12, 383, 20, 12, [("Step Number", str(k + 1))]),
              Text(x + 12, 408, cw4 - 24, 100, [("Eyebrow", stage), ("Body Small", " "), ("H4", prod),
                                                ("Body Small", desc), ("Card Timing", timing)]))
    d.add(IR, *eyebrow_with_dash(M, 526, 300, "What you gain"))
    outcomes = ["Confidence in the real estate decision", "Clinical strategy aligned to the market",
                "Reduced risk and faster approvals", "A long-term strategic advisor"]
    for k, o in enumerate(outcomes):
        x = M + k * (cw4 + 12)
        d.add(IR, Oval(x, 548, 14, 14, fill="Goldenrod", name="outcome dot"),
              Path([(x + 3.5, 555), (x + 6, 558), (x + 10.5, 552)], False, None, "Midnight", 1.3, name="outcome check"),
              Text(x + 20, 547, cw4 - 22, 30, [("Outcome", o)]))
    # band across the spread (right half)
    by = 600
    d.add(IR, Rect(0, by, W + B, H + B - by, fill="Light Gray", tint=60, name="spread band R"))
    d.add(IR, *eyebrow_with_dash(M, by + 22, 300, "Our Process"))
    process_steps(d, IR, M, by + 46, W - 2 * M)
    d.add(IR, Text(M, by + 140, W - 2 * M, 40, [
        ("Body Small", [("Emphasis Medium", "From analysis to signed lease. "),
                        (None, "Each step hands your brokers a sharper target — priority ZIP codes, building "
                               "requirements, labor and referral insight, and payer data to begin contracting early.")])]))

    # ---------- BACK (left-hand page of outside spread)
    d.add(BACK, *eyebrow_with_dash(M, 38, 300, "Proven results"))
    d.add(BACK, Text(M, 56, 540, 32, [("H2", "Success stories")]))
    cases = [("Fresenius", "A 14-year national partnership",
              [("2,235", "transactions"), ("$186.3M", "gross savings")],
              "Consulting, labor analytics, location strategy, incentives, transaction and project management "
              "across one of the world’s largest healthcare portfolios — with metrics on every completed "
              "project and planning that starts 3.5 years before lease expiration to maximize leverage."),
             ("DispatchHealth", "Rapid growth, on time and on budget",
              [("42", "transactions in 2022"), ("38", "markets")],
              "Portfolio strategy, account management, transaction management and lease administration for "
              "challenging requirements in new and existing markets. Every transaction closed ahead of schedule "
              "and within budget, through a single point of contact."),
             ("DaVita", "Headquarters leverage, put to work",
              [("20+", "year partnership"), ("430K", "SF HQ building")],
              "Transaction and project management for DaVita’s downtown Denver headquarters relocation and "
              "expansion. Occupying ~80% of the building, DaVita used that leverage to control design and secure "
              "a private entrance, elevator bank and green-roof event terrace.")]
    ccw = (W - 2 * M - 2 * 18) / 3
    for k, (lg, head, stats, body) in enumerate(cases):
        x = M + k * (ccw + 18)
        d.add(BACK, Image(x, 104, ccw * 0.72, 36, client_logo(lg), align="l", valign="c"),
              Line(x, 152, x + ccw, 152, stroke="Goldenrod", sw=1.5, name="case rule"),
              Text(x, 162, ccw, 30, [("H4", head)]))
        for j, (n, lab) in enumerate(stats):
            sx_ = x + j * (ccw / 2)
            d.add(BACK, Text(sx_, 186, ccw / 2 - 4, 26, [("Stat Number Small", n)]),
                  Text(sx_, 212, ccw / 2 - 6, 12, [("Caption", lab)]))
        d.add(BACK, Text(x, 236, ccw, 140, [("Body", body)]))
    # client wall
    d.add(BACK, Line(M, 386, W - M, 386, stroke="Light Gray", sw=1, name="divider"))
    d.add(BACK, *eyebrow_with_dash(M, 402, 300, "Trusted by healthcare leaders"))
    wall = ["Joerns", "Hanger", "Modivcare", "Benevis", "PartnersInHealth", "AtlantaOralFacial",
            "Sharecare", "RTGMedical", "ChenMed", "OneBlood", "ERT", "SyneosHealth"]
    lw_, gap = (W - 2 * M - 5 * 16) / 6, 16
    for k, lg in enumerate(wall):
        col, row = k % 6, k // 6
        x, y = M + col * (lw_ + gap), 426 + row * 62
        d.add(BACK, Image(x + 4, y + 6, lw_ - 8, 34, client_logo(lg), name=f"client logo {lg}"))
    footer(d, BACK, 568, with_logo=True, bleed_right=False, houston=houston)
    return d
