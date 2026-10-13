"""Renders the Gettysburg map with the mod's own art (docs/gettysburg_map.png) and the mod-manager preview (preview.png).

Run from the repository root after tools/gettysburg_geo.py and tools/art/make_art.py:
    python3 tools/render_map.py
"""
import json, math, os, random, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "art"))
import gettysburg_geo as geo
from pixel import new, put, disc, outline, upscale
from tiles_art import tree, mound, HEX, inside, clip, tile

TILES = os.path.join(ROOT, "Images", "TileSets", "HexaRealm", "Tiles")
UNITS = os.path.join(ROOT, "Images", "TileSets", "CivilWar", "Units")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def base_hex(color, seed):
    random.seed(seed)
    img = tile()
    for x in range(64):
        for y in range(56):
            if inside(x + 0.5, y + 0.5):
                k = random.random()
                c = color if k > 0.15 else tuple(max(0, v - 14) for v in color)
                put(img, x, y, c)
    for x in range(64):
        for y in range(56):
            if img.getpixel((x, y))[3] and (not inside(x + 2.5, y + 0.5) or not inside(x - 1.5, y + 0.5) or not inside(x + 0.5, y + 2.5)):
                put(img, x, y, tuple(max(0, v - 30) for v in color))
    return img


def forest_overlay(seed):
    random.seed(seed)
    img = tile()
    for _ in range(9):
        x, y = random.randint(12, 52), random.randint(10, 44)
        if inside(x, y):
            tree(img, x, y, 3, kind=random.choice(("leaf", "leaf", "pine")))
    return clip(img)


def hill_overlay():
    img = tile()
    mound(img, 32, 30, 26, 18)
    return clip(img)


def load(path):
    return Image.open(path).convert("RGBA")


def render(scale=1.0, with_units=True, labels=True):
    data = json.load(open(os.path.join(HERE, "build", "gettysburg_tiles.json")))
    tiles = {(t["x"], t["y"]): t for t in data["tiles"]}
    pos = {}
    for h in tiles:
        wx, wy = geo.hex_to_world(*h)
        pos[h] = (wx * 32.0, -wy * 32.33)
    minx = min(p[0] for p in pos.values()) - 32; maxx = max(p[0] for p in pos.values()) + 32
    miny = min(p[1] for p in pos.values()) - 28; maxy = max(p[1] for p in pos.values()) + 28
    W, H = int(maxx - minx), int(maxy - miny)
    img = Image.new("RGBA", (W, H), (34, 30, 26, 255))
    bases = {"Grassland": [base_hex((104, 150, 66), s) for s in range(3)], "Plains": [base_hex((186, 172, 88), s + 10) for s in range(3)]}
    forests = [forest_overlay(s) for s in range(4)]
    hill = hill_overlay()
    cache = {}

    def art(name):
        if name not in cache:
            p = os.path.join(TILES, name + ".png")
            cache[name] = load(p) if os.path.exists(p) else None
        return cache[name]

    order = sorted(tiles, key=lambda h: (pos[h][1], pos[h][0]))
    centers = {}
    for h in order:
        t = tiles[h]
        cx, cy = pos[h][0] - minx, pos[h][1] - miny
        centers[h] = (cx, cy)
        ox, oy = int(cx - 32), int(cy - 28)
        img.alpha_composite(bases[t["base"]][(h[0] * 7 + h[1] * 3) % 3], (ox, oy))
        layers = []
        for f in t["features"]:
            if f == "Hill":
                layers.append(hill)
            elif f == "Forest":
                layers.append(forests[(h[0] + h[1]) % 4])
            elif f == "Marsh":
                continue
            else:
                layers.append(art(f))
        if t["wonder"]:
            layers.append(art(t["wonder"]))
        for l in layers:
            if l is not None:
                img.alpha_composite(l, (ox, oy))
    d = ImageDraw.Draw(img)
    # roads
    for h, t in tiles.items():
        if not t["road"]:
            continue
        for n in geo.neighbors(h):
            if n in tiles and tiles[n]["road"] and n > h:
                d.line([centers[h], centers[n]], fill=(132, 100, 64), width=5)
                d.line([centers[h], centers[n]], fill=(170, 136, 90), width=2)
    # creeks on tile edges
    for x1, y1, x2, y2 in data["rivers"]:
        a, b = centers[(x1, y1)], centers[(x2, y2)]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        px, py = -dy / L * 19, dx / L * 19
        d.line([(mx - px, my - py), (mx + px, my + py)], fill=(64, 120, 200), width=5)
    # cities
    for c in data["cities"]:
        cx, cy = centers[(c["x"], c["y"])]
        city = art("City center-%s-Civil War era" % c["civ"])
        img.alpha_composite(city, (int(cx - 32), int(cy - 28)))
    if with_units:
        for u in data["startUnits"]:
            cx, cy = centers[(u["x"], u["y"])]
            sp = load(os.path.join(UNITS, u["unit"] + ".png"))
            img.alpha_composite(sp, (int(cx - 32), int(cy - 30)))
    if labels:
        font = ImageFont.truetype(FONT, 17)
        city_tiles = {(c["x"], c["y"]) for c in data["cities"]}
        for h, t in tiles.items():
            if t["wonder"] and h not in city_tiles:   # a key position is labelled once, as a city
                cx, cy = centers[h]
                d.text((cx - 4, cy + 10), t["wonder"], fill=(255, 250, 230), font=font, stroke_width=3, stroke_fill=(20, 16, 12), anchor="mt")
        for c in data["cities"]:
            cx, cy = centers[(c["x"], c["y"])]
            col = (150, 180, 255) if c["civ"] == "Union" else (255, 160, 150)
            name = ("\u2605 " + c["name"]) if c.get("objective") else c["name"]   # key positions get a star
            d.text((cx, cy + 22), name, fill=col, font=font, stroke_width=3, stroke_fill=(20, 16, 12), anchor="mt")
    if scale != 1.0:
        img = img.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
    return img


def preview(map_img):
    W, H = 900, 500
    out = Image.new("RGBA", (W, H), (24, 26, 34, 255))
    m = map_img.copy()
    k = W / m.width
    m = m.resize((W, int(m.height * k)), Image.LANCZOS)
    top = int(m.height * 0.30)
    out.alpha_composite(m.crop((0, top, W, top + H)))
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rectangle([0, 0, W, 150], fill=(16, 18, 26, 205))
    sd.rectangle([0, H - 110, W, H], fill=(16, 18, 26, 190))
    out.alpha_composite(shade)
    d = ImageDraw.Draw(out)
    d.text((W // 2, 46), "CIVIL WAR BATTLE SITUATION", fill=(240, 228, 196), font=ImageFont.truetype(SERIF, 48), anchor="mm")
    d.text((W // 2, 104), "Gettysburg  -  July 1-3, 1863", fill=(214, 196, 150), font=ImageFont.truetype(SERIF, 28), anchor="mm")
    union = ["Union Infantry", "Iron Brigade", "Union Cavalry", "Union Napoleon Battery", "Union General"]
    confed = ["Confederate General", "Confederate Parrott Rifles", "Confederate Cavalry", "Texas Brigade", "Confederate Infantry"]
    for i, n in enumerate(union):
        sp = upscale(load(os.path.join(UNITS, n + ".png")), 2)
        out.alpha_composite(sp, (10 + i * 82, H - 112))
    for i, n in enumerate(confed):
        sp = upscale(load(os.path.join(UNITS, n + ".png")), 2).transpose(Image.FLIP_LEFT_RIGHT)
        out.alpha_composite(sp, (W - 138 - i * 82, H - 112))
    return out.convert("RGB")


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    full = render()
    full.resize((full.width // 2, full.height // 2), Image.LANCZOS).convert("RGB").save(os.path.join(ROOT, "docs", "gettysburg_map.png"), optimize=True)
    preview(full).save(os.path.join(ROOT, "preview.png"), optimize=True)
    print("map", full.size, "-> docs/gettysburg_map.png (half size), preview.png")
