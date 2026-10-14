"""UI graphics: unit icons and portraits, nation icons, leader portraits, promotion, building and improvement icons."""
import math
from PIL import Image, ImageDraw, ImageFilter
from figures import *

# ------------------------------------------------------------------ unit icons (white silhouettes)

def _icon_canvas():
    return new(36, 36)


def icon_soldier(hat, pose=AIM, scoped=False):
    img = _icon_canvas()
    soldier(img, 6, 12, U_INF, pose, hat, weapon="scoped" if scoped else None)
    return img


def icon_rider(hat, saber=False, flag_kind=None, glass=False):
    img = _icon_canvas()
    if flag_kind:
        flag(img, 9, 2, flag_kind, pole_len=14)
    weapon = "saber" if saber else ("glass" if glass else None)
    rider(img, 6, 17, U_CAV, hat, "bay", weapon=weapon)
    return img


def icon_gun(kind):
    img = _icon_canvas()
    cannon(img, 14, 30, kind)
    return img


def icon_horse_gun():
    img = _icon_canvas()
    horse(img, 15, 10, "bay")
    cannon(img, 12, 33, "ordnance")
    return img


def icon_wagon(kind="supply", flag_kind=None):
    img = _icon_canvas()
    wagon(img, 6, 30, kind=kind)
    if flag_kind:
        flag(img, 6, 6, flag_kind, pole_len=12)
    return img


def icon_pioneer():
    img = _icon_canvas()
    line(img, 6, 30, 26, 6, WOOD); line(img, 7, 30, 27, 6, WOOD)        # shovel handle
    rect(img, 25, 3, 5, 6, STEEL)                                       # blade
    line(img, 8, 6, 28, 30, WOOD); line(img, 9, 6, 29, 30, WOOD)         # axe handle
    rect(img, 4, 3, 7, 5, STEEL)                                        # axe head
    return img


UNIT_ICONS = {
    "Infantry Brigade": lambda: icon_soldier("slouch"),
    "Union Infantry": lambda: icon_soldier("kepi"),
    "Iron Brigade": lambda: icon_soldier("hardee"),
    "Confederate Infantry": lambda: icon_soldier("slouch"),
    "Texas Brigade": lambda: icon_soldier("slouch", CHARGE),
    "Stonewall Brigade": lambda: icon_soldier("kepi", CHARGE),
    "Sharpshooters": lambda: icon_soldier("slouch", KNEEL),
    "US Sharpshooters": lambda: icon_soldier("kepi", KNEEL),
    "Confederate Sharpshooters": lambda: icon_soldier("slouch", KNEEL, scoped=True),
    "Cavalry Brigade": lambda: icon_rider("slouch"),
    "Union Cavalry": lambda: icon_rider("slouch", flag_kind="guidon_us"),
    "Michigan Cavalry Brigade": lambda: icon_rider("slouch", saber=True),
    "Confederate Cavalry": lambda: icon_rider("plumed", saber=True),
    "Napoleon Battery": lambda: icon_gun("napoleon"),
    "Union Napoleon Battery": lambda: icon_gun("napoleon"),
    "Confederate Napoleon Battery": lambda: icon_gun("napoleon"),
    "Rifled Battery": lambda: icon_gun("ordnance"),
    "Union Ordnance Rifles": lambda: icon_gun("ordnance"),
    "Confederate Parrott Rifles": lambda: icon_gun("parrott"),
    "Whitworth Battery": lambda: icon_gun("whitworth"),
    "Horse Artillery": icon_horse_gun,
    "US Horse Artillery": icon_horse_gun,
    "Stuart Horse Artillery": icon_horse_gun,
    "General": lambda: icon_rider("slouch", glass=True, flag_kind="neutral"),
    "Union General": lambda: icon_rider("slouch", glass=True, flag_kind="us"),
    "Confederate General": lambda: icon_rider("slouch", glass=True, flag_kind="anv"),
    "Supply Train": lambda: icon_wagon(),
    "Pioneers": icon_pioneer,
    "Field Hospital": lambda: icon_wagon("ambulance", "hospital"),
    "Ambulance Corps": lambda: icon_wagon("ambulance", "ambulance"),
}


def unit_icon(name):
    return smooth_icon(upscale(silhouette(UNIT_ICONS[name]()), 4), 100, 4)


def unit_portrait(sprite):
    """Full-colour portrait: the map sprite enlarged, on a transparent 128x128 canvas."""
    return fit_center(sprite, 128, 4)


def portrait_background():
    big = 512
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([8, 8, big - 8, big - 8], fill=(214, 196, 150, 255), outline=(70, 52, 30, 255), width=18)
    d.ellipse([40, 40, big - 40, big - 40], outline=(160, 136, 92, 255), width=6)
    return img.resize((128, 128), Image.LANCZOS)


# ------------------------------------------------------------------ vector helpers (white icons)

def vcanvas(n=400):
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def star_points(cx, cy, r, inner=0.38, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def finish_icon(img, size=100):
    return img.resize((size, size), Image.LANCZOS)


W8 = (255, 255, 255, 255)
CLEAR = (0, 0, 0, 0)


def nation_union():
    img, d = vcanvas()
    # the Union shield: a chief above thirteen vertical stripes
    shield = [(70, 60), (330, 60), (330, 220), (300, 290), (200, 350), (100, 290), (70, 220)]
    d.polygon(shield, fill=W8)
    for i in range(6):
        x = 92 + i * 40
        d.rectangle([x, 150, x + 16, 340], fill=CLEAR)
    d.polygon(shield, outline=W8, width=14)
    d.rectangle([70, 60, 330, 140], fill=W8)
    for i, x in enumerate((130, 200, 270)):
        d.polygon(star_points(x, 100, 26), fill=CLEAR)
    return finish_icon(img)


def nation_confederacy():
    img, d = vcanvas()
    d.ellipse([30, 30, 370, 370], outline=W8, width=18)
    d.polygon(star_points(200, 205, 110, 0.4), fill=W8)
    for i in range(13):
        a = math.radians(-90 + i * 360 / 13)
        d.polygon(star_points(200 + 140 * math.cos(a), 200 + 140 * math.sin(a), 15), fill=W8)
    return finish_icon(img)


def nation_adams_county():
    """The neutral city-state of the Gettysburg scenario: a keystone (Pennsylvania, the Keystone State) with a
    farmhouse roof cut out of it."""
    img, d = vcanvas()
    d.polygon([(60, 50), (340, 50), (290, 360), (110, 360)], fill=W8)
    d.polygon([(200, 120), (285, 200), (115, 200)], fill=CLEAR)      # roof
    d.rectangle([140, 200, 260, 300], fill=CLEAR)                     # walls
    d.rectangle([150, 205, 250, 295], fill=W8)
    d.rectangle([185, 235, 215, 295], fill=CLEAR)                     # door
    return finish_icon(img)


def leader_portrait(name):
    """Sepia 'carte de visite' style bust portraits."""
    n = 512
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    sepia_bg, frame = (206, 184, 140, 255), (64, 44, 26, 255)
    d.ellipse([24, 10, n - 24, n - 10], fill=sepia_bg)
    # vignette
    vig = Image.new("L", (n, n), 0)
    ImageDraw.Draw(vig).ellipse([60, 46, n - 60, n - 46], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(40))
    dark = Image.new("RGBA", (n, n), (120, 90, 56, 255))
    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).ellipse([24, 10, n - 24, n - 10], fill=255)
    mask = Image.composite(Image.new("L", (n, n), 0), mask, vig)
    img.paste(dark, (0, 0), mask.point(lambda v: int(v * 0.55)))
    d = ImageDraw.Draw(img)
    lee = name == "Robert E. Lee"
    coat = (128, 122, 110) if lee else (52, 44, 40)
    coat_d = shade(coat, 0.75)
    skin, skin_d = (226, 196, 160), (190, 156, 120)
    hair = (238, 236, 228) if lee else (120, 104, 86)
    beard = (244, 242, 236) if lee else (118, 100, 80)
    # shoulders and coat
    d.polygon([(70, 500), (110, 360), (200, 330), (312, 330), (402, 360), (442, 500)], fill=coat)
    d.polygon([(200, 330), (256, 470), (312, 330)], fill=coat_d)
    d.polygon([(226, 340), (256, 400), (286, 340)], fill=(236, 230, 214))          # shirt
    for i in range(4):                                                              # double-breasted buttons
        for x in (222, 290):
            d.ellipse([x - 6, 392 + i * 26 - 6, x + 6, 392 + i * 26 + 6], fill=(214, 182, 96))
    if lee:  # collar insignia: three stars
        for x in (150, 175, 200):
            d.polygon(star_points(x, 370, 9), fill=(214, 182, 96))
    else:    # major general's shoulder straps with two stars
        for x0 in (120, 330):
            d.rectangle([x0, 352, x0 + 62, 374], fill=(214, 182, 96))
            d.rectangle([x0 + 6, 356, x0 + 56, 370], fill=(30, 26, 26))
            for k in (18, 44):
                d.polygon(star_points(x0 + k, 363, 7), fill=(214, 182, 96))
    # neck and head
    d.rectangle([226, 290, 286, 340], fill=skin_d)
    d.ellipse([186, 128, 326, 312], fill=skin)
    d.ellipse([176, 200, 196, 244], fill=skin_d)                                    # ear
    d.ellipse([316, 200, 336, 244], fill=skin_d)
    # hair
    if lee:
        d.chord([182, 110, 330, 230], 180, 360, fill=hair)
        d.rectangle([182, 168, 198, 230], fill=hair); d.rectangle([314, 168, 330, 230], fill=hair)
    else:
        d.chord([186, 140, 326, 210], 180, 360, fill=skin)                          # high forehead
        d.rectangle([184, 170, 198, 228], fill=hair); d.rectangle([314, 170, 328, 228], fill=hair)
    # eyes, brows, nose
    for x in (228, 284):
        d.ellipse([x - 9, 202, x + 9, 212], fill=(60, 48, 40))
        d.line([x - 16, 192, x + 14, 190], fill=hair if lee else (90, 74, 60), width=6)
    d.polygon([(256, 206), (246, 252), (266, 252)], fill=skin_d)
    # beard and moustache
    d.chord([190, 214, 322, 336], 0, 180, fill=beard)
    d.polygon([(196, 250), (316, 250), (318, 290), (194, 290)], fill=beard)
    d.ellipse([224, 254, 288, 276], fill=beard)
    d.line([240, 272, 272, 272], fill=shade(beard, 0.6), width=4)
    if not lee:  # Meade's spectacles
        for x in (228, 284):
            d.ellipse([x - 18, 196, x + 18, 220], outline=(40, 36, 30), width=4)
        d.line([246, 206, 266, 206], fill=(40, 36, 30), width=4)
    # frame
    d.ellipse([24, 10, n - 24, n - 10], outline=frame, width=16)
    d.ellipse([46, 32, n - 46, n - 32], outline=(150, 120, 80, 255), width=4)
    # cut everything outside the oval
    cut = Image.new("L", (n, n), 0)
    ImageDraw.Draw(cut).ellipse([24, 10, n - 24, n - 10], fill=255)
    img.putalpha(Image.composite(img.split()[3], Image.new("L", (n, n), 0), cut))
    return img.resize((256, 256), Image.LANCZOS)


# ------------------------------------------------------------------ promotion icons (white, vector)

def pi_flag(d):
    d.rectangle([110, 60, 130, 360], fill=W8)
    d.polygon([(130, 70), (310, 110), (130, 200)], fill=W8)


def pi_shield(d):
    d.polygon([(90, 60), (310, 60), (310, 200), (200, 350), (90, 200)], fill=W8)


def pi_arrow(d):
    for off in (0, 110):
        d.polygon([(60 + off, 90), (160 + off, 200), (60 + off, 310), (110 + off, 310), (210 + off, 200), (110 + off, 90)], fill=W8)


def pi_tree(d):
    d.polygon([(200, 40), (330, 220), (70, 220)], fill=W8)
    d.polygon([(200, 120), (350, 300), (50, 300)], fill=W8)
    d.rectangle([180, 290, 220, 360], fill=W8)


def pi_boot(d):
    d.polygon([(140, 50), (230, 50), (230, 250), (330, 280), (340, 340), (120, 340), (130, 250)], fill=W8)


def pi_chevrons(d):
    for i in range(3):
        y = 90 + i * 80
        d.polygon([(60, y + 60), (200, y), (340, y + 60), (340, y + 110), (200, y + 50), (60, y + 110)], fill=W8)


def pi_bayonet(d):
    d.polygon([(70, 330), (300, 100), (320, 80), (310, 120), (90, 350)], fill=W8)
    d.rectangle([60, 300, 120, 320], fill=W8)


def pi_cross(d):
    d.rectangle([160, 60, 240, 340], fill=W8)
    d.rectangle([60, 160, 340, 240], fill=W8)


def pi_carbine(d):
    d.polygon([(40, 230), (300, 160), (360, 150), (360, 170), (300, 185), (150, 230), (120, 290), (60, 290)], fill=W8)


def pi_sabers(d):
    for flip in (False, True):
        pts = [(80, 320), (300, 70), (320, 60), (310, 85), (100, 335)]
        if flip:
            pts = [(400 - x, y) for x, y in pts]
        d.polygon(pts, fill=W8)
        hx = 80 if not flip else 320
        d.ellipse([hx - 25, 300, hx + 25, 350], outline=W8, width=12)


def pi_eye(d):
    d.chord([40, 110, 360, 290], 180, 360, fill=W8)
    d.chord([40, 110, 360, 290], 0, 180, fill=W8)
    d.ellipse([140, 140, 260, 260], fill=CLEAR)
    d.ellipse([175, 175, 225, 225], fill=W8)


def pi_crosshair(d):
    d.ellipse([60, 60, 340, 340], outline=W8, width=30)
    d.rectangle([185, 30, 215, 370], fill=W8)
    d.rectangle([30, 185, 370, 215], fill=W8)


def pi_balls(d):
    for (x, y) in ((130, 200), (270, 200), (200, 90), (200, 310)):
        d.ellipse([x - 62, y - 62, x + 62, y + 62], fill=W8)


def pi_cannon(d):
    d.polygon([(60, 170), (330, 120), (340, 160), (70, 230)], fill=W8)
    d.ellipse([110, 180, 250, 320], outline=W8, width=26)
    d.line([180, 250, 40, 340], fill=W8, width=24)


def pi_range(d):
    d.arc([40, 80, 360, 420], 200, 340, fill=W8, width=24)
    d.polygon([(320, 150), (370, 230), (290, 220)], fill=W8)
    d.ellipse([20, 260, 80, 320], fill=W8)


def pi_rope(d):
    d.ellipse([90, 60, 310, 280], outline=W8, width=30)
    d.line([200, 280, 200, 360], fill=W8, width=30)
    d.line([200, 360, 300, 360], fill=W8, width=30)


def pi_hillflag(d):
    d.chord([20, 220, 380, 500], 180, 360, fill=W8)
    d.rectangle([190, 60, 210, 250], fill=W8)
    d.polygon([(210, 60), (330, 95), (210, 140)], fill=W8)


def pi_union_general(d):
    d.rectangle([40, 140, 360, 260], outline=W8, width=22)
    for x in (130, 270):
        d.polygon(star_points(x, 200, 48), fill=W8)


def pi_confed_general(d):
    d.arc([40, 60, 360, 380], 110, 250, fill=W8, width=26)
    d.arc([40, 60, 360, 380], -70, 70, fill=W8, width=26)
    for i in range(6):
        a = math.radians(120 + i * 22)
        d.ellipse([200 + 160 * math.cos(a) - 22, 220 + 160 * math.sin(a) - 22, 200 + 160 * math.cos(a) + 22, 220 + 160 * math.sin(a) + 22], fill=W8)
        a = math.radians(60 - i * 22)
        d.ellipse([200 + 160 * math.cos(a) - 22, 220 + 160 * math.sin(a) - 22, 200 + 160 * math.cos(a) + 22, 220 + 160 * math.sin(a) + 22], fill=W8)
    d.polygon(star_points(200, 200, 70), fill=W8)
    d.polygon(star_points(115, 210, 34), fill=W8)
    d.polygon(star_points(285, 210, 34), fill=W8)


PROMOTION_ICONS = {
    "Rally": pi_flag, "Steady": pi_shield, "Assault": pi_arrow, "Skirmish Drill": pi_tree, "Forced March": pi_boot,
    "Hardened Veterans": pi_chevrons, "Bayonet Charge": pi_bayonet, "Field Medicine": pi_cross,
    "Dismounted Tactics": pi_carbine, "Saber Charge": pi_sabers, "Screening": pi_eye, "Gunnery": pi_crosshair,
    "Double Canister": pi_balls, "Counter-Battery": pi_cannon, "Long Range": pi_range, "Prolonge": pi_rope,
}


def vector_icon(fn):
    img, d = vcanvas()
    fn(d)
    return finish_icon(img)


# ------------------------------------------------------------------ building and improvement icons

def bi_headquarters(d):
    d.polygon([(40, 340), (200, 120), (360, 340)], fill=W8)
    d.polygon([(170, 340), (200, 230), (230, 340)], fill=CLEAR)
    d.rectangle([194, 30, 206, 130], fill=W8)
    d.polygon([(206, 30), (310, 55), (206, 85)], fill=W8)


def bi_depot(d):
    d.rectangle([40, 200, 200, 350], fill=W8)
    d.line([40, 200, 200, 350], fill=CLEAR, width=10)
    for x in (230, 300):
        d.ellipse([x - 40, 160, x + 40, 350], fill=W8)
        d.line([x - 40, 220, x + 40, 220], fill=CLEAR, width=8)
        d.line([x - 40, 290, x + 40, 290], fill=CLEAR, width=8)


def bi_arrivals(d):
    d.polygon([(130, 380), (180, 20), (220, 20), (270, 380)], fill=W8)
    d.rectangle([194, 60, 206, 100], fill=CLEAR); d.rectangle([194, 170, 206, 220], fill=CLEAR); d.rectangle([194, 290, 206, 340], fill=CLEAR)
    d.polygon([(40, 200), (110, 130), (110, 170), (150, 170), (150, 230), (110, 230), (110, 270)], fill=W8)
    d.polygon([(360, 200), (290, 130), (290, 170), (250, 170), (250, 230), (290, 230), (290, 270)], fill=W8)


def bi_fence(d):
    """Neutral ground (the Adams County city-state type and its Home Guard Command): a split-rail fence."""
    for x in (70, 200, 330):
        d.rectangle([x - 16, 90, x + 16, 330], fill=W8)          # posts
    for y in (140, 230):
        d.polygon([(40, y), (360, y - 20), (360, y + 14), (40, y + 34)], fill=W8)   # rails


def ii_breastworks(d):
    for i in range(4):
        y = 300 - i * 52
        d.rounded_rectangle([40 + i * 10, y - 40, 360 - i * 10, y], radius=20, fill=W8)
        d.ellipse([40 + i * 10, y - 40, 80 + i * 10, y], fill=CLEAR)
        d.ellipse([48 + i * 10, y - 32, 72 + i * 10, y - 8], fill=W8)
    for x in (90, 310):
        d.polygon([(x - 12, 360), (x + 12, 360), (x + 4, 80), (x - 4, 80)], fill=W8)
