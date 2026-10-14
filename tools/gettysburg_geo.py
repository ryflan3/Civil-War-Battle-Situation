"""Vector geography of the Gettysburg battlefield, rasterized onto Unciv's hex grid.

Coordinates are miles from the town square (the Diamond): x = east, y = north.
One hex is about 250 yards. The map is 34 columns x 37 rows.

Run from the repository root:
    python3 tools/gettysburg_geo.py            -> writes tools/build/gettysburg_tiles.json (+ preview PNG)
The Kotlin tool (tools/cwtool) turns that JSON into the Unciv map file "maps/Gettysburg (free play)" and the scenario saves.
"""
import json, math, os, sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gettysburg_oob as oob

# ---------------------------------------------------------------- grid

YARDS_PER_HEX = 250.0
WORLD_PER_MILE = 1760.0 / (YARDS_PER_HEX / math.sqrt(3))   # Unciv world units per mile
WIDTH, HEIGHT = 34, 37
CENTER_X, CENTER_Y = -0.50, -1.00                          # miles at the map's centre tile


def col_row_to_hex(col, row):
    two_rows = row * 2 + (1 if abs(col) % 2 == 1 else 0)
    return (two_rows - col) // 2, (two_rows + col) // 2


def hex_to_world(x, y):
    return 1.5 * (y - x), math.sqrt(3) / 2 * (x + y)


def hex_to_miles(x, y):
    wx, wy = hex_to_world(x, y)
    return wx / WORLD_PER_MILE + CENTER_X, wy / WORLD_PER_MILE + CENTER_Y


def all_hexes():
    # same ranges as Unciv's rectangular TileMap constructor (Kotlin integer division truncates toward zero)
    for col in range(-(WIDTH // 2), (WIDTH - 1) // 2 + 1):
        for row in range(-(HEIGHT // 2), (HEIGHT - 1) // 2 + 1):
            yield col_row_to_hex(col, row)


HEXES = list(all_hexes())
HEXSET = set(HEXES)
POS = {h: hex_to_miles(*h) for h in HEXES}
NEIGHBOR_OFFSETS = [(1, 1), (-1, -1), (0, 1), (1, 0), (0, -1), (-1, 0)]


def neighbors(h):
    for dx, dy in NEIGHBOR_OFFSETS:
        n = (h[0] + dx, h[1] + dy)
        if n in HEXSET:
            yield n


def nearest_hex(px, py):
    return min(HEXES, key=lambda h: (POS[h][0] - px) ** 2 + (POS[h][1] - py) ** 2)


# ---------------------------------------------------------------- geometry helpers

def dist_point_segment(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def dist_polyline(px, py, pts):
    return min(dist_point_segment(px, py, *pts[i], *pts[i + 1]) for i in range(len(pts) - 1))


def in_polygon(px, py, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def in_ellipse(px, py, cx, cy, rx, ry):
    return ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1.0


def segments_intersect(p1, p2, p3, p4):
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2 = orient(p3, p4, p1), orient(p3, p4, p2)
    d3, d4 = orient(p1, p2, p3), orient(p1, p2, p4)
    return (d1 > 0) != (d2 > 0) and (d3 > 0) != (d4 > 0)


def hex_path(pts, step=0.02):
    """Rasterize a polyline into a connected list of hexes."""
    path = []
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        n = max(1, int(math.hypot(bx - ax, by - ay) / step))
        for k in range(n + 1):
            px, py = ax + (bx - ax) * k / n, ay + (by - ay) * k / n
            h = nearest_hex(px, py)
            if math.hypot(POS[h][0] - px, POS[h][1] - py) > 0.12:   # off the map
                continue
            if not path or path[-1] != h:
                path.append(h)
    # straighten: drop any hex whose predecessor and successor are already adjacent (removes zig-zags)
    changed = True
    while changed:
        changed = False
        for i in range(1, len(path) - 1):
            a, c = path[i - 1], path[i + 1]
            if (c[0] - a[0], c[1] - a[1]) in NEIGHBOR_OFFSETS:
                del path[i]
                changed = True
                break
    return path


def noise(h, salt=0):
    """Deterministic pseudo-random number in [0, 1) for a hex."""
    v = (h[0] * 73856093) ^ (h[1] * 19349663) ^ (salt * 83492791)
    v = (v * 2654435761) & 0xFFFFFFFF
    return v / 2 ** 32


# ---------------------------------------------------------------- the battlefield

ROADS = OrderedDict([
    ("Chambersburg Pike", [(0, 0), (-0.3, 0.03), (-0.62, 0.07), (-1.15, 0.13), (-1.6, 0.18), (-2.05, 0.24), (-2.45, 0.30), (-2.8, 0.34)]),
    ("Fairfield Road", [(0, 0), (-0.25, -0.08), (-0.6, -0.22), (-1.2, -0.45), (-1.8, -0.7), (-2.8, -1.1)]),
    ("Mummasburg Road", [(0, 0), (-0.1, 0.3), (-0.4, 0.62), (-0.72, 0.95), (-0.88, 1.06), (-1.15, 1.3), (-1.8, 1.8)]),
    ("Middletown Road", [(-0.88, 1.06), (-0.95, 1.3), (-0.95, 1.5), (-0.97, 1.8)]),
    ("Carlisle Road", [(0, 0), (0.0, 0.3), (-0.03, 0.8), (-0.06, 1.3), (-0.08, 1.8)]),
    ("Harrisburg Road", [(0, 0), (0.08, 0.25), (0.25, 0.6), (0.42, 1.0), (0.6, 1.35), (0.70, 1.50), (0.8, 1.8)]),
    ("York Pike", [(0, 0), (0.2, 0.08), (0.6, 0.3), (1.1, 0.6), (1.7, 0.95)]),
    ("Hanover Road", [(0.2, 0.08), (0.6, 0.07), (1.0, 0.05), (1.5, 0.05), (1.7, 0.05)]),
    ("Baltimore Pike", [(0, 0), (0.04, -0.3), (0.12, -0.52), (0.3, -0.95), (0.48, -1.35), (0.7, -1.85), (0.95, -2.4), (1.2, -2.95), (1.45, -3.4), (1.6, -3.8)]),
    ("Taneytown Road", [(0, 0), (-0.02, -0.3), (-0.06, -0.65), (-0.08, -1.1), (-0.12, -1.7), (-0.16, -2.3), (-0.2, -2.9), (-0.22, -3.45), (-0.24, -3.8)]),
    ("Emmitsburg Road", [(0, 0), (-0.08, -0.25), (-0.22, -0.55), (-0.42, -0.98), (-0.65, -1.4), (-0.98, -1.85), (-1.22, -2.25), (-1.5, -2.75), (-1.95, -3.40), (-2.2, -3.8)]),
    ("Wheatfield Road", [(-0.98, -1.85), (-0.8, -1.98), (-0.6, -2.12), (-0.42, -2.25), (-0.16, -2.3)]),
])

CREEKS = OrderedDict([
    ("Willoughby Run", [(-1.38, 1.9), (-1.38, 1.0), (-1.42, 0.6), (-1.45, 0.2), (-1.45, -0.2), (-1.38, -0.7), (-1.32, -1.3), (-1.3, -1.9), (-1.35, -2.5), (-1.5, -3.2), (-1.6, -3.9)]),
    ("Plum Run", [(-0.3, -1.15), (-0.38, -1.5), (-0.45, -1.8), (-0.52, -2.15), (-0.53, -2.45), (-0.6, -2.8), (-0.7, -3.2), (-0.8, -3.9)]),
    ("Rock Creek", [(0.42, 1.9), (0.48, 1.2), (0.52, 0.9), (0.6, 0.5), (0.68, 0.15), (0.78, -0.25), (0.88, -0.6), (0.95, -1.0), (0.98, -1.4), (0.95, -1.9), (0.9, -2.4), (0.85, -3.0), (0.8, -3.9)]),
])

RIDGES = OrderedDict([
    ("Seminary Ridge", [(-0.62, 0.35), (-0.64, 0.05), (-0.7, -0.4), (-0.8, -0.9), (-0.9, -1.4), (-1.0, -1.8), (-1.08, -2.2), (-1.1, -2.6), (-1.05, -3.0)]),
    ("Oak Ridge", [(-0.62, 0.35), (-0.72, 0.6), (-0.82, 0.85), (-0.92, 1.1)]),
    ("McPherson's Ridge", [(-1.12, 0.6), (-1.14, 0.2), (-1.16, -0.2), (-1.2, -0.5)]),
    ("Herr Ridge", [(-1.95, 0.85), (-2.0, 0.3), (-2.02, -0.2), (-2.08, -0.7)]),
    ("Cemetery Ridge", [(-0.05, -0.7), (-0.15, -0.95), (-0.2, -1.2), (-0.24, -1.5), (-0.28, -1.8)]),
    ("Houck's Ridge", [(-0.62, -1.98), (-0.64, -2.2), (-0.66, -2.38)]),
    ("Emmitsburg Road Ridge", [(-0.6, -1.32), (-0.88, -1.72)]),
])

HILLS = [  # (name, cx, cy, rx, ry, wooded fraction, boulder fraction)
    ("Cemetery Hill", 0.12, -0.55, 0.20, 0.14, 0.0, 0.0),
    ("Culp's Hill", 0.66, -0.86, 0.20, 0.26, 1.0, 0.35),
    ("Little Round Top", -0.40, -2.45, 0.10, 0.10, 0.0, 0.6),
    ("Big Round Top", -0.44, -2.93, 0.18, 0.20, 1.0, 0.3),
    ("Oak Hill", -0.95, 1.15, 0.14, 0.14, 0.2, 0.0),
    ("Benner's Hill", 0.95, 0.05, 0.12, 0.10, 0.0, 0.0),
    ("Wolf Hill", 1.30, -1.05, 0.22, 0.22, 1.0, 0.25),
    ("Power's Hill", 0.40, -1.48, 0.10, 0.10, 0.4, 0.0),
    ("Stevens' Knoll", 0.38, -0.66, 0.06, 0.06, 0.0, 0.0),
    ("Stony Hill", -0.97, -2.08, 0.08, 0.08, 1.0, 0.0),
    ("McAllister's Hill", 0.72, -1.38, 0.10, 0.10, 0.6, 0.0),
]

WOODS_ELLIPSES = [  # (cx, cy, rx, ry, density)
    (-1.27, -0.06, 0.12, 0.17, 1.0),   # Herbst (McPherson's) Woods
    (-0.86, -2.33, 0.17, 0.13, 1.0),   # Rose Woods
    (-0.56, -1.98, 0.08, 0.07, 1.0),   # Trostle Woods
    (-0.03, -0.76, 0.05, 0.05, 1.0),   # Ziegler's Grove
    (1.00, -0.45, 0.17, 0.15, 0.8),    # woods along Rock Creek
    (-1.08, 1.42, 0.17, 0.14, 0.8),    # woods north of Oak Hill
    (-2.05, -0.50, 0.17, 0.16, 0.8),   # woods on Herr Ridge
    (-1.62, -0.62, 0.18, 0.16, 0.8),   # Shultz's woods beyond Willoughby Run
    (-1.62, -2.42, 0.22, 0.22, 0.75),  # woods along the lower Emmitsburg Road
    (0.80, -2.30, 0.24, 0.22, 0.8),    # woods along the Baltimore Pike
    (1.30, -2.60, 0.25, 0.30, 0.7),    # woods south-east
    (-2.35, -2.10, 0.25, 0.35, 0.6),   # woods south-west
    (1.35, 1.25, 0.22, 0.18, 0.6),     # woods north-east
    (-2.30, 1.30, 0.25, 0.20, 0.6),    # woods north-west
    (-0.10, -3.30, 0.20, 0.15, 0.6),   # woods along the upper Taneytown Road
]
SEMINARY_WOODS = [(-0.70, -0.40), (-0.80, -0.90), (-0.90, -1.40), (-1.00, -1.80), (-1.08, -2.20), (-1.10, -2.60), (-1.05, -3.00)]

TOWN = [(-0.32, 0.36), (0.22, 0.36), (0.30, 0.02), (0.20, -0.36), (-0.16, -0.36), (-0.36, -0.04)]

STONE_WALL_PATH = [(-0.07, -0.78), (-0.15, -0.95), (-0.2, -1.2), (-0.22, -1.38)]

RAILROAD_CUT = [(-0.62, 0.22), (-0.85, 0.25), (-1.10, 0.28), (-1.35, 0.30)]

ORCHARDS = [(-1.05, -1.75), (-0.40, -0.70), (-0.48, 0.35), (0.30, 0.40), (-0.50, -1.18), (-0.20, -2.0), (0.55, -0.20), (-1.55, 0.25)]

FARMSTEADS = [  # stone farmhouses, barns and other strong buildings
    (-0.45, -1.05),  # Codori farm
    (-0.56, -0.73),  # Bliss farm
    (-0.62, -1.86),  # Trostle farm
    (-1.05, -2.18),  # Rose farm
    (-0.97, -2.65),  # Slyder farm
    (-0.66, -1.40),  # Klingle farm
    (-0.33, -1.80),  # George Weikert farm
    (-0.04, -0.90),  # Leister house (Meade's HQ, July 2-3)
    (0.00, 0.43),    # Pennsylvania College
    (-2.03, 0.22),   # Herr's Tavern
    (0.30, -1.15),   # Spangler farm
    (0.48, -0.30),   # Culp farm
    (-1.25, 0.50),   # Forney farm
    (0.18, 0.75),    # Almshouse
    (1.10, 0.35),    # Lady farm
]

BOULDERS = [(-0.68, -2.55), (-0.58, -2.38), (-0.48, -2.52), (-0.55, -2.95), (0.78, -1.02), (-0.72, -2.30)]

MARSH = [(-0.60, -2.78), (-0.66, -3.05), (1.00, -1.62), (-1.42, -1.05)]

CROP_FIELDS = [  # polygons of wheat and corn (Plains); everything else is meadow (Grassland) unless chance says otherwise
    [(-0.80, -0.62), (-0.42, -0.70), (-0.30, -0.98), (-0.52, -1.36), (-0.88, -1.42), (-0.86, -0.90)],   # Pickett's Charge ground
    [(-0.60, 0.40), (0.40, 0.40), (0.52, 1.25), (-0.62, 1.10)],                                       # fields north of town
    [(-1.10, 0.75), (-0.62, 0.40), (-0.62, 0.20), (-1.10, 0.25)],                                     # fields along Oak Ridge
]

LANDMARKS = OrderedDict([
    ("Gettysburg", (0.00, 0.00)),
    ("Cemetery Hill", (0.05, -0.55)),
    ("East Cemetery Hill", (0.25, -0.52)),
    ("Culp's Hill", (0.62, -0.82)),
    ("Little Round Top", (-0.38, -2.45)),
    ("Big Round Top", (-0.42, -2.92)),
    ("Devil's Den", (-0.66, -2.47)),
    ("The Angle", (-0.18, -1.05)),
    ("Peach Orchard", (-0.98, -1.85)),
    ("The Wheatfield", (-0.80, -2.13)),
    ("Lutheran Seminary", (-0.64, 0.00)),
    ("Oak Hill", (-0.95, 1.15)),
    ("McPherson's Ridge", (-1.14, 0.08)),
    ("Barlow's Knoll", (0.32, 0.95)),
    ("Benner's Hill", (0.95, 0.05)),
])


# ---------------------------------------------------------------- rasterize

def build():
    tiles = {h: {"base": "Grassland", "features": [], "road": False, "wonder": None} for h in HEXES}

    def add(h, f):
        if f not in tiles[h]["features"]:
            tiles[h]["features"].append(f)

    # base terrain
    for h in HEXES:
        x, y = POS[h]
        if any(in_polygon(x, y, p) for p in CROP_FIELDS) or noise(h, 1) < 0.35:
            tiles[h]["base"] = "Plains"

    # ridges first, hills override them
    for pts in RIDGES.values():
        for h in hex_path(pts):
            add(h, "Ridge")
    for name, cx, cy, rx, ry, wooded, rocky in HILLS:
        for h in HEXES:
            x, y = POS[h]
            if in_ellipse(x, y, cx, cy, rx, ry) or (rx < 0.09 and h == nearest_hex(cx, cy)):
                if "Ridge" in tiles[h]["features"]:
                    tiles[h]["features"].remove("Ridge")
                add(h, "Hill")
                if noise(h, 2) < wooded:
                    add(h, "Forest")
                if noise(h, 3) < rocky:
                    add(h, "Boulders")

    # town
    for h in HEXES:
        if in_polygon(*POS[h], TOWN):
            tiles[h]["features"] = ["Town"]

    # woods
    for h in HEXES:
        x, y = POS[h]
        if "Town" in tiles[h]["features"]:
            continue
        for cx, cy, rx, ry, density in WOODS_ELLIPSES:
            if in_ellipse(x, y, cx, cy, rx, ry) and noise(h, 4) < density:
                add(h, "Forest")
        # the wooded west slope of Seminary Ridge, where the Confederate lines formed
        if dist_polyline(x, y, SEMINARY_WOODS) < 0.13 and noise(h, 5) < 0.75:
            ridge_x = min(SEMINARY_WOODS, key=lambda p: abs(p[1] - y))[0]
            if x <= ridge_x + 0.04:
                add(h, "Forest")

    # scattered farm woodlots across the countryside (kept off the crop fields and the town)
    wooded_before = {h for h in HEXES if "Forest" in tiles[h]["features"]}
    for h in HEXES:
        x, y = POS[h]
        t = tiles[h]
        if t["features"] or any(in_polygon(x, y, p) for p in CROP_FIELDS):
            continue
        if noise(h, 6) < 0.07 or (noise(h, 7) < 0.15 and any(n in wooded_before for n in neighbors(h))):
            add(h, "Forest")

    for pts, feature in ((STONE_WALL_PATH, "Stone Wall"), (RAILROAD_CUT, "Railroad Cut")):
        for h in hex_path(pts):
            tiles[h]["features"] = [f for f in tiles[h]["features"] if f == "Ridge"] + [feature]

    for points, feature in ((ORCHARDS, "Orchard"), (FARMSTEADS, "Farmstead"), (BOULDERS, "Boulders"), (MARSH, "Marsh")):
        for px, py in points:
            h = nearest_hex(px, py)
            fs = tiles[h]["features"]
            if feature in ("Orchard", "Farmstead"):
                fs[:] = [f for f in fs if f in ("Ridge", "Hill")]
            elif feature == "Marsh":
                fs[:] = []
            add(h, feature)

    # landmarks (natural wonders) - they replace whatever else is on the tile
    for name, (px, py) in LANDMARKS.items():
        h = nearest_hex(px, py)
        assert tiles[h]["wonder"] is None, (name, tiles[h]["wonder"])
        tiles[h]["wonder"] = name
        tiles[h]["features"] = []
        tiles[h]["base"] = "Plains" if name == "The Wheatfield" else "Grassland"

    # roads
    road_tiles = set()
    for pts in ROADS.values():
        road_tiles.update(hex_path(pts))
    for h in road_tiles:
        tiles[h]["road"] = True
        # a road runs through the Railroad Cut's ridge, not through the cut
    # roads never run over boulders or marsh
    for h in road_tiles:
        tiles[h]["features"] = [f for f in tiles[h]["features"] if f not in ("Boulders", "Marsh")]

    # creeks: river edges between adjacent tiles whose connecting segment crosses the creek line
    rivers = set()
    for pts in CREEKS.values():
        segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
        for h in HEXES:
            for n in neighbors(h):
                if (n, h) in rivers or (h, n) in rivers:
                    continue
                if any(segments_intersect(POS[h], POS[n], a, b) for a, b in segs):
                    rivers.add((h, n))

    # entry cities sit on open ground
    cities = []
    for name, side, px, py, capital, _ in oob.ENTRIES:
        h = nearest_hex(px, py)
        tiles[h]["features"] = []
        tiles[h]["wonder"] = None
        cities.append({"name": name, "civ": side, "x": h[0], "y": h[1], "capital": capital, "objective": False})
    # key positions: a city on the landmark itself (the landmark stays under the city)
    for name, side, _ in oob.OBJECTIVES:
        h = nearest_hex(*LANDMARKS[name])
        assert tiles[h]["wonder"] == name, name
        cities.append({"name": name, "civ": side, "x": h[0], "y": h[1], "capital": False, "objective": True})

    # tidy feature order: Hill/Ridge first, then vegetation, then the rest (Unciv uses the last one for movement cost)
    order = ["Hill", "Ridge", "Forest", "Orchard", "Boulders", "Town", "Stone Wall", "Farmstead", "Railroad Cut", "Marsh"]
    for t in tiles.values():
        t["features"] = sorted(set(t["features"]), key=order.index)

    return tiles, sorted(rivers), cities, road_tiles


CIVILIAN_KEYS = ("GEN", "AMB", "HOSP")


def unit_positions(city_sides):
    """Tiles of every unit on the field at the start: the 7:00 AM positions (oob.START), then the opening
    deployment (oob.OPENING). A tile holds one military and one civilian unit (generals are civilians).
    Units may start in their own side's cities (a garrison) but never in an enemy city.
    city_sides maps each city tile to the side that holds it."""
    out = []
    taken = set()

    def put(side, key, inst, h, group=None):
        slot = (h, key in CIVILIAN_KEYS)
        assert slot not in taken and city_sides.get(h, side) == side, ("tile taken", inst, h)
        taken.add(slot)
        out.append({"civ": side, "unit": oob.unit_name(side, key), "name": inst, "x": h[0], "y": h[1], "group": group})

    for side, key, inst, px, py in oob.START:
        put(side, key, inst, nearest_hex(px, py))

    def free(h, side, civilian):
        return city_sides.get(h, side) == side and (h, civilian) not in taken

    for side, road, first, last, label, line in oob.OPENING:
        units = [(turn, key, name) for turn, s_, entry, key, names in oob.ARRIVALS
                 if s_ == side and entry == road and first <= turn <= last for name in names]
        # candidate tiles: along the anchor line, then ring after ring around it
        candidates = hex_path(line) or [nearest_hex(*line[0])]
        seen = set(candidates)
        i = 0
        while len(candidates) < 4 * len(units) + 20 and i < len(candidates):
            for n in neighbors(candidates[i]):
                if n not in seen:
                    seen.add(n)
                    candidates.append(n)
            i += 1
        troops = []  # (turn, tile) of this group's military units, so generals ride with their own men
        for turn, key, name in units:
            if key in CIVILIAN_KEYS:
                continue
            h = next(c for c in candidates if free(c, side, False))
            put(side, key, name, h, label)
            troops.append((turn, h))
        for turn, key, name in units:
            if key not in CIVILIAN_KEYS:
                continue
            near = [h for t, h in sorted(troops, key=lambda th: abs(th[0] - turn))] + candidates
            h = next(c for c in near if free(c, side, True))
            put(side, key, name, h, label)
    return out


def export(path):
    tiles, rivers, cities, roads = build()
    data = {
        "width": WIDTH, "height": HEIGHT,
        "tiles": [{"x": h[0], "y": h[1], **t} for h, t in tiles.items()],
        "rivers": [[a[0], a[1], b[0], b[1]] for a, b in rivers],
        "cities": cities,
        "startUnits": unit_positions({(c["x"], c["y"]): c["civ"] for c in cities}),
        "startingLocations": [{"x": c["x"], "y": c["y"], "nation": c["civ"]} for c in cities if c["capital"]],
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=1)
    return data


if __name__ == "__main__":
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    d = export(os.path.join(root, "build", "gettysburg_tiles.json"))
    combos = {}
    for t in d["tiles"]:
        k = "+".join([t["base"]] + t["features"]) if not t["wonder"] else t["base"] + "+" + t["wonder"]
        combos[k] = combos.get(k, 0) + 1
    print("tiles", len(d["tiles"]), "river edges", len(d["rivers"]), "cities", len(d["cities"]))
    for k, v in sorted(combos.items(), key=lambda kv: -kv[1]):
        print("  %4d  %s" % (v, k))
