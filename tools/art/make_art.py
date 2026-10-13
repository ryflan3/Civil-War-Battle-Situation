"""Generates every image of the mod into <repo>/Images. Run from anywhere:  python3 tools/art/make_art.py

Afterwards pack the atlas (game.atlas / game.png) - see README "Rebuilding".
"""
import os, sys, json, shutil
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from figures import *
from units_art import SPRITES
from icons_art import (portrait_background, nation_union, nation_confederacy, leader_portrait, PROMOTION_ICONS,
                       vector_icon, pi_union_general, pi_confed_general, bi_headquarters, bi_depot, bi_arrivals,
                       ii_breastworks, icon_pioneer)
from tiles_art import FEATURES, WONDERS, CITY_CENTERS

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
IMAGES = os.path.join(ROOT, "Images")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gen_promotions
import gettysburg_oob as oob

# ------------------------------------------------------------------ hero figures (one figure per unit, in its own uniform)

def hero_soldier(pal, hat, pose=AIM, flag_kind=None, scoped=False, gaiters=False):
    img = new(40, 40)
    if flag_kind:
        flag(img, 4, 2, flag_kind, pole_len=20)
    soldier(img, 8, 16, pal, pose, hat, weapon="scoped" if scoped else None)
    if gaiters:
        for j in range(9, 12):
            for i in range(0, 8):
                c = img.getpixel((8 + i, 16 + j))
                if c[3] and c[:3] in (pal["T"], pal["t"]):
                    put(img, 8 + i, 16 + j, pal["W"])
    return img


def hero_rider(pal, hat, coat, weapon=None, flag_kind=None, neck=False):
    img = new(40, 40)
    if flag_kind:
        flag(img, 10, 2, flag_kind, pole_len=16)
    rider(img, 8, 20, pal, hat, coat, weapon=weapon)
    if neck:
        put(img, 17, 19, RED)
    return img


def hero_gun(kind, carriage=(78, 92, 58), horse_coat=None):
    img = new(40, 40)
    if horse_coat:
        horse(img, 18, 12, horse_coat)
    cannon(img, 16, 36, kind, carriage)
    return img


def hero_wagon(kind="supply", flag_kind=None):
    img = new(40, 40)
    wagon(img, 6, 34, kind=kind)
    if flag_kind:
        flag(img, 6, 8, flag_kind, pole_len=12)
    return img


def hero_pioneer(pal, hat):
    img = new(40, 40)
    for i in range(3):
        rect(img, 18, 34 - i * 2, 18, 2, WOOD if i % 2 else WOOD_D)
    soldier(img, 6, 18, pal, DIGGER, hat)
    return img


CS_CARRIAGE = (96, 92, 70)
HERO = {
    "Infantry Brigade": lambda f: hero_soldier(N_INF, "slouch", flag_kind=f and "neutral"),
    "Union Infantry": lambda f: hero_soldier(U_INF, "kepi", flag_kind=f and "us"),
    "Iron Brigade": lambda f: hero_soldier(U_IRON, "hardee", flag_kind=f and "regimental", gaiters=True),
    "Confederate Infantry": lambda f: hero_soldier(C_GRAY, "slouch", flag_kind=f and "anv"),
    "Texas Brigade": lambda f: hero_soldier(C_BUTT, "slouch", CHARGE, flag_kind=f and "texas"),
    "Stonewall Brigade": lambda f: hero_soldier(C_GRAY, "kepi", CHARGE, flag_kind=f and "anv"),
    "Sharpshooters": lambda f: hero_soldier(N_INF, "slouch", KNEEL),
    "US Sharpshooters": lambda f: hero_soldier(U_SS, "kepi", KNEEL),
    "Confederate Sharpshooters": lambda f: hero_soldier(C_BUTT, "slouch", KNEEL, scoped=True),
    "Cavalry Brigade": lambda f: hero_rider(N_INF, "slouch", "bay", flag_kind=f and "neutral"),
    "Union Cavalry": lambda f: hero_rider(U_CAV, "slouch", "bay", "carbine", flag_kind="guidon_us"),
    "Michigan Cavalry Brigade": lambda f: hero_rider(U_CAV, "slouch", "dark", "saber", flag_kind=f and "guidon_us", neck=True),
    "Confederate Cavalry": lambda f: hero_rider(C_CAV, "plumed", "chestnut", "saber", flag_kind=f and "guidon_cs"),
    "Napoleon Battery": lambda f: hero_gun("napoleon"),
    "Union Napoleon Battery": lambda f: hero_gun("napoleon"),
    "Confederate Napoleon Battery": lambda f: hero_gun("napoleon", CS_CARRIAGE),
    "Rifled Battery": lambda f: hero_gun("ordnance"),
    "Union Ordnance Rifles": lambda f: hero_gun("ordnance"),
    "Confederate Parrott Rifles": lambda f: hero_gun("parrott", CS_CARRIAGE),
    "Whitworth Battery": lambda f: hero_gun("whitworth", CS_CARRIAGE),
    "Horse Artillery": lambda f: hero_gun("ordnance", horse_coat="bay"),
    "US Horse Artillery": lambda f: hero_gun("ordnance", horse_coat="bay"),
    "Stuart Horse Artillery": lambda f: hero_gun("ordnance", CS_CARRIAGE, horse_coat="chestnut"),
    "General": lambda f: hero_rider(N_INF, "slouch", "dark", "glass", flag_kind="neutral"),
    "Union General": lambda f: hero_rider(U_GEN, "slouch", "dark", "glass", flag_kind="us"),
    "Confederate General": lambda f: hero_rider(C_GEN, "slouch", "gray", "glass", flag_kind="anv"),
    "Supply Train": lambda f: hero_wagon(),
    "Pioneers": lambda f: hero_pioneer(U_INF, "kepi") if f else icon_pioneer(),
    "Field Hospital": lambda f: hero_wagon("ambulance", "hospital"),
    "Ambulance Corps": lambda f: hero_wagon("ambulance", "ambulance"),
}


def save(img, *parts):
    path = os.path.join(IMAGES, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path


def main():
    if os.path.isdir(IMAGES):
        shutil.rmtree(IMAGES)
    count = 0
    units = [u["name"] for u in json.load(open(os.path.join(ROOT, "jsons", "Units.json")))]
    assert set(units) == set(SPRITES) == set(HERO), "unit list mismatch"
    bg = portrait_background()
    save(bg, "UnitPortraits", "Background.png"); count += 1
    for name in units:
        save(SPRITES[name](), "TileSets", "CivilWar", "Units", name + ".png")
        hero_color = HERO[name](True)
        outline(hero_color)
        save(fit_center(hero_color, 128, 6), "UnitPortraits", name + ".png")
        icon = silhouette(HERO[name](False))
        save(fit_center(icon, 100, 4), "UnitIcons", name + ".png")
        count += 3

    save(nation_union(), "NationIcons", "Union.png")
    save(nation_confederacy(), "NationIcons", "Confederacy.png")
    for leader in ("George G. Meade", "Robert E. Lee"):
        save(leader_portrait(leader), "LeaderIcons", leader + ".png")
    count += 4

    for name, fn in PROMOTION_ICONS.items():
        save(vector_icon(fn), "UnitPromotionIcons", name + ".png"); count += 1
    union_gen, confed_gen = vector_icon(pi_union_general), vector_icon(pi_confed_general)
    for g in gen_promotions.GENERALS:
        is_union = g["name"] in oob.FREE_PLAY_GENERALS["Union"]
        save(union_gen if is_union else confed_gen, "UnitPromotionIcons", g["name"] + ".png"); count += 1

    buildings = [b["name"] for b in json.load(open(os.path.join(ROOT, "jsons", "Buildings.json")))]
    hq, depot, arr = vector_icon(bi_headquarters), vector_icon(bi_depot), vector_icon(bi_arrivals)
    for b in buildings:
        save(hq if b == "Army Headquarters" else depot if b == "Supply Depot" else arr, "BuildingIcons", b + ".png"); count += 1
    save(vector_icon(ii_breastworks), "ImprovementIcons", "Breastworks.png"); count += 1

    tiles = {}
    tiles.update(FEATURES); tiles.update(WONDERS); tiles.update(CITY_CENTERS)
    for name, fn in tiles.items():
        img = fn()
        save(img, "TileSets", "HexaRealm", "Tiles", name + ".png")
        save(img.resize((32, 28), Image.LANCZOS), "TileSets", "FantasyHex", "Tiles", name + ".png")
        count += 2
    print("Wrote %d images to %s" % (count, IMAGES))


if __name__ == "__main__":
    main()
