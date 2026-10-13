"""Pixel figures: soldiers, horses, guns, wagons and flags (all facing right)."""
from pixel import *

SKIN, SKIN_D = (232, 186, 148), (196, 146, 110)
LEATHER, BOOTS = (34, 28, 24), (22, 18, 16)
WOOD, WOOD_D = (124, 80, 42), (88, 56, 30)
STEEL, STEEL_D = (176, 180, 186), (112, 116, 122)
BRASS = (222, 182, 70)
BRONZE, BRONZE_D = (190, 140, 62), (140, 96, 40)
IRON, IRON_D = (78, 80, 86), (50, 52, 56)
CANVAS, CANVAS_D = (236, 230, 210), (196, 188, 166)
WHITE, RED, BLUE, NAVY = (240, 240, 236), (196, 34, 40), (36, 62, 140), (24, 34, 80)

# ------------------------------------------------------------------ uniforms

def uniform(hat, hat_d, coat, coat_d, trousers, trousers_d, trim=BRASS, extra=None):
    p = {"H": hat, "h": hat_d, "C": coat, "c": coat_d, "T": trousers, "t": trousers_d, "Y": trim,
         "S": SKIN, "s": SKIN_D, "B": LEATHER, "K": BOOTS, "R": WOOD, "M": STEEL, "m": STEEL_D,
         "W": (232, 230, 220), "L": (150, 62, 52), "G": (176, 156, 112), "N": RED, "P": (20, 20, 22)}
    if extra:
        p.update(extra)
    return p

U_INF = uniform((36, 42, 74), (20, 24, 46), (40, 54, 102), (26, 36, 72), (112, 142, 192), (84, 110, 160))
U_IRON = uniform((26, 26, 30), (14, 14, 16), (40, 54, 102), (26, 36, 72), (112, 142, 192), (84, 110, 160))
U_SS = uniform((44, 74, 48), (28, 50, 32), (44, 76, 50), (30, 54, 34), (70, 92, 66), (52, 70, 48), trim=(60, 60, 50))
U_CAV = uniform((26, 26, 30), (14, 14, 16), (38, 52, 100), (26, 36, 72), (112, 142, 192), (84, 110, 160), trim=(224, 190, 60))
U_ART = uniform((36, 42, 74), (20, 24, 46), (40, 54, 102), (26, 36, 72), (112, 142, 192), (84, 110, 160), trim=(200, 44, 44))
U_GEN = uniform((22, 22, 26), (12, 12, 14), (30, 40, 80), (20, 28, 58), (40, 52, 96), (28, 38, 72), trim=(232, 196, 90))

C_GRAY = uniform((126, 126, 130), (92, 92, 98), (132, 132, 138), (100, 100, 108), (118, 116, 112), (92, 90, 86), extra={"L": (120, 110, 96)})
C_BUTT = uniform((112, 92, 62), (82, 66, 44), (160, 128, 82), (126, 100, 62), (140, 116, 76), (110, 90, 58))
C_MIX = uniform((96, 84, 66), (70, 60, 46), (132, 132, 138), (100, 100, 108), (150, 124, 82), (118, 96, 62))
C_CAV = uniform((24, 24, 26), (14, 14, 16), (130, 130, 136), (98, 98, 106), (110, 108, 104), (84, 82, 78), trim=(226, 192, 64))
C_ART = uniform((126, 126, 130), (92, 92, 98), (132, 132, 138), (100, 100, 108), (118, 116, 112), (92, 90, 86), trim=(200, 44, 44))
C_GEN = uniform((150, 146, 136), (110, 106, 98), (136, 138, 146), (104, 106, 114), (118, 120, 128), (90, 92, 100), trim=(232, 196, 90))

N_INF = uniform((30, 28, 26), (16, 16, 14), (116, 90, 62), (86, 66, 44), (100, 100, 100), (76, 76, 76))  # neutral militia

# ------------------------------------------------------------------ hats (drawn on top of the head; head top is row 0)

HATS = {
    "kepi":   (["..HHH..", "..HHHH.", "..hhhhh"], -3),
    "hardee": (["...HHH.", "...HHH.", "..HHHH.", ".hhhhhhh"], -4),
    "slouch": (["..HHH..", ".hhhhhhh"], -2),
    "plumed": (["P......", "PPHHH..", ".hhhhhhh"], -3),
    "bare":   ([], 0),
}

# ------------------------------------------------------------------ bodies (row 0 = top of face)

STAND = [  # shoulder arms - rifle carried upright at the right side
    "...SSs..M",
    "...SSS..M",
    "..LCCCC.R",
    ".LCCYCCSR",
    ".CCCYCC.R",
    ".C.CYCC.R",
    ".S.BBBB.R",
    "...CCCC..",
    "...TTTt..",
    "...TT.T..",
    "...TT.T..",
    "...Tt.T..",
    "..KK..KK.",
]
AIM = [  # standing, firing to the right
    "...SSs.........",
    "...SSSRRRRRMMMMM",
    "..CCCSSR........",
    ".CCCCCC.........",
    ".CCYCCc.........",
    "..BBBB..........",
    "..CCCC..........",
    "..TTTt..........",
    "..TT.TT.........",
    "..T...T.........",
    ".TT...TT........",
    ".KK...KK........",
]
CHARGE = [  # bayonet leveled, stepping forward
    "...SSs..........",
    "...SSS..........",
    "..CCCCSRRRRRMMMMM",
    ".CCCYCSR........",
    ".CCCYCc.........",
    "..BBBB..........",
    "..CCCC..........",
    "..TTTt..........",
    ".TT..TT.........",
    "TT....TT........",
    "KK.....KK.......",
]
KNEEL = [  # kneeling, firing
    "...SSs..........",
    "...SSSRRRRRMMMMMM",
    "..CCCSSR.........",
    ".CCCCCC..........",
    ".CCYCCc..........",
    "..BBBB...........",
    "..CCTTTTT........",
    "..TT....T........",
    ".KTT....T........",
    ".KKK....KK.......",
]
BEARER = [  # colour bearer: flag staff held upright in front
    "...SSs..F",
    "...SSS..F",
    "..LCCCC.F",
    ".LCCYCCSF",
    ".CCCYCC.F",
    ".C.CYCC.F",
    ".S.BBBB.F",
    "...CCCC.F",
    "...TTTt..",
    "...TT.T..",
    "...TT.T..",
    "...Tt.T..",
    "..KK..KK.",
]
GUNNER = [  # artilleryman with rammer
    "...SSs.......",
    "...SSS.......",
    "..CCCCSRRRRRRG",
    ".CCCYCS......",
    ".CCCYCC......",
    "..BBBB.......",
    "..CCCC.......",
    "..TTTt.......",
    "..TT.TT......",
    "..T...T......",
    ".KK...KK.....",
]
DIGGER = [  # pioneer with a shovel
    "...SSs.....",
    "...SSS.....",
    "..CCCCS....",
    ".CCCYCSR...",
    ".CCCYCC.R..",
    "..BBBB...R.",
    "..CCCC....R",
    "..TTTt...MMM",
    "..TT.TT..MM",
    "..T...T....",
    ".KK...KK...",
]
RIDER = [  # seated on a horse; row 7 sits on the horse's back
    "...SSs.",
    "...SSS.",
    "..CCCCS",
    ".CCCYCS",
    ".CCCYC.",
    ".BBBBB.",
    "..CTTT.",
    "..TTTT.",
    "...TT..",
    "...KK..",
]
HORSE = [
    "...............ee.",
    "..............nHH.",
    "............nnHHHHs",
    "...........nHHH..ss",
    "..nnHHHHHHHHHH.....",
    ".HHHHHHHHHHHHH.....",
    "tHHHHHHHHHHHHh.....",
    "t.hHHHHHHHHHh......",
    "t.Hh.H....Hh.H.....",
    "..Hh.H....Hh.H.....",
    "..H..H....H..H.....",
    "..k..k....k..k.....",
]
HORSE_COLORS = {
    "bay": {"H": (122, 72, 40), "h": (92, 54, 30), "n": (30, 24, 20), "t": (30, 24, 20), "e": (92, 54, 30), "s": (60, 40, 26), "k": (30, 26, 22)},
    "dark": {"H": (70, 46, 30), "h": (50, 32, 22), "n": (22, 18, 16), "t": (22, 18, 16), "e": (50, 32, 22), "s": (36, 26, 20), "k": (24, 20, 18)},
    "chestnut": {"H": (156, 84, 40), "h": (122, 64, 30), "n": (110, 54, 24), "t": (110, 54, 24), "e": (122, 64, 30), "s": (80, 46, 26), "k": (40, 30, 24)},
    "gray": {"H": (196, 196, 190), "h": (156, 156, 150), "n": (120, 120, 116), "t": (120, 120, 116), "e": (156, 156, 150), "s": (110, 110, 106), "k": (60, 58, 56)},
    "mule": {"H": (110, 90, 72), "h": (84, 68, 54), "n": (60, 48, 38), "t": (60, 48, 38), "e": (84, 68, 54), "s": (70, 56, 44), "k": (40, 34, 28)},
}


def soldier(img, x, y, pal, pose=STAND, hat="kepi", flip=False, weapon=None):
    """(x, y) = top-left of the face. Returns nothing; draws in place."""
    p = dict(pal)
    if weapon == "scoped":
        p["M"] = STEEL_D
    template(img, x, y, pose, p, flip)
    rows, dy = HATS[hat]
    if rows:
        pose_w = max(len(r) for r in pose)
        hat_w = max(len(r) for r in rows)
        template(img, x + (pose_w - hat_w if flip else 0), y + dy, rows, p, flip)
    if weapon == "scoped":  # telescope sight along the barrel
        for i in range(6):
            put(img, x + 8 + i, y, (40, 40, 44))


def horse(img, x, y, coat="bay", flip=False):
    template(img, x, y, HORSE, HORSE_COLORS[coat], flip)


def rider(img, x, y, pal, hat="slouch", coat="bay", weapon=None, flip=False):
    """(x, y) = top-left of the horse template."""
    horse(img, x, y, coat, flip)
    rx = x + 6
    template(img, rx, y - 3, RIDER, pal)
    rows, dy = HATS[hat]
    template(img, rx, y - 3 + dy, rows, pal)
    # saddle cloth
    rect(img, x + 5, y + 4, 5, 1, pal["C"])
    if weapon == "saber":
        line(img, rx + 7, y - 1, rx + 11, y - 7, STEEL)
    elif weapon == "carbine":
        line(img, rx + 6, y + 0, rx + 12, y - 1, WOOD)
        put(img, rx + 12, y - 1, STEEL_D); put(img, rx + 13, y - 1, STEEL_D)
    elif weapon == "glass":
        rect(img, rx + 6, y - 2, 3, 1, BRASS)


# ------------------------------------------------------------------ flags

def flag(img, x, y, kind, pole_len=14, pole=WOOD_D):
    """x, y = top of the pole; the flag flies to the right."""
    for j in range(pole_len):
        put(img, x, y + j, pole)
    fx, fy = x + 1, y
    if kind == "us":
        for j in range(6):
            rect(img, fx, fy + j, 9, 1, RED if j % 2 == 0 else WHITE)
        rect(img, fx, fy, 4, 3, NAVY)
        put(img, fx + 1, fy + 1, WHITE); put(img, fx + 3, fy + 1, WHITE)
    elif kind == "anv":  # red field, blue saltire, white stars
        rect(img, fx, fy, 7, 7, RED)
        for i in range(7):
            put(img, fx + i, fy + i, BLUE); put(img, fx + 6 - i, fy + i, BLUE)
        put(img, fx + 3, fy + 3, WHITE); put(img, fx + 1, fy + 1, WHITE); put(img, fx + 5, fy + 5, WHITE)
        put(img, fx + 5, fy + 1, WHITE); put(img, fx + 1, fy + 5, WHITE)
    elif kind == "texas":  # lone star
        rect(img, fx, fy, 3, 6, BLUE)
        put(img, fx + 1, fy + 2, WHITE); put(img, fx + 1, fy + 3, WHITE)
        rect(img, fx + 3, fy, 6, 3, WHITE)
        rect(img, fx + 3, fy + 3, 6, 3, RED)
    elif kind == "guidon_us":
        for j in range(5):
            rect(img, fx, fy + j, 7, 1, RED if j % 2 == 0 else WHITE)
        rect(img, fx, fy, 3, 3, NAVY)
        put(img, fx + 6, fy + 2, (0, 0, 0, 0)); put(img, fx + 5, fy + 2, (0, 0, 0, 0))
    elif kind == "guidon_cs":
        rect(img, fx, fy, 7, 5, RED)
        for i in range(5):
            put(img, fx + i, fy + i, BLUE); put(img, fx + 4 - i, fy + i, BLUE)
        put(img, fx + 6, fy + 2, (0, 0, 0, 0)); put(img, fx + 5, fy + 2, (0, 0, 0, 0))
    elif kind == "regimental":  # dark blue state colour with gold eagle hint
        rect(img, fx, fy, 8, 6, NAVY)
        rect(img, fx + 3, fy + 2, 2, 2, BRASS)
    elif kind == "hospital":
        rect(img, fx, fy, 7, 5, (230, 200, 40))
        rect(img, fx + 2, fy + 1, 1, 3, (30, 120, 50)); rect(img, fx + 4, fy + 1, 1, 3, (30, 120, 50)); put(img, fx + 3, fy + 2, (30, 120, 50))
    elif kind == "ambulance":
        rect(img, fx, fy, 7, 5, (40, 140, 60))
        rect(img, fx + 1, fy + 1, 5, 3, (230, 200, 40))
    elif kind == "neutral":
        rect(img, fx, fy, 8, 6, (150, 40, 36))
        rect(img, fx, fy + 2, 8, 2, (220, 200, 160))
    elif kind == "artillery_us":
        rect(img, fx, fy, 7, 5, RED)
        line(img, fx + 1, fy + 1, fx + 5, fy + 3, BRASS); line(img, fx + 1, fy + 3, fx + 5, fy + 1, BRASS)


# ------------------------------------------------------------------ guns and wagons

def wheel(img, cx, cy, r=4, wood=WOOD, hub=IRON_D):
    import math
    ring(img, cx, cy, r, wood)
    ring(img, cx, cy, r - 0.6, wood)
    for a in (0, 45, 90, 135):
        import math
        dx, dy = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
        line(img, cx - dx, cy - dy, cx + dx, cy + dy, WOOD_D)
    disc(img, cx, cy, 1, hub)


def cannon(img, x, y, kind="napoleon", carriage=(78, 92, 58)):
    """x, y = ground point under the wheel. Muzzle points right."""
    cx, cy = x, y - 5
    # trail resting on the ground behind the gun
    line(img, cx + 1, cy - 1, cx - 12, y, carriage)
    line(img, cx + 1, cy, cx - 11, y, shade(carriage, 0.7))
    line(img, cx + 2, cy - 2, cx - 2, cy - 1, carriage)
    by = cy - 5  # top row of the barrel
    if kind == "napoleon":      # bronze, 3 px thick, swelling at the muzzle
        rect(img, cx - 4, by, 18, 3, BRONZE)
        rect(img, cx - 4, by + 2, 18, 1, BRONZE_D)
        rect(img, cx + 12, by - 1, 3, 5, BRONZE)
        rect(img, cx - 6, by + 1, 2, 1, BRONZE_D)      # cascabel knob
        rect(img, cx - 2, by, 12, 1, shade(BRONZE, 1.3))
    elif kind == "ordnance":    # wrought iron, slim and smooth
        rect(img, cx - 4, by, 9, 3, IRON)
        rect(img, cx + 5, by, 11, 2, IRON)
        rect(img, cx - 4, by, 18, 1, shade(IRON, 1.4))
        rect(img, cx - 6, by + 1, 2, 1, IRON_D)
    elif kind == "parrott":     # cast iron with a heavy band around the breech
        rect(img, cx - 4, by, 20, 2, IRON)
        rect(img, cx - 4, by, 20, 1, shade(IRON, 1.4))
        rect(img, cx - 5, by - 1, 5, 4, IRON_D)
        rect(img, cx - 5, by - 1, 5, 1, shade(IRON_D, 1.5))
    elif kind == "whitworth":   # very long, thin English breech-loader
        rect(img, cx - 4, by, 24, 2, IRON)
        rect(img, cx + 8, by, 12, 1, shade(IRON, 1.4))
        rect(img, cx - 6, by - 1, 4, 4, (60, 62, 68))
        rect(img, cx - 8, by + 1, 2, 1, BRASS)
    wheel(img, cx, cy, 5)


def limber(img, x, y, carriage=(78, 92, 58)):
    rect(img, x - 4, y - 8, 8, 4, carriage)
    rect(img, x - 4, y - 8, 8, 1, shade(carriage, 1.2))
    wheel(img, x, y - 4, 4)


def wagon(img, x, y, cover=CANVAS, body=WOOD, kind="supply"):
    """x, y = ground below rear wheel."""
    rect(img, x - 4, y - 9, 16, 4, body)
    rect(img, x - 4, y - 9, 16, 1, shade(body, 1.2))
    if kind == "supply":
        for i in range(16):
            h = 6 if 2 < i < 13 else 5
            rect(img, x - 4 + i, y - 9 - h, 1, h, cover if i % 5 else CANVAS_D)
    else:  # ambulance: boxy body
        rect(img, x - 3, y - 15, 12, 6, cover)
        rect(img, x - 3, y - 15, 12, 1, CANVAS_D)
    wheel(img, x - 1, y - 4, 4)
    wheel(img, x + 10, y - 3, 3)
    line(img, x + 12, y - 7, x + 18, y - 7, WOOD_D)  # tongue


def finish(img, shadow_box=None):
    """Outline and drop shadow for a unit sprite."""
    outline(img)
    if shadow_box:
        cx, cy, rx, ry = shadow_box
        img = shadow(img, cx, cy, rx, ry)
    return img
