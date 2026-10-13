"""Generates jsons/UnitPromotions.json.

Three kinds of promotions:
  * XP promotions that units earn in combat (per arm of service),
  * the 'Holding Key Terrain' status used by the Hold the Field victory,
  * personal abilities of named generals. Unciv automatically grants a promotion whose name
    equals the name a unit receives from a UnitNameGroup, so 'Winfield S. Hancock' gets his.
Run from the repository root:  python3 tools/gen_promotions.py
"""
import json, os

INF, SKIR, CAV, ART = "Infantry", "Skirmisher", "Cavalry", "Artillery"
LINE = [INF, SKIR, CAV]
ALL = [INF, SKIR, CAV, ART]

def p(name, uniques, types, col, row, prereq=None, text=None):
    d = {"name": name, "uniques": uniques, "unitTypes": types, "column": col, "row": row}
    if prereq: d["prerequisites"] = prereq
    if text: d["civilopediaText"] = [{"text": text}]
    return d

PROMOS = [
    p("Rally", ["[This Unit] heals [50] HP", "Doing so will consume this opportunity to choose a Promotion"], ALL, 0, 0,
      text="Officers re-form the shattered ranks; stragglers return to the colors."),

    # Line troops
    p("Steady I", ["[+15]% Strength <when defending>"], LINE, 1, 1, text="Discipline under fire: the line holds and keeps loading."),
    p("Steady II", ["[+15]% Strength <when defending>"], LINE, 1, 2, ["Steady I"]),
    p("Steady III", ["[+15]% Strength <when defending>"], LINE, 1, 3, ["Steady II"]),
    p("Assault I", ["[+15]% Strength <when attacking>"], LINE, 2, 1, text="Experience in closing with the enemy at the run."),
    p("Assault II", ["[+15]% Strength <when attacking>"], LINE, 2, 2, ["Assault I"]),
    p("Assault III", ["[+15]% Strength <when attacking>"], LINE, 2, 3, ["Assault II"]),
    p("Skirmish Drill", ["[+20]% Strength <when fighting in [Rough terrain] tiles>"], [INF, SKIR], 3, 1,
      text="Fighting in open order from tree to rock, using every scrap of cover."),
    p("Forced March", ["[+1] Movement"], [INF, SKIR], 3, 2, ["Steady I", "Assault I"],
      text="Veterans who can march twenty miles and fight at the end of it - like Sedgwick's VI Corps, which covered 34 miles to reach the field on July 2."),
    p("Hardened Veterans", ["No damage penalty for wounded units"], LINE, 4, 3, ["Steady II", "Assault II"],
      text="Regiments that fight on at half strength without breaking."),
    p("Bayonet Charge", ["[+25]% Strength <vs [Wounded] units> <when attacking>"], [INF], 4, 2, ["Assault II"],
      text="Out of ammunition and facing a tired enemy, Colonel Chamberlain ordered the 20th Maine to fix bayonets and charge down Little Round Top."),
    p("Field Medicine", ["All adjacent units heal [+5] HP when healing"], LINE, 5, 1, ["Steady I", "Assault I"]),

    # Cavalry
    p("Dismounted Tactics", ["[+20]% Strength <when defending>"], [CAV], 6, 1,
      text="Every fourth man holds the horses while the rest fight on foot with carbines from behind fences."),
    p("Saber Charge", ["[+33]% Strength <vs [Wounded] units>", "[+33]% Strength <vs [Artillery] units>"], [CAV], 6, 2, ["Dismounted Tactics"],
      text="A mounted charge against shaken troops or unsupported guns."),
    p("Screening", ["[+1] Sight", "[+1] Movement"], [CAV], 7, 1, text="Pickets and vedettes far ahead of the army."),

    # Artillery
    p("Gunnery I", ["[+15]% Strength <when attacking>"], [ART], 8, 1, text="Well-drilled crews, accurate range estimation and good fuse cutting."),
    p("Gunnery II", ["[+15]% Strength <when attacking>"], [ART], 8, 2, ["Gunnery I"]),
    p("Gunnery III", ["[+15]% Strength <when attacking>"], [ART], 8, 3, ["Gunnery II"]),
    p("Double Canister", ["[+33]% Strength <when defending>"], [ART], 9, 1,
      text="At the last moment, two loads of canister at once."),
    p("Counter-Battery", ["[+33]% Strength <vs [Artillery] units>"], [ART], 9, 2, ["Gunnery I"]),
    p("Long Range", ["[+1] Range"], [ART], 9, 3, ["Gunnery III"], text="Experienced officers who can hit targets at extreme range."),
    p("Prolonge", ["Can move after attacking"], [ART], 10, 2, ["Gunnery II"],
      text="Firing while being dragged back by ropes - the 9th Massachusetts Battery retired 'by prolonge' from the Peach Orchard on July 2."),
]

STATUS = [{
    "name": "Holding Key Terrain",
    "uniques": ["Comment [This unit occupies key terrain and counts toward the Hold the Field victory]"],
    "innerColor": [255, 217, 102], "outerColor": [60, 50, 20],
    "civilopediaText": [{"text": "Given for one turn to a military unit that ends its turn on Cemetery Hill, East Cemetery Hill, Culp's Hill, Little Round Top or the Angle."}],
}]

def g(name, uniques, text):
    return {"name": name, "uniques": uniques, "innerColor": [255, 255, 255], "outerColor": [90, 70, 30],
            "civilopediaText": [{"text": text}]}

ALL_MIL = "{Military} {Land}"
def aura(pct, filt, radius, cond=""):
    return "[+%d]%% Strength bonus for [%s] units within [%d] tiles%s" % (pct, filt, radius, (" " + cond) if cond else "")

GENERALS = [
    # Union
    g("George G. Meade", [aura(20, ALL_MIL, 3, "<when defending>")],
      "Commanding the Army of the Potomac since June 28. Fought a skillful defensive battle on interior lines, shifting brigades to each threatened point. Inspires all troops within 3 tiles when defending."),
    g("John F. Reynolds", [aura(25, ALL_MIL, 1), "[+1] Movement"],
      "Commander of the I Corps and the army's left wing; widely thought the best general in the army. He rushed his men into Herbst Woods on the morning of July 1 and was shot dead at its edge."),
    g("Winfield S. Hancock", [aura(25, ALL_MIL, 2)],
      "'Hancock the Superb', II Corps. Sent ahead by Meade on July 1, he rallied the broken corps on Cemetery Hill; on July 2 he plugged every gap in the line; on July 3 he was wounded repelling Pickett's Charge."),
    g("Oliver O. Howard", [aura(20, ALL_MIL, 2, "<when defending>")],
      "XI Corps. Posted his reserve on Cemetery Hill at midday on July 1 - the decision that gave the army its anchor. Congress later thanked him for selecting the position."),
    g("Abner Doubleday", [aura(15, ALL_MIL, 2), "[+10]% Strength <when defending>"],
      "Commanded the I Corps after Reynolds fell and held McPherson's and Seminary Ridges for most of July 1."),
    g("Daniel E. Sickles", [aura(20, ALL_MIL, 2, "<when attacking>")],
      "III Corps. A political general who, without orders, advanced his corps to the Peach Orchard salient on July 2. His leg was shattered by a cannonball at the Trostle farm."),
    g("Henry W. Slocum", [aura(20, ALL_MIL, 2, "<when defending>")],
      "XII Corps, which fought for Culp's Hill on the nights of July 2 and the morning of July 3."),
    g("George Sykes", [aura(15, ALL_MIL, 2)],
      "V Corps, the army's reserve, including the U.S. Regulars, which saved Little Round Top and fought in the Wheatfield."),
    g("John Sedgwick", [aura(15, ALL_MIL, 2), "[+1] Movement"],
      "VI Corps, the largest in the army, which marched about 34 miles to reach the field on July 2."),
    g("John Gibbon", [aura(20, ALL_MIL, 2, "<when defending>")],
      "Commanded the II Corps division at the Angle that met Pickett's Charge."),
    g("John Buford", [aura(25, "Cavalry", 2), "[+2] Sight"],
      "Cavalry division commander with an eye for ground. He recognized the importance of the heights at Gettysburg and held off Heth's infantry on July 1 until the I Corps arrived."),
    g("Gouverneur K. Warren", ["[+2] Sight", "Can see over obstacles", aura(15, ALL_MIL, 2)],
      "Meade's chief engineer. From the signal station on Little Round Top he saw Hood's division about to sweep the undefended hill and diverted troops to it just in time."),
    g("Henry J. Hunt", [aura(25, "Artillery", 3)],
      "Chief of artillery of the Army of the Potomac and the best artillerist of the war. He husbanded his ammunition during the July 3 cannonade so the guns could smash Pickett's Charge."),
    g("David M. Gregg", [aura(20, "Cavalry", 2, "<when defending>")],
      "2nd Cavalry Division, which with Custer's brigade stopped Stuart at East Cavalry Field on July 3."),
    g("Judson Kilpatrick", [aura(20, "Cavalry", 2, "<when attacking>")],
      "'Kill-Cavalry'. On July 3 he ordered Farnsworth's hopeless mounted charge against Confederate infantry south of Big Round Top."),
    # Confederacy
    g("Robert E. Lee", [aura(15, ALL_MIL, 3, "<when attacking>")],
      "Commanding the Army of Northern Virginia. Confident after Chancellorsville, he attacked on all three days. Inspires all troops within 3 tiles when attacking."),
    g("James Longstreet", [aura(25, ALL_MIL, 2, "<when defending>")],
      "'Old Pete', I Corps. Lee's 'old war horse' urged a move around the Union left onto defensive ground, and opposed the July 3 assault. His July 2 attack nevertheless came close to rolling up the Union line."),
    g("Richard S. Ewell", [aura(15, ALL_MIL, 2)],
      "II Corps, Stonewall Jackson's successor. Told to take Cemetery Hill on July 1 'if practicable', he decided it was not."),
    g("A. P. Hill", [aura(15, ALL_MIL, 2)],
      "III Corps, which opened the battle on July 1. Hill was ill during much of the battle."),
    g("Henry Heth", [aura(15, ALL_MIL, 2)],
      "His division marched toward Gettysburg on July 1, reportedly in search of shoes, and ran into Buford's cavalry. Wounded in the head that afternoon - a wad of paper in his hat saved his life."),
    g("William D. Pender", [aura(15, "Infantry", 2, "<when attacking>")],
      "Division commander whose brigades broke the last Union line on Seminary Ridge on July 1. Mortally wounded on July 2."),
    g("Robert E. Rodes", [aura(15, ALL_MIL, 2), "[+1] Sight"],
      "Division commander who arrived on Oak Hill on July 1 and attacked the flank of the Union I Corps."),
    g("Jubal A. Early", [aura(15, ALL_MIL, 2, "<when attacking>")],
      "His division arrived from the north-east on July 1 and crushed the Union XI Corps at Barlow's Knoll."),
    g("Edward Johnson", [aura(15, ALL_MIL, 2)],
      "'Allegheny' Johnson, whose division assaulted Culp's Hill on the night of July 2 and again on July 3."),
    g("Richard H. Anderson", [aura(15, ALL_MIL, 2)],
      "Division commander whose brigades struck the Union center on July 2 and briefly reached Cemetery Ridge."),
    g("Lafayette McLaws", [aura(15, ALL_MIL, 2)],
      "Division commander whose brigades - Kershaw, Barksdale, Semmes, Wofford - overran the Peach Orchard and the Wheatfield on July 2."),
    g("John B. Hood", [aura(20, "Infantry", 2, "<when attacking>")],
      "Commander of the division that attacked Devil's Den and Little Round Top on July 2. A shell fragment crippled his arm early in the assault."),
    g("George E. Pickett", [aura(15, "Infantry", 2, "<when attacking>")],
      "His fresh Virginia division led the grand assault on the Union center on July 3. 'General Lee, I have no division,' he is said to have answered afterward."),
    g("J. E. B. Stuart", [aura(25, "Cavalry", 2), "[+1] Movement", "[+1] Sight"],
      "Lee's flamboyant cavalry chief. His long raid around the Union army meant he reached Gettysburg only on the evening of July 2."),
    g("E. Porter Alexander", [aura(25, "Artillery", 3)],
      "Colonel commanding Longstreet's artillery; he directed the great bombardment of July 3, the largest of the war."),
]

if __name__ == "__main__":
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    with open(os.path.join(root, "jsons", "UnitPromotions.json"), "w") as f:
        json.dump(PROMOS + STATUS + GENERALS, f, indent=4)
    print("Wrote %d promotions" % (len(PROMOS) + len(STATUS) + len(GENERALS)))
