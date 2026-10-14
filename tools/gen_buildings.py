"""Generates jsons/Buildings.json and jsons/UnitNameGroups.json from tools/gettysburg_oob.py.

Each scenario objective city holds the 'Key Position' building, which the Hold the Field victory counts.
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

# Every building the scenario places carries this tag; "<if [Gettysburg Scenario] is constructed>" means "in the scenario"
SCENARIO_TAG = "Gettysburg Scenario"


# The capital building of the neutral city-state that holds some key positions at the start
NEUTRAL_CAPITAL = "Home Guard Command"


def _names(names):
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1] if names else ""


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
            # Strong enough that only a real assault takes it: the other cities get no "tech" strength in this mod
            # (cityStrengthFromTechsFullMultiplier 0), so their defence is base + buildings + garrison.
            "cityStrength": 40,
            "cityHealth": 300,
            "uniques": ["Indicates the capital city", "[+25]% Production when constructing [Military] units [in this city]"],
            "civilopediaText": [
                {"text": "The army commander's headquarters, with its staff, couriers, signal officers and the guard. Losing it means losing the army: capturing the enemy headquarters wins a Decisive Victory."},
                {"text": "It is far stronger than any other city: taking it needs a deliberate assault, with artillery and several brigades."}
            ]
        },
        # Must come after Army Headquarters: an army takes the first capital building in this list that is not
        # reserved for someone else, and this one is reserved for the neutral city-state.
        {
            "name": NEUTRAL_CAPITAL,
            "cost": 0,
            "uniqueTo": "City-States",
            "uniques": ["Indicates the capital city", "Unbuildable", "Unsellable"],
            "civilopediaText": [
                {"text": "Marks the neutral key positions of the Gettysburg scenario, held by %s - the town and the farms that neither army has occupied yet." % oob.NEUTRAL},
                {"text": "Both armies are at war with %s for the whole battle, and no peace can be made: a neutral key position must be taken by force. Nobody defends it but a few home-guard companies, so a brigade or two takes it quickly - but until then it counts for neither side." % oob.NEUTRAL},
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
        {
            "name": oob.OBJECTIVE_BUILDING,
            "cost": 1,
            "cityStrength": 4,
            "cityHealth": 25,
            "uniques": [SCENARIO_TAG, "Unbuildable", "Unsellable", "Never destroyed when the city is captured"],
            "civilopediaText": [
                {"text": "One of the seven key positions of the Gettysburg scenario: %s." % ", ".join(o[0] for o in oob.OBJECTIVES)},
                {"text": "Each is a city that cannot be razed. %s start in Union hands; %s start neutral (held by %s) and must be taken by force. At nightfall on July 3 (the end of turn %d) the army holding more key positions wins the Hold the Field victory." % (
                    _names([o[0] for o in oob.OBJECTIVES if o[1] == "Union"]) or "None", _names([o[0] for o in oob.OBJECTIVES if o[1] == oob.NEUTRAL]) or "none", oob.NEUTRAL, oob.LAST_TURN)},
                {"text": "Rifle pits, gun emplacements and stone walls make the position stronger to defend than an ordinary town."},
            ]
        },
    ]

    by_entry = OrderedDict()
    for turn, side, entry, key, names in oob.timetable():
        by_entry.setdefault((side, entry), []).append((turn, key, names))

    for (side, entry), rows in by_entry.items():
        rows.sort(key=lambda r: r[0])
        uniques = [SCENARIO_TAG, "Unbuildable", "Unsellable", "Destroyed when the city is captured"]
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
    for turn, side, entry, key, names in oob.timetable():
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
                        "Only available <after turn number [%d]> <before turn number [%d]> <if [%s] is constructed>" % (turn, turn + 1, SCENARIO_TAG)],
        })
    for side, gen in (("Union", "Union General"), ("Confederacy", "Confederate General")):
        groups.append({
            "name": "%s generals" % ("Union" if side == "Union" else "Confederate"),
            "unitNames": oob.FREE_PLAY_GENERALS[side],
            "uniques": [gen, "Unavailable <if [%s] is constructed>" % SCENARIO_TAG],
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
