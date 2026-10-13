"""Map sprites for every unit (64x56, facing right), drawn from the figures library."""
from figures import *

W, H = 64, 56
GROUND = 44


def canvas():
    return new(W, H)


# ------------------------------------------------------------------ infantry

def infantry_line(pal, hat="kepi", flag_kind="us", pal2=None, hat2=None, gaiters=False, pose_front=AIM, roll=False):
    img = canvas()
    p2 = pal2 or pal
    h2 = hat2 or hat
    # rear rank: colour bearer and a soldier at shoulder arms
    bearer_pal = dict(pal)
    bearer_pal["F"] = WOOD_D
    flag(img, 30, 9, flag_kind, pole_len=6)
    soldier(img, 22, 16, bearer_pal, BEARER, hat)
    soldier(img, 11, 17, p2, STAND, h2)
    # front rank firing
    soldier(img, 14, 28, pal, pose_front, hat)
    soldier(img, 30, 29, p2, pose_front, h2)
    if gaiters:
        for (x, y) in ((14, 28), (30, 29)):
            for j in range(9, 11):
                for i in range(0, 8):
                    c = img.getpixel((x + i, y + j))
                    if c[3] and c[:3] in (pal["T"], pal["t"], p2["T"], p2["t"]):
                        put(img, x + i, y + j, pal["W"])
    return finish(img, (30, 41, 22, 4))


def infantry_charge(pal, hat, flag_kind, pal2=None, hat2=None):
    img = canvas()
    p2 = pal2 or pal
    bearer = dict(pal); bearer["F"] = WOOD_D
    flag(img, 33, 8, flag_kind, pole_len=6)
    soldier(img, 25, 15, bearer, BEARER, hat)
    soldier(img, 9, 20, p2, CHARGE, hat2 or hat)
    soldier(img, 16, 30, pal, CHARGE, hat)
    soldier(img, 33, 31, p2, CHARGE, hat2 or hat)
    return finish(img, (32, 42, 24, 4))


def sharpshooters(pal, hat, scoped=False, rocks=False):
    img = canvas()
    if rocks:
        for (cx, cy, r) in ((40, 39, 5), (47, 41, 4), (12, 40, 4)):
            disc(img, cx, cy, r, (120, 118, 112))
            disc(img, cx - 1, cy - 1, r - 2, (150, 148, 140))
    soldier(img, 10, 22, pal, KNEEL, hat, weapon="scoped" if scoped else None)
    soldier(img, 26, 30, pal, KNEEL, hat, weapon="scoped" if scoped else None)
    return finish(img, (28, 41, 20, 3))


# ------------------------------------------------------------------ cavalry

def cavalry(pal, hat, coat, guidon, weapon="carbine", coat2=None, neck=False, charge=False):
    img = canvas()
    flag(img, 18, 3, guidon, pole_len=16, pole=WOOD_D)
    rider(img, 4, 20, pal, hat, coat2 or coat, weapon="saber" if charge else None)
    rider(img, 22, 27, pal, hat, coat, weapon="saber" if charge else weapon)
    if neck:  # Custer's Wolverines wore red neckties
        put(img, 31, 26, RED); put(img, 13, 19, RED)
    return finish(img, (32, 41, 24, 4))


# ------------------------------------------------------------------ artillery

def battery(pal, hat, gun, carriage=(78, 92, 58), flag_kind=None, mounted=False, horse_coat="bay"):
    img = canvas()
    crew = dict(pal); crew["F"] = (40, 34, 28)   # sponge staff
    if mounted:
        rider(img, 0, 21, pal, hat, horse_coat)
    else:
        soldier(img, 4, 25, crew, BEARER, hat)       # number 1 with the sponge staff
    if flag_kind:
        flag(img, 16, 10, flag_kind, pole_len=14)
    cannon(img, 30, GROUND - 1, gun, carriage)
    soldier(img, 13, 27, pal, STAND, hat)            # gunner at the trail
    rammer = dict(pal); rammer["G"] = (40, 36, 30)
    soldier(img, 46, 25, rammer, GUNNER, hat, flip=True)   # loader at the muzzle
    return finish(img, (32, 42, 27, 4))


# ------------------------------------------------------------------ commanders and support

def general(pal, hat, coat, flag_kind, aide_pal=None, aide_coat=None):
    img = canvas()
    ap = aide_pal or pal
    flag(img, 14, 6, flag_kind, pole_len=14)
    rider(img, 2, 22, ap, "kepi", aide_coat or coat)
    rider(img, 24, 25, pal, hat, coat, weapon="glass")
    # gold sash / shoulder straps
    put(img, 32, 25, pal["Y"]); put(img, 33, 25, pal["Y"])
    return finish(img, (34, 41, 24, 4))


def supply_train(pal):
    img = canvas()
    wagon(img, 14, GROUND)
    horse(img, 34, 31, "mule")
    horse(img, 40, 33, "mule")
    soldier(img, 8, 26, pal, STAND, "slouch")
    return finish(img, (32, 42, 26, 4))


def ambulance(pal, flag_kind, hat="kepi"):
    img = canvas()
    wagon(img, 16, GROUND, cover=(232, 226, 206), kind="ambulance")
    flag(img, 15, 14, flag_kind, pole_len=10)
    horse(img, 36, 31, "bay")
    soldier(img, 6, 27, pal, STAND, hat)
    return finish(img, (32, 42, 25, 4))


def pioneers(pal, hat):
    img = canvas()
    for i in range(4):  # log breastwork
        rect(img, 30, 38 - i * 2, 22, 2, WOOD if i % 2 else WOOD_D)
    soldier(img, 12, 26, pal, DIGGER, hat)
    soldier(img, 26, 19, pal, STAND, hat)
    return finish(img, (32, 42, 24, 4))


SPRITES = {
    # generic
    "Infantry Brigade": lambda: infantry_line(N_INF, "slouch", "neutral"),
    "Sharpshooters": lambda: sharpshooters(N_INF, "slouch"),
    "Cavalry Brigade": lambda: cavalry(N_INF, "slouch", "bay", "neutral"),
    "Napoleon Battery": lambda: battery(N_INF, "slouch", "napoleon"),
    "Rifled Battery": lambda: battery(N_INF, "slouch", "ordnance"),
    "Horse Artillery": lambda: battery(N_INF, "slouch", "ordnance", mounted=True),
    "General": lambda: general(N_INF, "slouch", "dark", "neutral"),
    "Supply Train": lambda: supply_train(N_INF),
    "Pioneers": lambda: pioneers(N_INF, "slouch"),
    "Field Hospital": lambda: ambulance(N_INF, "hospital", "slouch"),
    # Union
    "Union Infantry": lambda: infantry_line(U_INF, "kepi", "us"),
    "Iron Brigade": lambda: infantry_line(U_IRON, "hardee", "regimental", gaiters=True),
    "US Sharpshooters": lambda: sharpshooters(U_SS, "kepi"),
    "Union Cavalry": lambda: cavalry(U_CAV, "slouch", "bay", "guidon_us"),
    "Michigan Cavalry Brigade": lambda: cavalry(U_CAV, "slouch", "dark", "guidon_us", coat2="bay", neck=True, charge=True),
    "Union Napoleon Battery": lambda: battery(U_ART, "kepi", "napoleon", flag_kind="artillery_us"),
    "Union Ordnance Rifles": lambda: battery(U_ART, "kepi", "ordnance"),
    "US Horse Artillery": lambda: battery(U_ART, "kepi", "ordnance", mounted=True),
    "Union General": lambda: general(U_GEN, "slouch", "dark", "us", aide_pal=U_CAV),
    "Ambulance Corps": lambda: ambulance(U_INF, "ambulance"),
    # Confederacy
    "Confederate Infantry": lambda: infantry_line(C_GRAY, "slouch", "anv", pal2=C_BUTT, hat2="kepi"),
    "Texas Brigade": lambda: infantry_charge(C_BUTT, "slouch", "texas", pal2=C_MIX),
    "Stonewall Brigade": lambda: infantry_charge(C_GRAY, "kepi", "anv"),
    "Confederate Sharpshooters": lambda: sharpshooters(C_BUTT, "slouch", scoped=True, rocks=True),
    "Confederate Cavalry": lambda: cavalry(C_CAV, "plumed", "chestnut", "guidon_cs", coat2="bay", charge=True),
    "Confederate Napoleon Battery": lambda: battery(C_ART, "kepi", "napoleon", carriage=(96, 92, 70)),
    "Confederate Parrott Rifles": lambda: battery(C_ART, "slouch", "parrott", carriage=(96, 92, 70)),
    "Whitworth Battery": lambda: battery(C_ART, "slouch", "whitworth", carriage=(96, 92, 70)),
    "Stuart Horse Artillery": lambda: battery(C_ART, "plumed", "ordnance", carriage=(96, 92, 70), mounted=True, horse_coat="chestnut"),
    "Confederate General": lambda: general(C_GEN, "slouch", "gray", "anv", aide_pal=C_CAV, aide_coat="chestnut"),
}
