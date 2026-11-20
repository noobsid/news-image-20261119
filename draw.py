#!/usr/bin/env python3
"""Thursday 19 November 2026 - one day of world news as a broadsheet page.

Data-driven renderer: every story lives in the TABLES section below and the
page is assembled by generic panel, strip and brief engines. Flat vector
style on cream newsprint, drawn with PIL (build-time only; the submitted
program main.py just copies the finished entry.png).
"""
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 34                      # page margin
CW = W - 2 * M              # content width

PAPER = (247, 241, 222)
PAPER_D = (238, 229, 203)
INK = (20, 19, 16)
FAINT = (90, 84, 70)
RED = (179, 32, 42)
BLUE = (29, 78, 137)
TEAL = (14, 116, 110)
GOLD = (176, 124, 22)
GREEN = (46, 110, 54)
PURPLE = (96, 62, 140)
WHITE = (255, 255, 255)

REGION_COLOUR = {
    "EUROPE": RED, "ASIA": GOLD, "AMERICAS": BLUE, "MIDDLE EAST": TEAL,
    "AFRICA": GREEN, "OCEANIA": PURPLE, "GLOBAL": INK,
}

FD = "/usr/share/fonts/truetype/liberation/"
F_SERIF = FD + "LiberationSerif-Bold.ttf"
F_SERIF_I = FD + "LiberationSerif-BoldItalic.ttf"
F_SANS = FD + "LiberationSans-Regular.ttf"
F_SANS_B = FD + "LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, width):
    """Greedy word wrap against pixel width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_line(d, text, fnt, width):
    """One line, ellipsised to fit."""
    if d.textlength(text, font=fnt) <= width:
        return text
    while text and d.textlength(text + "…", font=fnt) > width:
        text = text.rsplit(" ", 1)[0] if " " in text else text[:-1]
    return text + "…"


# ---------------------------------------------------------------- art scenes
def art(d, kind, x, y, w, h, accent):
    """Tiny flat-icon scenes, one per story kind. Box is (x, y, w, h)."""
    cx, cy = x + w // 2, y + h // 2
    if kind == "summit":                       # three flags over a table
        for i, c in enumerate((RED, GOLD, BLUE)):
            fx = x + 18 + i * (w - 36) // 2
            d.line([fx, y + 8, fx, y + h - 16], fill=INK, width=3)
            d.polygon([fx, y + 8, fx + 20, y + 14, fx, y + 20], fill=c)
        d.rectangle([x + 8, y + h - 14, x + w - 8, y + h - 8], fill=INK)
    elif kind == "chip":                       # AI chip with pins
        s = min(w, h) - 26
        bx, by = cx - s // 2, cy - s // 2
        d.rectangle([bx, by, bx + s, by + s], outline=INK, width=4)
        d.rectangle([bx + s // 4, by + s // 4, bx + 3 * s // 4, by + 3 * s // 4],
                    fill=accent)
        for i in range(3):
            p = bx + s // 4 + i * s // 4
            d.line([p, by - 9, p, by], fill=INK, width=3)
            d.line([p, by + s, p, by + s + 9], fill=INK, width=3)
            d.line([bx - 9, p, bx, p], fill=INK, width=3)
            d.line([bx + s, p, bx + s + 9, p], fill=INK, width=3)
    elif kind == "chart-up":
        d.line([x + 10, y + h - 12, x + w - 10, y + h - 12], fill=INK, width=3)
        pts = [(x + 14, y + h - 22), (x + w // 3, y + h // 2),
               (x + w // 2, y + h - 34), (x + w - 16, y + 14)]
        d.line(pts, fill=accent, width=5)
        d.polygon([pts[-1], (pts[-1][0] - 14, pts[-1][1] + 2),
                   (pts[-1][0] - 2, pts[-1][1] + 14)], fill=accent)
    elif kind == "chart-down":
        d.line([x + 10, y + h - 12, x + w - 10, y + h - 12], fill=INK, width=3)
        pts = [(x + 14, y + 16), (x + w // 3, y + h // 3),
               (x + w // 2, y + h - 40), (x + w - 16, y + h - 20)]
        d.line(pts, fill=RED, width=5)
        d.polygon([pts[-1], (pts[-1][0] - 14, pts[-1][1] - 2),
                   (pts[-1][0] - 2, pts[-1][1] - 14)], fill=RED)
    elif kind == "missile":
        d.polygon([x + w - 30, y + 10, x + w - 12, y + 26, x + w - 34, y + 30],
                  fill=INK)
        d.line([x + w - 28, y + 26, x + 30, y + h - 18], fill=RED, width=4)
        for i in range(3):
            bx = x + 16 + i * (w // 3)
            d.rectangle([bx, y + h - 16, bx + 20, y + h - 6], fill=accent)
    elif kind == "storm":
        d.arc([cx - 34, cy - 30, cx + 34, cy + 38], 300, 160, fill=BLUE, width=6)
        d.arc([cx - 20, cy - 16, cx + 20, cy + 24], 300, 160, fill=TEAL, width=5)
        d.polygon([cx + 2, cy + 2, cx - 10, cy + 26, cx + 2, cy + 26,
                   cx - 4, cy + 44, cx + 14, cy + 18, cx + 3, cy + 18],
                  fill=GOLD)
    elif kind == "globe":
        r = min(w, h) // 2 - 8
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLUE, width=4)
        d.ellipse([cx - r // 3, cy - r, cx + r // 3, cy + r], outline=BLUE, width=2)
        d.line([cx - r, cy, cx + r, cy], fill=BLUE, width=2)
    elif kind == "gavel":
        d.line([x + 24, y + h - 18, x + w - 24, y + 22], fill=INK, width=7)
        d.rectangle([x + w - 46, y + 8, x + w - 16, y + 30], fill=accent)
        d.rectangle([x + 14, y + h - 14, x + 74, y + h - 8], fill=INK)
    elif kind == "ship":
        d.polygon([x + 14, cy + 6, x + w - 14, cy + 6, x + w - 30, cy + 26,
                   x + 30, cy + 26], fill=INK)
        d.rectangle([cx - 16, cy - 20, cx + 16, cy + 6], fill=accent)
        for i in range(3):
            wx = x + 12 + i * (w // 3)
            d.arc([wx, cy + 30, wx + 26, cy + 44], 0, 180, fill=BLUE, width=3)
    elif kind == "rocket":
        d.polygon([cx, y + 6, cx - 13, cy + 10, cx + 13, cy + 10], fill=accent)
        d.rectangle([cx - 13, cy + 10, cx + 13, cy + 30], fill=INK)
        d.polygon([cx - 6, cy + 30, cx, cy + 48, cx + 6, cy + 30], fill=RED)
        d.ellipse([cx - 5, cy - 6, cx + 5, cy + 4], fill=WHITE)
    elif kind == "ball":
        r = min(w, h) // 2 - 10
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=4)
        d.polygon([cx, cy - 10, cx + 10, cy - 3, cx + 6, cy + 9, cx - 6, cy + 9,
                   cx - 10, cy - 3], fill=accent)
    elif kind == "coin":
        r = min(w, h) // 2 - 8
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=5)
        f = font(F_SERIF, r)
        d.text((cx, cy - 2), "$", font=f, fill=GOLD, anchor="mm")
    elif kind == "wave":
        for i in range(3):
            yy = y + 14 + i * (h - 24) // 2
            d.arc([x + 8, yy, x + w // 2, yy + 22], 180, 360, fill=BLUE, width=4)
            d.arc([x + w // 2, yy, x + w - 8, yy + 22], 180, 360, fill=TEAL,
                  width=4)
    elif kind == "crown":
        d.polygon([x + 14, y + h - 18, x + 14, y + 20, x + w // 3, y + 34,
                   cx, y + 12, x + 2 * w // 3, y + 34, x + w - 14, y + 20,
                   x + w - 14, y + h - 18], fill=GOLD)
    elif kind == "pill":
        d.rounded_rectangle([x + 16, cy - 13, x + w - 16, cy + 13], 13,
                            outline=INK, width=4)
        d.line([cx, cy - 13, cx, cy + 13], fill=INK, width=4)
        d.rectangle([x + 16, cy - 13, cx, cy + 13], fill=accent)
    elif kind == "vote":
        d.rectangle([x + 18, cy - 2, x + w - 18, y + h - 12], outline=INK, width=4)
        d.rectangle([x + w // 3, cy - 2, x + 2 * w // 3, cy + 5], fill=INK)
        d.rectangle([cx - 16, y + 8, cx + 16, cy - 6], fill=WHITE, outline=INK,
                    width=3)
        d.line([cx - 8, cy - 2, cx - 2, cy + 3], fill=accent, width=3)
        d.line([cx - 2, cy + 3, cx + 9, cy - 8], fill=accent, width=3)
    elif kind == "quake":
        pts = [(x + 12, y + 8), (cx - 8, cy - 6), (cx + 6, cy + 4),
               (x + w - 16, cy - 2)]
        d.line(pts, fill=RED, width=5)
        d.line([x + 8, y + h - 10, x + w - 8, y + h - 10], fill=INK, width=3)
    else:  # "burst" fallback: sun/star burst
        for a in range(0, 360, 30):
            import math
            rad = math.radians(a)
            d.line([cx, cy, cx + int(30 * math.cos(rad)),
                    cy + int(30 * math.sin(rad))], fill=accent, width=4)
        d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=accent)


# ------------------------------------------------------------------- panels
def badge(d, x, y, n):
    d.ellipse([x, y, x + 25, y + 25], fill=RED)
    d.text((x + 12.5, y + 12.5), str(n), font=font(F_SANS_B, 14), fill=WHITE,
           anchor="mm")


def panel(d, st, x, y, w, h, tier, n):
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=INK, width=2)
    colour = REGION_COLOUR[st["region"]]
    d.rectangle([x, y, x + w, y + 5], fill=colour)
    if tier == "hero":
        art(d, st["art"], x + 8, y + 12, w - 16, 96, colour)
        ty = y + 114
    elif tier == "medium":
        art(d, st["art"], x + 8, y + 10, w - 16, 62, colour)
        ty = y + 78
    else:  # small: giant stat instead of a scene
        f = font(F_SERIF, 33)
        d.text((x + w / 2, y + 28), st["stat"], font=f, fill=colour, anchor="mm")
        ty = y + 54
    badge(d, x + 8, ty, n)
    kx = x + 40
    d.text((kx, ty + 3), st["region"], font=font(F_SANS_B, 11), fill=colour)
    if tier == "small":  # compact: no source line, no body, tighter leading
        hf = font(F_SERIF, 14)
        hy = ty + 22
        for line in wrap(d, st["headline"], hf, w - 18)[:2]:
            d.text((x + 9, hy), line, font=hf, fill=INK)
            hy += 15
        return
    d.text((kx, ty + 16), st.get("src", ""), font=font(F_SANS, 9), fill=FAINT)
    hy = ty + 30
    hf = font(F_SERIF, 19 if tier == "hero" else 15)
    for line in wrap(d, st["headline"], hf, w - 18)[:3]:
        d.text((x + 9, hy), line, font=hf, fill=INK)
        hy += 21 if tier == "hero" else 17
    bf = font(F_SANS, 11.5 if tier == "hero" else 10.5)
    for line in wrap(d, st["body"], bf, w - 18)[:3 if tier == "hero" else 2]:
        d.text((x + 9, hy + 2), line, font=bf, fill=FAINT)
        hy += 14


# --------------------------------------------------------------------- map
MAP_ROWS = [
    "                                                              ",
    "    #####    ###                                              ",
    "  ######### #####          #####  #############               ",
    " ##########  ####         ##########################  ##      ",
    "  ########    ##          #######################  ####       ",
    "   ######                  ##################     ###         ",
    "    ####   ##               ################       #          ",
    "    ###   #####              #############                    ",
    "    ##    ######              ###########          #          ",
    "          #######              #########        #####         ",
    "          ######                #######        #######        ",
    "          #####                  #####          #####    ##   ",
    "          ####                    ###            ###   ###### ",
    "          ###                                                   ",
]
PINS = [  # (story number, col, row) on the dotted map
    (1, 44, 3), (2, 42, 5), (3, 11, 3), (4, 34, 4), (5, 30, 2),
    (6, 35, 5), (7, 9, 4), (8, 11, 7),
]


def dotted_map(d, x, y):
    f = font(F_SANS_B, 10)
    d.text((x, y), "WHERE IT HAPPENED", font=font(F_SANS_B, 11), fill=INK)
    cell = 7
    oy = y + 16
    for r, row in enumerate(MAP_ROWS):
        for c, ch in enumerate(row):
            if ch == "#":
                d.ellipse([x + c * cell, oy + r * cell, x + c * cell + 3,
                           oy + r * cell + 3], fill=FAINT)
    for n, c, r in PINS:
        px, py = x + c * cell, oy + r * cell
        d.ellipse([px - 7, py - 7, px + 8, py + 8], fill=RED)
        d.text((px, py), str(n), font=f, fill=WHITE, anchor="mm")


# ------------------------------------------------------------------- tables
NUMBERS = [  # (value, caption) - the day in six figures
    ("+17%", "Anthropic's first-day close on its Nasdaq debut"),
    ("-2.02%", "S&P 500: a fifth straight losing day on Wall Street"),
    ("-4.68%", "Nikkei 225 as Japan inflation hit a year high"),
    ("$3,596", "gold per ounce, a 14-month low, down 2.42%"),
    ("34", "gang suspects killed in a Haiti police raid"),
    ("€45bn", "the EU's proposed new loan for Ukraine"),
]
REGION_COUNTS = [("EUROPE", 7), ("ASIA", 10), ("AMERICAS", 7),
                  ("MIDDLE EAST", 3), ("AFRICA", 4), ("GLOBAL", 3)]
HEROES = [
    {"region": "ASIA", "art": "summit", "src": "Reuters",
     "headline": "Trump, Xi and Putin meet in Shenzhen",
     "body": "First trilateral summit agrees a four-point 'Declaration Toward "
             "Peace': no nuclear war, UN reform, energy supply."},
    {"region": "ASIA", "art": "globe", "src": "OneTurn",
     "headline": "World Court: Myanmar committed genocide",
     "body": "The ICJ's first genocide finding against a state. Some 10,000 "
             "Rohingya were killed in 2017; reparations ordered."},
    {"region": "AMERICAS", "art": "chip", "src": "BBC",
     "headline": "Anthropic's record IPO closes up 17%",
     "body": "Priced at $83, opened near $111.50, closed about $97: an $81bn "
             "raise, the largest IPO in history."},
]
MEDIUMS = [
    {"region": "MIDDLE EAST", "art": "missile", "src": "OneTurn",
     "headline": "Houthi missile hits Riyadh tower",
     "body": "PIF Tower windows blown out; a second missile and a drone "
             "were intercepted."},
    {"region": "EUROPE", "art": "quake", "src": "OpenChronicle",
     "headline": "Ukraine hits Kerch Bridge again",
     "body": "Third strike in four days halts rail traffic; partial "
             "collapse reported."},
    {"region": "MIDDLE EAST", "art": "ship", "src": "EGazette",
     "headline": "Tankers strike mines in Hormuz",
     "body": "Three tankers mined east of the strait; two carried 4M+ "
             "barrels of crude."},
    {"region": "AMERICAS", "art": "pill", "src": "PAHO",
     "headline": "US loses measles-free status",
     "body": "Gone after 26 years: 5,400+ cases and 10 deaths in the US "
             "this year."},
    {"region": "AMERICAS", "art": "burst", "src": "OneTurn",
     "headline": "Haiti raid kills 34 suspects",
     "body": "Police offensive in Martissant, Port-au-Prince, kills at "
             "least 34 gang suspects."},
]
SMALLS = [
    {"region": "GLOBAL", "stat": "1 LT-DAY",
     "headline": "Voyager 1 reaches one light-day from Earth"},
    {"region": "GLOBAL", "stat": "8 YRS",
     "headline": "BepiColombo finally reaches Mercury orbit"},
    {"region": "AMERICAS", "stat": "13 YRS",
     "headline": "GTA VI launches after a 13-year wait"},
    {"region": "EUROPE", "stat": "$190.4M",
     "headline": "Van Gogh sells for a record $190.4M"},
    {"region": "ASIA", "stat": "8",
     "headline": "Litton Das: record 8 dismissals"},
]
BRIEFS = [
    (14, "EUROPE", "Russian strikes kill five across Ukraine"),
    (15, "MIDDLE EAST", "Israel begins ground operation inside Gaza"),
    (16, "ASIA", "Bangladesh unrest kills four; Yunus home burned"),
    (17, "AFRICA", "Migrant boat sinks off Senegal; dozens missing"),
    (18, "ASIA", "Japan inflation hits year high; Nikkei -4.68%"),
    (19, "AMERICAS", "Hegseth signs military deal in Caracas"),
    (20, "EUROPE", "EU approves trade deal with Indonesia"),
    (21, "EUROPE", "Ukraine's allies unite in Berlin on talks"),
    (22, "EUROPE", "Denmark ratifies US Greenland security deal"),
    (23, "ASIA", "IAEA: North Korea expands uranium enrichment"),
    (24, "ASIA", "Russian Tu-95 bombers land in Vietnam"),
    (25, "AMERICAS", "Canada extends China tariff deal to 2028"),
    (26, "ASIA", "Philippines signs first FTA with Chile"),
    (27, "AFRICA", "Tanzania's Lissu convicted of sedition"),
    (28, "AFRICA", "Ethiopia and Eritrea mass troops on border"),
    (29, "AFRICA", "US group wins Kenya's Mrima Hill minerals deal"),
    (30, "ASIA", "Pakistan says 22 militants killed in raids"),
    (31, "EUROPE", "Drone attack injures 11 in Russia's Kursk"),
    (32, "GLOBAL", "Nearly 1 in 4 children live in conflict zones"),
    (33, "AMERICAS", "Fiona the hippo dies at Cincinnati Zoo"),
    (34, "ASIA", "Odisha evacuates as Cyclone Akvan nears"),
]
DATE_CHECK = ("Checked before printing: Cyclone Akvan had NOT made landfall "
              "on Thursday (that came Friday), and nor had the Kyiv barrage. "
              "The Shenzhen summit and Anthropic's debut both happened on "
              "Thursday itself. Nothing on this page is dated before "
              "19 November 2026.")
DECK = ("Shenzhen's peace declaration, a genocide ruling, the biggest IPO "
        "ever: one Thursday.")


# -------------------------------------------------------------------- page
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # kicker
    d.text((M, 22), "THE WORLD IN ONE DAY", font=font(F_SANS_B, 13), fill=RED)
    right = "34 STORIES · 6 REGIONS · EVERY ONE DATED THURSDAY 19 NOVEMBER 2026"
    d.text((W - M, 22), right, font=font(F_SANS_B, 13), fill=INK, anchor="ra")
    d.line([M, 42, W - M, 42], fill=INK, width=3)

    # masthead
    d.text((W / 2, 50), "Thursday 19 November 2026", font=font(F_SERIF, 57),
           fill=INK, anchor="ma")
    d.line([M, 116, W - M, 116], fill=INK, width=1)
    d.text((W / 2, 122), DECK, font=font(F_SERIF_I, 19), fill=FAINT, anchor="ma")

    # by-the-numbers strip
    y = 148
    cw6 = CW / 6
    d.rectangle([M, y, W - M, y + 58], fill=PAPER_D, outline=INK, width=2)
    for i, (val, cap) in enumerate(NUMBERS):
        cx = M + i * cw6
        if i:
            d.line([cx, y, cx, y + 58], fill=INK, width=1)
        d.text((cx + cw6 / 2, y + 6), val, font=font(F_SERIF, 25), fill=RED,
               anchor="ma")
        for j, line in enumerate(wrap(d, cap, font(F_SANS, 9.5), cw6 - 12)[:2]):
            d.text((cx + cw6 / 2, y + 36 + j * 11), line, font=font(F_SANS, 9.5),
                   fill=FAINT, anchor="ma")

    # region bar
    y = 214
    d.rectangle([M, y, W - M, y + 28], fill=INK)
    label = "   ·   ".join(f"{name} {n}" for name, n in REGION_COUNTS)
    d.text((W / 2, y + 6), label, font=font(F_SANS_B, 13.5), fill=WHITE,
           anchor="ma")

    # story panels
    gap = 10
    hw = (CW - 2 * gap) / 3
    for i, st in enumerate(HEROES):
        panel(d, st, M + i * (hw + gap), 252, hw, 234, "hero", i + 1)
    mw = (CW - 4 * gap) / 5
    for i, st in enumerate(MEDIUMS):
        panel(d, st, M + i * (mw + gap), 496, mw, 178, "medium", i + 4)
    for i, st in enumerate(SMALLS):
        panel(d, st, M + i * (mw + gap), 684, mw, 114, "small", i + 9)

    # briefs
    y = 810
    d.text((M, y), "ALSO ON THURSDAY 19 NOVEMBER — THE REST OF THE DAY",
           font=font(F_SANS_B, 13), fill=INK)
    d.line([M, y + 20, W - M, y + 20], fill=INK, width=1)
    colw = (CW - 2 * gap) / 3
    bf = font(F_SANS, 10.5)
    per = (len(BRIEFS) + 2) // 3
    for i, (n, region, text) in enumerate(BRIEFS):
        col, row = divmod(i, per)
        bx = M + col * (colw + gap)
        by = y + 28 + row * 15.5
        d.text((bx, by), f"{n}.", font=font(F_SANS_B, 10.5), fill=RED)
        line = fit_line(d, text, bf, colw - 24)
        d.text((bx + 22, by), line, font=bf, fill=INK)

    # bottom: full-width date check strip
    d.rectangle([M, 954, W - M, 998], outline=RED, width=2)
    d.text((M + 10, 960), "DATE CHECK", font=font(F_SANS_B, 12), fill=RED)
    for j, line in enumerate(wrap(d, DATE_CHECK, font(F_SANS, 10.5),
                                   CW - 130)[:2]):
        d.text((M + 108, 961 + j * 14), line, font=font(F_SANS, 10.5), fill=INK)
    d.text((W - M, 1004), "Sources credited per panel · Original artwork",
           font=font(F_SANS, 9.5), fill=FAINT, anchor="ra")

    img.save("entry.png")
    print("wrote entry.png")


if __name__ == "__main__":
    build()
