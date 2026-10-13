"""Generates jsons/Buildings.json and jsons/UnitNameGroups.json from tools/gettysburg_oob.py.

Each scenario entry city holds one 'arrivals' building. Its uniques spawn the historical
reinforcements at the start of the right turn, e.g.
  "[3] free [Union Infantry] units appear <upon turn start> <after turn number [9]> <before turn number [10]> <for [Union] Civilizations>"
Units spawned that turn get their historical names from a UnitNameGroup that is only available on that turn.
Run from the repository root:  python3 tools/gen_buildings.py
"""
import json, os, sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gettysburg_oob as oob

ARRIVALS_TAG = "Gettysburg Arrivals"


def arrival_building_name(side, entry):
    return "%s Arrivals: %s" % ("Union" if side == "Union" else "Confederate", entry)


def build():
    oob.check()
    buildings = [
        {
            "name": "Army Headquarters",
            "isNationalWonder": True,
            "cost": 0,
            "production": 3,
            "gold": 3,
            "cityStrength": 8,
            "cityHealth": 50,
            "uniques": ["Indicates the capital city", "[+25]% Production when constructing [Military] units [in this city]"],
            "civilopediaText": [
                {"text": "The army commander's headquarters, with its staff, couriers and signal officers. Losing it means losing the army: capturing the enemy headquarters wins a Decisive Victory."}
            ]
        },
        {
            "name": "Supply Depot",
            "cost": 50,
            "production": 2,
            "food": 1,
            "gold": 2,
            "cityStrength": 5,
            "cityHealth": 25,
            "uniques": ["[+15]% Production when constructing [Military] units [in this city]"],
            "civilopediaText": [
                {"text": "Wagon parks, ammunition trains and commissary stores at the end of a road or railroad."}
            ]
        },
    ]

    by_entry = OrderedDict()
    for turn, side, entry, key, names in oob.ARRIVALS:
        by_entry.setdefault((side, entry), []).append((turn, key, names))

    for (side, entry), rows in by_entry.items():
        rows.sort(key=lambda r: r[0])
        uniques = [ARRIVALS_TAG, "Unbuildable", "Unsellable", "Destroyed when the city is captured"]
        timetable = OrderedDict()
        for turn, key, names in rows:
            unit = oob.unit_name(side, key)
            when = "<upon turn start> <after turn number [%d]> <before turn number [%d]> <for [%s] Civilizations>" % (turn, turn + 1, side)
            if len(names) == 1:
                uniques.append("Free [%s] appears %s" % (unit, when))
            else:
                uniques.append("[%d] free [%s] units appear %s" % (len(names), unit, when))
            label = "Turn %d (%s)" % (turn, oob.turn_label(turn))
            timetable.setdefault(label, []).extend(n if n else unit for n in names)
        description = next(e[5] for e in oob.ENTRIES if e[0] == entry)
        text = ["Order of march for the %s." % entry, description, ""]
        for label, units in timetable.items():
            text.append("%s: %s" % (label, "; ".join(units)))
        text += ["", "Reinforcements appear in or next to this city at the start of the listed turn. If the enemy captures the city, the remaining reinforcements on this road are lost."]
        buildings.append({
            "name": arrival_building_name(side, entry),
            "cost": 1,
            "uniqueTo": side,
            "uniques": uniques,
            "replacementTextForUniques": "\n".join(text),
        })

    # ---------------------------------------------------------------- name groups
    groups = []
    keyed = OrderedDict()
    for turn, side, entry, key, names in oob.ARRIVALS:
        named = [n for n in names if n]
        if not named:
            continue
        keyed.setdefault((side, key, turn), []).extend(named)
    for (side, key, turn), names in keyed.items():
        unit = oob.unit_name(side, key)
        groups.append({
            "name": "%s arriving on turn %d" % (unit, turn),
            "unitNames": names,
            "uniques": [unit,
                        "Only available <after turn number [%d]> <before turn number [%d]> <if [%s] is constructed>" % (turn, turn + 1, ARRIVALS_TAG)],
        })
    for side, gen in (("Union", "Union General"), ("Confederacy", "Confederate General")):
        groups.append({
            "name": "%s generals" % ("Union" if side == "Union" else "Confederate"),
            "unitNames": oob.FREE_PLAY_GENERALS[side],
            "uniques": [gen, "Unavailable <if [%s] is constructed>" % ARRIVALS_TAG],
        })
    return buildings, groups


if __name__ == "__main__":
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    b, g = build()
    with open(os.path.join(root, "jsons", "Buildings.json"), "w") as f:
        json.dump(b, f, indent=4)
    with open(os.path.join(root, "jsons", "UnitNameGroups.json"), "w") as f:
        json.dump(g, f, indent=4)
    print("Wrote %d buildings, %d unit name groups" % (len(b), len(g)))
