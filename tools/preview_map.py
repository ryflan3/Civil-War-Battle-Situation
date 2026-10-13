"""Renders a labelled top-down preview of the Gettysburg map (tools/build/gettysburg_tiles.json).

Run from the repository root:  python3 tools/preview_map.py [out.png]
"""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gettysburg_geo as geo

COLORS = {"Grassland": (118, 160, 72), "Plains": (196, 182, 96)}
FEATURE_TINT = {
    "Forest": (40, 92, 40), "Hill": (150, 120, 70), "Ridge": (140, 150, 80), "Town": (150, 70, 55),
    "Orchard": (170, 200, 90), "Boulders": (135, 135, 128), "Stone Wall": (200, 200, 190),
    "Farmstead": (190, 120, 80), "Railroad Cut": (100, 80, 60), "Marsh": (80, 130, 120),
}


def render(data, out, scale=22, labels=True):
    tiles = {(t["x"], t["y"]): t for t in data["tiles"]}
    pts = {h: geo.hex_to_world(*h) for h in tiles}
    minx = min(p[0] for p in pts.values()); maxx = max(p[0] for p in pts.values())
    miny = min(p[1] for p in pts.values()); maxy = max(p[1] for p in pts.values())
    W = int((maxx - minx + 2) * scale); H = int((maxy - miny + 2) * scale)
    img = Image.new("RGB", (W, H), (30, 30, 30))
    d = ImageDraw.Draw(img)

    def to_px(wx, wy):
        return (wx - minx + 1) * scale, (maxy - wy + 1) * scale

    def corners(h):
        cx, cy = to_px(*pts[h])
        r = scale * 1.0
        return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]

    for h, t in tiles.items():
        col = COLORS[t["base"]]
        for f in t["features"]:
            tint = FEATURE_TINT[f]
            k = 0.65 if f in ("Forest", "Town", "Boulders", "Railroad Cut") else 0.45
            col = tuple(int(col[i] * (1 - k) + tint[i] * k) for i in range(3))
        if t["wonder"]:
            col = (230, 200, 60)
        d.polygon(corners(h), fill=col, outline=(60, 70, 50))
        if t["road"]:
            cx, cy = to_px(*pts[h])
            d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(90, 60, 40))
    # road links
    for h, t in tiles.items():
        if not t["road"]:
            continue
        for n in geo.neighbors(h):
            if tiles.get(n, {}).get("road") and n > h:
                d.line([to_px(*pts[h]), to_px(*pts[n])], fill=(110, 75, 45), width=3)
    # rivers (draw the shared edge)
    for x1, y1, x2, y2 in data["rivers"]:
        a, b = to_px(*pts[(x1, y1)]), to_px(*pts[(x2, y2)])
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        px, py = -dy / L * scale * 0.55, dx / L * scale * 0.55
        d.line([(mx - px, my - py), (mx + px, my + py)], fill=(60, 120, 220), width=3)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
    except OSError:
        font = ImageFont.load_default()
    if labels:
        for h, t in tiles.items():
            if t["wonder"]:
                cx, cy = to_px(*pts[h])
                d.text((cx + 6, cy - 6), t["wonder"], fill=(255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
        for c in data["cities"]:
            cx, cy = to_px(*pts[(c["x"], c["y"])])
            colr = (60, 90, 200) if c["civ"] == "Union" else (200, 60, 60)
            d.rectangle([cx - 7, cy - 7, cx + 7, cy + 7], fill=colr, outline=(255, 255, 255))
            d.text((cx + 9, cy + 2), c["name"], fill=(255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
        for u in data.get("startUnits", []):
            cx, cy = to_px(*pts[(u["x"], u["y"])])
            colr = (40, 70, 220) if u["civ"] == "Union" else (190, 40, 40)
            d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=colr, outline=(255, 255, 255))
    img.save(out)
    return img


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    data = json.load(open(os.path.join(here, "build", "gettysburg_tiles.json")))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "build", "gettysburg_preview.png")
    render(data, out)
    print("wrote", out)
