"""Tile overlays (64x56, drawn over Grassland/Plains) for the HexaRealm tileset; FantasyHex gets 32x28 downscales."""
import random
from figures import *

TW, TH = 64, 56
HEX = [(16, 1), (48, 1), (63, 29), (49, 55), (15, 55), (1, 29)]

GRASS_HI, GRASS, GRASS_D = (134, 174, 86), (108, 148, 70), (78, 112, 52)
LEAF, LEAF_HI, LEAF_D = (52, 104, 46), (78, 136, 60), (34, 74, 34)
PINE, PINE_D = (40, 86, 50), (26, 60, 36)
ROCK, ROCK_HI, ROCK_D = (132, 130, 124), (172, 170, 162), (88, 86, 82)
BRICK, BRICK_D = (156, 70, 50), (118, 50, 36)
ROOF, ROOF_D = (70, 62, 60), (46, 40, 40)
STONE_HOUSE = (172, 164, 146)
DIRT, DIRT_D = (128, 98, 64), (92, 70, 46)
WHEAT, WHEAT_D, WHEAT_HI = (214, 182, 82), (176, 142, 56), (238, 214, 124)
GOLD = (250, 206, 60)


def tile():
    return new(TW, TH)


def inside(x, y):
    from pixel import Image
    # point-in-hex for the HexaRealm footprint
    poly = HEX
    inside_ = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside_ = not inside_
        j = i
    return inside_


def clip(img):
    px = img.load()
    for x in range(TW):
        for y in range(TH):
            if px[x, y][3] and not inside(x + 0.5, y + 0.5):
                px[x, y] = (0, 0, 0, 0)
    return img


def mound(img, cx, cy, rx, ry, base=GRASS, rocky=False):
    """A hill drawn as a soft, top-left lit swelling that fades into the base terrain at its edge."""
    for x in range(int(cx - rx - 1), int(cx + rx + 2)):
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            dx, dy = (x - cx) / rx, (y - cy) / ry
            dd = dx * dx + dy * dy
            if dd > 1:
                continue
            light = -dx * 0.5 - dy * 0.8           # lit from the top-left
            c = base
            if light > 0.45:
                c = shade(base, 1.18)
            elif light < -0.45:
                c = shade(base, 0.8)
            if rocky and random.random() < 0.10:
                c = ROCK if light > 0 else ROCK_D
            alpha = 255 if dd < 0.6 else int(255 * (1 - dd) / 0.4)
            put(img, x, y, (*c, max(alpha, 40)))


def tree(img, x, y, r=3, kind="leaf", fruit=None):
    if kind == "pine":
        for i in range(r + 2):
            rect(img, x - i // 2, y - (r + 2) + i, (i // 2) * 2 + 1, 1, PINE if i % 2 else PINE_D)
        put(img, x, y + 1, WOOD_D)
        return
    disc(img, x, y + r + 1, r, (0, 0, 0, 60))            # shadow
    put(img, x, y + r, WOOD_D); put(img, x, y + r + 1, WOOD_D)
    disc(img, x, y, r, LEAF_D)
    disc(img, x - 0.5, y - 0.5, r - 0.8, LEAF)
    put(img, x - 1, y - 1, LEAF_HI)
    if fruit:
        put(img, x + 1, y, fruit); put(img, x - 1, y + 1, fruit)


def rock(img, x, y, r):
    ellipse(img, x + 1, y + 1, r + 0.5, r * 0.7 + 0.5, (0, 0, 0, 70))
    ellipse(img, x, y, r, r * 0.75, ROCK_D)
    ellipse(img, x - 0.5, y - 0.5, r - 0.6, r * 0.75 - 0.6, ROCK)
    put(img, x - r // 2, y - r // 2, ROCK_HI)


def house(img, x, y, w=6, h=4, wall=BRICK, roof=ROOF, windows=True):
    """(x, y) = bottom-left corner."""
    rect(img, x + 1, y + 1, w, 1, (0, 0, 0, 70))
    rect(img, x, y - h, w, h, wall)
    rect(img, x + w - 1, y - h, 1, h, shade(wall, 0.8))
    for i in range(3):
        rect(img, x - 1 + i, y - h - 1 - i, w + 2 - 2 * i, 1, roof if i % 2 == 0 else ROOF_D)
    if windows:
        for wx in range(x + 1, x + w - 1, 2):
            put(img, wx, y - h + 1, (230, 220, 160))
    put(img, x + w // 2, y - 1, (60, 40, 30))


def barn(img, x, y, w=8, h=5):
    house(img, x, y, w, h, wall=(170, 50, 40), roof=(90, 90, 88), windows=False)
    rect(img, x + w // 2 - 1, y - 3, 2, 3, (90, 30, 24))


def tent(img, x, y):
    for i in range(5):
        rect(img, x - i, y - 4 + i, i * 2 + 1, 1, CANVAS)
        put(img, x + i, y - 4 + i, CANVAS_D)
    put(img, x, y, (90, 80, 60))


def fence(img, x0, y0, x1, y1):
    line(img, x0, y0, x1, y1, (150, 120, 80))
    n = max(abs(x1 - x0), abs(y1 - y0))
    for k in range(0, n + 1, 3):
        put(img, x0 + (x1 - x0) * k // max(n, 1), y0 + (y1 - y0) * k // max(n, 1) - 1, (110, 86, 56))


def wall(img, pts):
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        n = max(abs(x1 - x0), abs(y1 - y0))
        for k in range(n + 1):
            x = x0 + (x1 - x0) * k / max(n, 1); y = y0 + (y1 - y0) * k / max(n, 1)
            put(img, x, y + 1, (0, 0, 0, 80))
            put(img, x, y, ROCK if (k % 3) else ROCK_HI)
            put(img, x, y - 1, ROCK_D if k % 2 else ROCK)


def key_marker(img):
    """Small gold star in the top-right corner: KEY TERRAIN for the Hold the Field victory."""
    star = new(TW, TH)
    cx, cy = 50, 9
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if abs(dx) + abs(dy) <= 3 and not (abs(dx) == 3 and dy > 0):
                put(star, cx + dx, cy + dy, GOLD)
    put(star, cx, cy, (255, 240, 160))
    outline(star, (60, 40, 10))
    img.alpha_composite(star)


def small_cannon(img, x, y):
    rect(img, x, y - 3, 6, 1, IRON)
    disc(img, x + 1, y - 1, 1.5, WOOD)


# ------------------------------------------------------------------ features

def f_ridge():
    random.seed(1)
    img = tile()
    for x in range(4, 60):
        for y in range(14, 44):
            dx, dy = (x - 32) / 28, (y - 30) / 11
            dd = dx * dx + dy * dy
            if dd > 1:
                continue
            if dy < -0.15:
                put(img, x, y, (*GRASS_HI, 110))
            elif dy > 0.35:
                put(img, x, y, (*GRASS_D, 120))
    for _ in range(14):
        x, y = random.randint(10, 54), random.randint(20, 30)
        put(img, x, y, (*shade(GRASS_HI, 1.1), 200))
    return clip(img)


def f_orchard():
    img = tile()
    for row in range(3):
        for col in range(4):
            x = 14 + col * 11 + (5 if row % 2 else 0)
            y = 14 + row * 12
            if inside(x, y) and x < 56:
                tree(img, x, y, 3, fruit=(220, 120, 90))
    return clip(img)


def f_boulders():
    img = tile()
    for x, y, r in ((22, 20, 4), (38, 18, 3), (30, 32, 5), (16, 36, 3), (45, 34, 4), (40, 44, 2), (26, 44, 3)):
        rock(img, x, y, r)
    return clip(img)


def f_town(square=False):
    img = tile()
    rect(img, 6, 29, 52, 2, (*DIRT, 200))       # main street
    rect(img, 30, 6, 2, 46, (*DIRT, 200))       # cross street
    spots = [(9, 26, BRICK), (19, 25, STONE_HOUSE), (36, 26, BRICK), (46, 25, (190, 180, 160)),
             (12, 45, (190, 180, 160)), (22, 46, BRICK), (36, 46, BRICK), (45, 45, STONE_HOUSE), (20, 14, BRICK), (38, 14, STONE_HOUSE)]
    for x, y, c in spots:
        if square and 24 <= x <= 40 and 20 <= y <= 40:
            continue
        house(img, x, y, 7, 5, wall=c)
    if square:
        rect(img, 25, 25, 12, 10, (186, 176, 150))
        tree(img, 31, 28, 2)
        house(img, 41, 38, 9, 7, wall=BRICK)          # courthouse
        rect(img, 44, 25, 2, 6, (230, 230, 230))       # cupola
    else:
        rect(img, 47, 8, 2, 8, (230, 230, 226)); put(img, 47, 7, (230, 230, 226))   # church steeple
        house(img, 44, 18, 7, 4, wall=(230, 228, 220))
    return clip(img)


def f_stone_wall():
    img = tile()
    wall(img, [(6, 36), (24, 33), (40, 30), (58, 27)])
    for x, y in ((14, 26), (34, 23), (48, 40), (20, 44)):
        put(img, x, y, GRASS_HI); put(img, x + 1, y - 1, GRASS_HI)
    return clip(img)


def f_farmstead():
    img = tile()
    house(img, 14, 30, 8, 6, wall=STONE_HOUSE)
    barn(img, 32, 33, 13, 8)
    fence(img, 8, 44, 54, 40)
    tree(img, 50, 22, 3)
    return clip(img)


def f_railroad_cut():
    img = tile()
    for t in range(0, 101):
        x = 2 + t * 0.6
        y = 40 - t * 0.2
        for w in range(-5, 6):
            c = DIRT_D if abs(w) <= 2 else DIRT
            if abs(w) == 5:
                c = (150, 120, 80)
            put(img, x, y + w, c)
    rock(img, 20, 31, 2); rock(img, 44, 27, 2)
    return clip(img)


def f_breastworks():
    img = tile()
    for i, (x, y) in enumerate(((10, 36), (20, 33), (30, 31), (40, 30), (50, 31))):
        rect(img, x, y + 2, 11, 2, DIRT_D)
        rect(img, x, y, 11, 2, WOOD if i % 2 else WOOD_D)
        put(img, x, y, (170, 130, 80))
    return clip(img)


def city_center(flag_kind=None):
    img = tile()
    rect(img, 12, 26, 40, 2, (*DIRT, 180))
    for x, y in ((14, 22), (24, 20), (34, 21), (44, 23), (18, 34), (30, 35), (42, 34), (24, 45), (36, 46)):
        tent(img, x, y)
    wagon_img = new(64, 56)
    wagon(wagon_img, 46, 50)
    img.alpha_composite(wagon_img.resize((64, 56)), (0, 0))
    if flag_kind:
        flag(img, 30, 4, flag_kind, pole_len=20)
    # camp fire smoke
    put(img, 20, 41, (230, 120, 40)); put(img, 20, 39, (200, 200, 200)); put(img, 21, 37, (220, 220, 220))
    return clip(img)


# ------------------------------------------------------------------ landmarks (natural wonders)

def nw_cemetery_hill(east=False):
    random.seed(3 if east else 2)
    img = tile()
    mound(img, 32, 30, 26, 18)
    if east:
        for x, y in ((18, 30), (30, 26), (42, 28)):
            rect(img, x - 2, y + 2, 9, 2, DIRT_D)     # lunettes
            small_cannon(img, x, y + 1)
        tree(img, 48, 40, 3)
    else:
        # the Evergreen Cemetery gatehouse
        rect(img, 24, 20, 4, 8, BRICK); rect(img, 34, 20, 4, 8, BRICK)
        rect(img, 24, 18, 14, 3, BRICK_D)
        rect(img, 28, 22, 6, 6, (60, 40, 30))
        for i in range(10):
            x, y = random.randint(14, 50), random.randint(30, 44)
            put(img, x, y, (236, 236, 228)); put(img, x, y - 1, (236, 236, 228))
        tree(img, 16, 26, 3); tree(img, 48, 30, 3)
    key_marker(img)
    return clip(img)


def nw_culps_hill():
    random.seed(4)
    img = tile()
    mound(img, 32, 30, 27, 20, base=(96, 132, 64))
    for x, y in ((22, 20), (32, 16), (42, 21), (16, 32), (48, 33), (26, 38), (38, 40), (30, 27)):
        tree(img, x, y, 3)
    for x, y in ((20, 26), (44, 28)):
        rock(img, x, y, 2)
    for i, x in enumerate(range(18, 46, 6)):           # Greene's breastworks
        rect(img, x, 30 - (i % 2), 6, 2, WOOD_D)
    key_marker(img)
    return clip(img)


def nw_little_round_top():
    random.seed(5)
    img = tile()
    mound(img, 32, 30, 25, 19, base=(118, 140, 82), rocky=True)
    for x, y, r in ((18, 34, 3), (24, 40, 4), (40, 38, 3), (14, 28, 2), (34, 44, 2)):
        rock(img, x, y, r)
    tree(img, 44, 22, 3); tree(img, 50, 30, 3)
    flag(img, 30, 10, "us", pole_len=12)              # the signal station on the summit
    key_marker(img)
    return clip(img)


def nw_big_round_top():
    random.seed(6)
    img = tile()
    mound(img, 32, 29, 29, 23, base=(90, 124, 60))
    for x, y in ((20, 16), (30, 11), (40, 15), (14, 26), (24, 24), (36, 22), (48, 26), (18, 36), (30, 34), (42, 36), (26, 44), (38, 46), (50, 38)):
        tree(img, x, y, 3)
    return clip(img)


def nw_devils_den():
    img = tile()
    for x, y, r in ((20, 24, 6), (34, 20, 5), (44, 30, 6), (26, 36, 7), (40, 44, 4), (14, 36, 3), (52, 40, 3)):
        rock(img, x, y, r)
    tree(img, 48, 18, 3)
    return clip(img)


def nw_the_angle():
    img = tile()
    wall(img, [(4, 40), (30, 34), (30, 18), (58, 14)])
    for x, y in ((38, 28), (44, 26), (41, 33), (48, 31), (45, 37)):   # the Copse of Trees
        tree(img, x, y, 3)
    key_marker(img)
    return clip(img)


def nw_peach_orchard():
    img = tile()
    for row in range(3):
        for col in range(4):
            x, y = 12 + col * 10 + (4 if row % 2 else 0), 16 + row * 11
            if inside(x, y):
                tree(img, x, y, 3, fruit=(246, 150, 120))
    house(img, 46, 46, 8, 5, wall=BRICK)
    return clip(img)


def nw_wheatfield():
    random.seed(7)
    img = tile()
    for x in range(4, 60):
        for y in range(6, 52):
            if inside(x, y) and random.random() < 0.65:
                c = random.choice((WHEAT, WHEAT, WHEAT_D, WHEAT_HI))
                put(img, x, y, c)
                if random.random() < 0.3:
                    put(img, x, y - 1, WHEAT_HI)
    fence(img, 8, 14, 56, 14)
    for x, y in ((10, 30), (54, 34)):
        tree(img, x, y, 3)
    return clip(img)


def nw_seminary():
    img = tile()
    house(img, 20, 38, 22, 12, wall=BRICK)
    rect(img, 29, 18, 4, 7, (236, 236, 230))          # the cupola Buford watched from
    rect(img, 28, 17, 6, 1, ROOF); put(img, 31, 15, ROOF); put(img, 31, 16, ROOF)
    tree(img, 12, 30, 3); tree(img, 50, 34, 3); tree(img, 48, 22, 2)
    return clip(img)


def nw_oak_hill():
    img = tile()
    mound(img, 32, 30, 26, 19)
    for x, y in ((20, 22), (40, 18), (48, 30)):
        tree(img, x, y, 4)
    small_cannon(img, 26, 34); small_cannon(img, 34, 36)
    return clip(img)


def nw_mcpherson():
    img = tile()
    for x in range(4, 60):
        for y in range(18, 40):
            dx, dy = (x - 32) / 28, (y - 29) / 10
            if dx * dx + dy * dy <= 1:
                put(img, x, y, (*(GRASS_HI if dy < 0 else GRASS_D), 110))
    barn(img, 24, 34, 14, 8)
    house(img, 42, 32, 7, 5, wall=STONE_HOUSE)
    fence(img, 6, 44, 58, 44)
    return clip(img)


def nw_barlows_knoll():
    img = tile()
    mound(img, 32, 30, 20, 14)
    tree(img, 26, 22, 3); tree(img, 38, 24, 3); tree(img, 32, 30, 3)
    return clip(img)


def nw_benners_hill():
    img = tile()
    mound(img, 32, 30, 24, 16)
    for x in (22, 32, 42):
        small_cannon(img, x, 30)
    return clip(img)


FEATURES = {
    "Ridge": f_ridge, "Orchard": f_orchard, "Boulders": f_boulders, "Town": f_town, "Stone Wall": f_stone_wall,
    "Farmstead": f_farmstead, "Railroad Cut": f_railroad_cut, "Breastworks": f_breastworks,
}
WONDERS = {
    "Cemetery Hill": nw_cemetery_hill, "East Cemetery Hill": lambda: nw_cemetery_hill(True), "Culp's Hill": nw_culps_hill,
    "Little Round Top": nw_little_round_top, "Big Round Top": nw_big_round_top, "Devil's Den": nw_devils_den,
    "The Angle": nw_the_angle, "Peach Orchard": nw_peach_orchard, "The Wheatfield": nw_wheatfield,
    "Lutheran Seminary": nw_seminary, "Oak Hill": nw_oak_hill, "McPherson's Ridge": nw_mcpherson,
    "Barlow's Knoll": nw_barlows_knoll, "Benner's Hill": nw_benners_hill, "Gettysburg": lambda: f_town(square=True),
}
CITY_CENTERS = {
    "City center-Civil War era": lambda: city_center(None),
    "City center-Union-Civil War era": lambda: city_center("us"),
    "City center-Confederacy-Civil War era": lambda: city_center("anv"),
}
