"""Generates docs/ORDER_OF_BATTLE.md and docs/UNITS.md from the game data, so the docs always match the mod.
Run from the repository root:  python3 tools/gen_docs.py
"""
import json, os, sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import gettysburg_oob as oob
import gen_promotions


def order_of_battle():
    out = ["# Gettysburg scenario - order of battle and arrival timetable", "",
           "Generated from `tools/gettysburg_oob.py`. Turn numbers are Unciv's turn counter (top bar).",
           "Each daylight turn is about one hour; each night is two turns.", "",
           "## Key positions", "",
           "Seven cities founded on landmarks at the start. They cannot be razed. "
           "The ones marked *neutral* belong to the city-state of %s, which is at war with both armies for the whole battle "
           "and cannot make peace: they must be taken by force, and until then they count for neither side. "
           "The army holding more key positions at the end of turn %d (nightfall, July 3) wins **Hold the Field**." % (oob.NEUTRAL, oob.LAST_TURN), "",
           "| Key position | Held at the start by | Why it mattered |", "|---|---|---|"]
    for name, side, why in oob.OBJECTIVES:
        out.append("| %s | %s | %s |" % (name, "%s (neutral)" % side if side == oob.NEUTRAL else side, why))
    out += ["", "## On the field at the start (turn 0)", ""]
    for side in ("Confederacy", "Union"):
        cut = oob.OPENING_CUTOFF[side]
        out.append("* **%s**: everything due by turn %d (%s) starts on the map, in or near the ground it fought over; "
                   "later forces arrive on the timetable below." % (side, cut, oob.turn_label(cut)))
    out += ["", "So the Confederate marches of July 1 are compressed, while the Union corps race up their roads on the "
            "historical timetable - the race for the high ground that the Confederacy won on July 1.", "",
            "| Side | Group | Units |", "|---|---|---|"]
    start_names = OrderedDict()
    for side, key, inst, x, y in oob.START:
        start_names.setdefault((side, "Buford's cavalry division" if side == "Union" else "Heth's division"), []).append(inst or oob.unit_name(side, key))
    for (side, label), names in start_names.items():
        out.append("| %s | %s (7:00 AM positions) | %s |" % (side, label, "; ".join(names)))
    for side, road, first, last, label, line in oob.OPENING:
        names = [n if n else oob.unit_name(side, key) for turn, s_, entry, key, ns in oob.ARRIVALS
                 if s_ == side and entry == road and first <= turn <= last for n in ns]
        out.append("| %s | %s | %s |" % (side, label, "; ".join(names)))
    out += ["", "## Entry roads", "", "| Road | Side | Notes |", "|---|---|---|"]
    for name, side, x, y, cap, desc in oob.ENTRIES:
        out.append("| %s%s | %s | %s |" % (name, " (army HQ)" if cap else "", side, desc))
    out += ["", "## Reinforcements", "",
            "They appear at the start of the turn, in or next to the entry city on their road. "
            "If the enemy has captured that city, they are lost.", "",
            "| Turn | Time | Side | Road | Arrives |", "|---|---|---|---|---|"]
    rows = OrderedDict()
    for turn, side, entry, key, names in sorted(oob.timetable(), key=lambda a: (a[0], a[1] != "Union")):
        k = (turn, side, entry)
        rows.setdefault(k, []).extend(n if n else oob.unit_name(side, key) for n in names)
    for (turn, side, entry), names in rows.items():
        out.append("| %d | %s | %s | %s | %s |" % (turn, oob.turn_label(turn), side, entry, "; ".join(names)))
    union = sum(len(a[4]) for a in oob.ARRIVALS if a[1] == "Union") + sum(1 for s in oob.START if s[0] == "Union")
    confed = sum(len(a[4]) for a in oob.ARRIVALS if a[1] == "Confederacy") + sum(1 for s in oob.START if s[0] == "Confederacy")
    out += ["", "Totals: Union %d units, Confederacy %d units (historically about 94,000 and 71,000-75,000 men)." % (union, confed), ""]
    return "\n".join(out)


def units_doc():
    units = json.load(open(os.path.join(ROOT, "jsons", "Units.json")))
    out = ["# Units", "", "Generated from `jsons/Units.json`. Strength is on Unciv's relative scale - a standard infantry brigade is 20.", ""]
    for side, title in ((None, "Base units (any army)"), ("Union", "Union - Army of the Potomac"), ("Confederacy", "Confederacy - Army of Northern Virginia")):
        out += ["## " + title, "", "| Unit | Type | Str | Ranged | Range | Move | Replaces | Abilities |", "|---|---|---|---|---|---|---|---|"]
        for u in units:
            if u.get("uniqueTo") != side:
                continue
            ab = [x for x in u.get("uniques", []) if not x.startswith("[This Unit] gets a name") and not x.startswith("Unavailable <if")]
            out.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                u["name"], u["unitType"], u.get("strength", "-"), u.get("rangedStrength", "-"),
                u.get("range", "-") if u.get("rangedStrength") else "-", u.get("movement", 0), u.get("replaces", ""),
                "<br>".join(ab).replace("|", "/")))
        out.append("")
    out += ["## Generals' personal abilities", "",
            "A general gets the ability matching his name. Only the best general's bonus in range applies (they do not stack).", "",
            "| General | Ability | Notes |", "|---|---|---|"]
    for g in gen_promotions.GENERALS:
        out.append("| %s | %s | %s |" % (g["name"], "<br>".join(g["uniques"]), g["civilopediaText"][0]["text"]))
    out += ["", "## Promotions earned in battle", "", "| Promotion | Effect | For |", "|---|---|---|"]
    for p in gen_promotions.PROMOS:
        out.append("| %s | %s | %s |" % (p["name"], "<br>".join(p["uniques"]), ", ".join(p["unitTypes"])))
    out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    open(os.path.join(ROOT, "docs", "ORDER_OF_BATTLE.md"), "w").write(order_of_battle())
    open(os.path.join(ROOT, "docs", "UNITS.md"), "w").write(units_doc())
    print("wrote docs/ORDER_OF_BATTLE.md and docs/UNITS.md")
