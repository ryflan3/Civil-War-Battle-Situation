"""Order of battle and arrival timetable for the Gettysburg scenario.

Turn numbers are Unciv's turn counter (shown in the top bar). Turn 0 = 7:00 AM, July 1, 1863.
Each daylight turn is about one hour; each night is compressed into two turns.

Everything else (Buildings.json arrival timetables, UnitNameGroups.json, the scenario save)
is generated from this file, so edit the battle here: the key positions (objective cities), the
opening deployment and the reinforcement timetable.

Positions are in miles relative to the town square of Gettysburg (the Diamond):
x = miles east, y = miles north.
"""

# ---------------------------------------------------------------- time

def turn_label(t):
    """Human readable time of day for a turn number."""
    if t <= 12:
        return "%s, July 1" % _hour(7 + t)
    if t in (13, 14):
        return "Night of July 1-2"
    if t <= 30:
        return "%s, July 2" % _hour(5 + t - 15)
    if t in (31, 32):
        return "Night of July 2-3"
    return "%s, July 3" % _hour(5 + t - 33)


def _hour(h):
    suffix = "AM" if h < 12 else "PM"
    h12 = h if h <= 12 else h - 12
    return "%d:00 %s" % (h12, suffix)


LAST_TURN = 47  # 7:00 PM, July 3 - "Hold the Field" (more key positions held) is decided from here on

# ---------------------------------------------------------------- unit type keys

U = {
    "INF": "Union Infantry", "IRON": "Iron Brigade", "SS": "US Sharpshooters", "CAV": "Union Cavalry",
    "MICH": "Michigan Cavalry Brigade", "NAP": "Union Napoleon Battery", "RIF": "Union Ordnance Rifles",
    "HA": "US Horse Artillery", "GEN": "Union General", "AMB": "Ambulance Corps",
}
C = {
    "INF": "Confederate Infantry", "TEX": "Texas Brigade", "STONE": "Stonewall Brigade", "SS": "Confederate Sharpshooters",
    "CAV": "Confederate Cavalry", "NAP": "Confederate Napoleon Battery", "PAR": "Confederate Parrott Rifles",
    "WHIT": "Whitworth Battery", "HA": "Stuart Horse Artillery", "GEN": "Confederate General", "HOSP": "Field Hospital",
}

# ---------------------------------------------------------------- entry points (cities)
# (name, side, x, y, is_capital, description)

ENTRIES = [
    ("Taneytown Road", "Union", -0.22, -3.45, True,
     "Meade's headquarters and the road from Taneytown, Maryland. The II Corps, XI Corps and the Artillery Reserve came up this road."),
    ("Emmitsburg Road", "Union", -1.95, -3.40, False,
     "The road from Emmitsburg, Maryland. The I Corps and III Corps marched up it on July 1."),
    ("Baltimore Pike", "Union", 1.20, -2.95, False,
     "The turnpike from Baltimore and the army's supply line. The XII Corps and the VI Corps arrived by it."),
    ("Hanover Road", "Union", 1.50, 0.05, False,
     "The road from Hanover. The V Corps and Gregg's cavalry division came in from the east."),
    ("Chambersburg Pike", "Confederacy", -2.45, 0.30, True,
     "Lee's line of advance from Cashtown and the Cumberland Valley. Hill's and Longstreet's corps came down this pike."),
    ("Middletown Road", "Confederacy", -0.95, 1.50, False,
     "The road from Middletown (Biglerville). Rodes's division arrived by it at Oak Hill around noon on July 1."),
    ("Harrisburg Road", "Confederacy", 0.70, 1.50, False,
     "The road from Heidlersburg and Harrisburg. Early's and Johnson's divisions and Stuart's cavalry came in from the north-east."),
]

# ---------------------------------------------------------------- key positions (objective cities)
# The scenario founds a city on each of these landmarks. All of them start in Union hands: on the morning of
# July 1 Buford's cavalry screened the town and the ridges, and the rest lay behind the Union lines.
# Cities cannot be razed. The army holding more of them at nightfall on July 3 (end of turn 47) wins "Hold the Field".
OBJECTIVE_BUILDING = "Key Position"
OBJECTIVES = [  # (landmark = city name, side at the start, why it mattered)
    ("Oak Hill", "Union",
     "The high ground north of town. Rodes's guns on Oak Hill raked the Union I Corps line on the afternoon of July 1."),
    ("Lutheran Seminary", "Union",
     "Buford watched Heth's approach from the seminary cupola, and the I Corps made its last stand on Seminary Ridge on July 1."),
    ("Gettysburg", "Union",
     "Ten roads met in the town square. Whoever held the town held the roads both armies needed."),
    ("Cemetery Hill", "Union",
     "The key to the whole field, where the beaten Union corps rallied on the evening of July 1."),
    ("Culp's Hill", "Union",
     "The barb of the Union fishhook, guarding the Baltimore Pike - the army's line of supply and retreat."),
    ("The Angle", "Union",
     "The bend in the stone wall on Cemetery Ridge, where Pickett's Charge struck the Union centre on July 3."),
    ("Little Round Top", "Union",
     "The rocky hill anchoring the Union left. Had it fallen on July 2, Confederate guns could have swept the whole line."),
]

# ---------------------------------------------------------------- units on the field at 7:00 AM, July 1
# (side, type key, instance name or None, x, y)

START = [
    ("Union", "CAV", "Gamble's Brigade (Buford)", -1.15, -0.10),
    ("Union", "CAV", "Devin's Brigade (Buford)", -1.08, 0.45),
    ("Union", "HA", "Calef's Battery (A, 2nd US)", -1.12, 0.15),
    ("Union", "GEN", "John Buford", -0.62, 0.00),
    ("Confederacy", "INF", "Archer's Brigade (Heth)", -2.10, -0.05),
    ("Confederacy", "INF", "Davis's Brigade (Heth)", -2.10, 0.42),
    ("Confederacy", "INF", "Pettigrew's Brigade (Heth)", -2.30, 0.15),
    ("Confederacy", "INF", "Brockenbrough's Brigade (Heth)", -2.32, -0.08),
    ("Confederacy", "PAR", "Pegram's Battalion", -2.05, 0.20),
    ("Confederacy", "GEN", "Henry Heth", -2.30, 0.15),
]

# ---------------------------------------------------------------- arrivals
# (turn, side, entry, type key, [instance names])  - one list entry per unit
# Rule: a given (side, unit type, turn) may only arrive at ONE entry, because the unit names
# for each turn are drawn from one shared name group.

ARRIVALS = [
    # ----- Union, July 1
    (1, "Union", "Emmitsburg Road", "GEN", ["John F. Reynolds"]),
    (1, "Union", "Emmitsburg Road", "INF", ["Cutler's Brigade (I Corps)"]),
    (1, "Union", "Emmitsburg Road", "IRON", [None]),
    (1, "Union", "Emmitsburg Road", "RIF", ["Hall's 2nd Maine Battery"]),
    (2, "Union", "Emmitsburg Road", "GEN", ["Abner Doubleday"]),
    (2, "Union", "Emmitsburg Road", "INF", ["Biddle's Brigade (I Corps)", "Stone's Bucktail Brigade (I Corps)"]),
    (2, "Union", "Emmitsburg Road", "NAP", ["I Corps Artillery (Wainwright)"]),
    (3, "Union", "Emmitsburg Road", "INF", ["Paul's Brigade (I Corps)", "Baxter's Brigade (I Corps)"]),
    (3, "Union", "Taneytown Road", "GEN", ["Oliver O. Howard"]),
    (4, "Union", "Taneytown Road", "INF", ["von Gilsa's Brigade (XI Corps)", "Ames's Brigade (XI Corps)"]),
    (5, "Union", "Taneytown Road", "INF", ["Schimmelfennig's Brigade (XI Corps)", "Krzyzanowski's Brigade (XI Corps)"]),
    (5, "Union", "Taneytown Road", "NAP", ["XI Corps Artillery (Osborn)"]),
    (6, "Union", "Taneytown Road", "INF", ["Coster's Brigade (XI Corps)", "Orland Smith's Brigade (XI Corps)"]),
    (8, "Union", "Taneytown Road", "GEN", ["Winfield S. Hancock"]),
    (9, "Union", "Baltimore Pike", "GEN", ["Henry W. Slocum"]),
    (9, "Union", "Baltimore Pike", "INF", ["McDougall's Brigade (XII Corps)", "Lockwood's Brigade (XII Corps)", "Ruger's Brigade (XII Corps)"]),
    (9, "Union", "Baltimore Pike", "RIF", ["XII Corps Artillery (Muhlenberg)"]),
    (10, "Union", "Baltimore Pike", "INF", ["Candy's Brigade (XII Corps)", "Kane's Brigade (XII Corps)", "Greene's Brigade (XII Corps)"]),
    (10, "Union", "Emmitsburg Road", "GEN", ["Daniel E. Sickles"]),
    (11, "Union", "Emmitsburg Road", "INF", ["Graham's Brigade (III Corps)", "Ward's Brigade (III Corps)", "de Trobriand's Brigade (III Corps)"]),
    (11, "Union", "Emmitsburg Road", "SS", ["Berdan's Sharpshooters (1st & 2nd USSS)"]),
    # ----- Union, night of July 1-2
    (13, "Union", "Taneytown Road", "GEN", ["George G. Meade"]),
    (13, "Union", "Emmitsburg Road", "INF", ["Carr's Brigade (III Corps)", "Brewster's Excelsior Brigade (III Corps)", "Stannard's Vermont Brigade (I Corps)"]),
    (13, "Union", "Emmitsburg Road", "NAP", ["III Corps Artillery (Randolph)"]),
    (14, "Union", "Taneytown Road", "INF", ["Cross's Brigade (II Corps)", "Kelly's Irish Brigade (II Corps)", "Zook's Brigade (II Corps)", "Brooke's Brigade (II Corps)"]),
    (14, "Union", "Taneytown Road", "NAP", ["II Corps Artillery (Hazard)"]),
    (14, "Union", "Taneytown Road", "AMB", [None]),
    # ----- Union, July 2
    (15, "Union", "Taneytown Road", "GEN", ["John Gibbon", "Gouverneur K. Warren"]),
    (15, "Union", "Taneytown Road", "INF", ["Harrow's Brigade (II Corps)", "Webb's Philadelphia Brigade (II Corps)", "Hall's Brigade (II Corps)"]),
    (16, "Union", "Taneytown Road", "INF", ["Carroll's Brigade (II Corps)", "Smyth's Brigade (II Corps)", "Willard's Brigade (II Corps)"]),
    (17, "Union", "Hanover Road", "GEN", ["George Sykes"]),
    (17, "Union", "Hanover Road", "INF", ["Tilton's Brigade (V Corps)", "Sweitzer's Brigade (V Corps)", "Vincent's Brigade (V Corps)"]),
    (18, "Union", "Hanover Road", "INF", ["Day's U.S. Regulars (V Corps)", "Burbank's U.S. Regulars (V Corps)", "Weed's Brigade (V Corps)"]),
    (18, "Union", "Hanover Road", "RIF", ["V Corps Artillery (Martin)"]),
    (19, "Union", "Emmitsburg Road", "INF", ["Burling's Brigade (III Corps)"]),
    (20, "Union", "Taneytown Road", "GEN", ["Henry J. Hunt"]),
    (20, "Union", "Taneytown Road", "NAP", ["1st Volunteer Brigade, Artillery Reserve (McGilvery)"]),
    (20, "Union", "Taneytown Road", "RIF", ["1st Regular Brigade, Artillery Reserve (Ransom)", "2nd Volunteer Brigade, Artillery Reserve (Taft)"]),
    (21, "Union", "Taneytown Road", "NAP", ["3rd Volunteer Brigade, Artillery Reserve (Huntington)"]),
    (21, "Union", "Taneytown Road", "RIF", ["4th Volunteer Brigade, Artillery Reserve (Fitzhugh)"]),
    (22, "Union", "Hanover Road", "GEN", ["David M. Gregg"]),
    (22, "Union", "Hanover Road", "INF", ["McCandless's Pennsylvania Reserves (V Corps)", "Fisher's Pennsylvania Reserves (V Corps)"]),
    (22, "Union", "Hanover Road", "CAV", ["McIntosh's Brigade (Gregg)", "Irvin Gregg's Brigade (Gregg)"]),
    (22, "Union", "Hanover Road", "HA", ["Randol's Battery (E & G, 1st US)"]),
    (24, "Union", "Baltimore Pike", "GEN", ["John Sedgwick"]),
    (24, "Union", "Baltimore Pike", "INF", ["Torbert's New Jersey Brigade (VI Corps)", "Bartlett's Brigade (VI Corps)", "Russell's Brigade (VI Corps)"]),
    (24, "Union", "Baltimore Pike", "AMB", [None]),
    (25, "Union", "Baltimore Pike", "INF", ["Grant's Vermont Brigade (VI Corps)", "Neill's Brigade (VI Corps)"]),
    (26, "Union", "Baltimore Pike", "INF", ["Shaler's Brigade (VI Corps)", "Eustis's Brigade (VI Corps)", "Wheaton's Brigade (VI Corps)"]),
    (26, "Union", "Baltimore Pike", "NAP", ["VI Corps Artillery (Tompkins)"]),
    # ----- Union, July 3
    (33, "Union", "Hanover Road", "MICH", [None]),
    (33, "Union", "Hanover Road", "HA", ["Pennington's Battery (M, 2nd US)"]),
    (36, "Union", "Taneytown Road", "GEN", ["Judson Kilpatrick"]),
    (36, "Union", "Taneytown Road", "CAV", ["Farnsworth's Brigade (Kilpatrick)"]),
    (38, "Union", "Emmitsburg Road", "CAV", ["Merritt's Reserve Brigade (Buford)"]),
    (38, "Union", "Emmitsburg Road", "HA", ["Graham's Battery (K, 1st US)"]),

    # ----- Confederacy, July 1
    (1, "Confederacy", "Chambersburg Pike", "GEN", ["A. P. Hill"]),
    (2, "Confederacy", "Chambersburg Pike", "GEN", ["William D. Pender"]),
    (2, "Confederacy", "Chambersburg Pike", "INF", ["Perrin's Brigade (Pender)", "Lane's Brigade (Pender)", "Thomas's Brigade (Pender)", "Scales's Brigade (Pender)"]),
    (2, "Confederacy", "Chambersburg Pike", "NAP", ["McIntosh's Battalion"]),
    (2, "Confederacy", "Chambersburg Pike", "WHIT", [None]),
    (4, "Confederacy", "Middletown Road", "GEN", ["Robert E. Rodes", "Richard S. Ewell"]),
    (4, "Confederacy", "Middletown Road", "INF", ["Daniel's Brigade (Rodes)", "Iverson's Brigade (Rodes)", "O'Neal's Brigade (Rodes)"]),
    (4, "Confederacy", "Middletown Road", "PAR", ["Carter's Battalion"]),
    (5, "Confederacy", "Middletown Road", "INF", ["Doles's Brigade (Rodes)", "Ramseur's Brigade (Rodes)"]),
    (5, "Confederacy", "Middletown Road", "SS", ["Blackford's Sharpshooters (Rodes)"]),
    (5, "Confederacy", "Chambersburg Pike", "GEN", ["Robert E. Lee"]),
    (6, "Confederacy", "Harrisburg Road", "GEN", ["Jubal A. Early"]),
    (6, "Confederacy", "Harrisburg Road", "INF", ["Gordon's Brigade (Early)", "Hays's Louisiana Tigers (Early)"]),
    (6, "Confederacy", "Harrisburg Road", "NAP", ["Jones's Battalion"]),
    (7, "Confederacy", "Harrisburg Road", "INF", ["Avery's Brigade (Early)", "Extra Billy Smith's Brigade (Early)"]),
    (7, "Confederacy", "Harrisburg Road", "CAV", ["Jenkins's Brigade"]),
    (9, "Confederacy", "Chambersburg Pike", "GEN", ["Richard H. Anderson"]),
    (9, "Confederacy", "Chambersburg Pike", "INF", ["Wilcox's Brigade (Anderson)", "Wright's Brigade (Anderson)", "Mahone's Brigade (Anderson)"]),
    (9, "Confederacy", "Chambersburg Pike", "NAP", ["Lane's Battalion (Sumter Artillery)"]),
    (9, "Confederacy", "Chambersburg Pike", "HOSP", [None]),
    (10, "Confederacy", "Chambersburg Pike", "INF", ["Perry's Florida Brigade (Anderson)", "Posey's Brigade (Anderson)"]),
    (10, "Confederacy", "Chambersburg Pike", "NAP", ["Poague's Battalion"]),
    (10, "Confederacy", "Chambersburg Pike", "PAR", ["Garnett's Battalion"]),
    (12, "Confederacy", "Harrisburg Road", "GEN", ["Edward Johnson"]),
    (12, "Confederacy", "Harrisburg Road", "INF", ["Steuart's Brigade (Johnson)", "Nicholls's Louisiana Brigade (Johnson)", "J. M. Jones's Brigade (Johnson)"]),
    (12, "Confederacy", "Harrisburg Road", "STONE", [None]),
    (12, "Confederacy", "Harrisburg Road", "PAR", ["Latimer's Battalion"]),
    # ----- Confederacy, night of July 1-2
    (13, "Confederacy", "Harrisburg Road", "PAR", ["Dance's Battalion"]),
    (13, "Confederacy", "Harrisburg Road", "NAP", ["Nelson's Battalion"]),
    # ----- Confederacy, July 2
    (15, "Confederacy", "Chambersburg Pike", "GEN", ["James Longstreet", "Lafayette McLaws"]),
    (15, "Confederacy", "Chambersburg Pike", "INF", ["Kershaw's Brigade (McLaws)", "Barksdale's Brigade (McLaws)", "Semmes's Brigade (McLaws)", "Wofford's Brigade (McLaws)"]),
    (15, "Confederacy", "Chambersburg Pike", "PAR", ["Cabell's Battalion"]),
    (15, "Confederacy", "Chambersburg Pike", "HOSP", [None]),
    (16, "Confederacy", "Chambersburg Pike", "GEN", ["John B. Hood"]),
    (16, "Confederacy", "Chambersburg Pike", "TEX", [None]),
    (16, "Confederacy", "Chambersburg Pike", "INF", ["G. T. Anderson's Brigade (Hood)", "Benning's Brigade (Hood)"]),
    (16, "Confederacy", "Chambersburg Pike", "NAP", ["Henry's Battalion"]),
    (16, "Confederacy", "Chambersburg Pike", "SS", ["Hood's Division Sharpshooters"]),
    (17, "Confederacy", "Chambersburg Pike", "GEN", ["E. Porter Alexander"]),
    (17, "Confederacy", "Chambersburg Pike", "PAR", ["Alexander's Battalion"]),
    (17, "Confederacy", "Chambersburg Pike", "NAP", ["Washington Artillery of New Orleans (Eshleman)"]),
    (21, "Confederacy", "Chambersburg Pike", "INF", ["Law's Alabama Brigade (Hood)"]),
    (27, "Confederacy", "Harrisburg Road", "GEN", ["J. E. B. Stuart"]),
    (27, "Confederacy", "Harrisburg Road", "CAV", ["Hampton's Brigade (Stuart)", "Fitz Lee's Brigade (Stuart)", "Chambliss's Brigade (Stuart)"]),
    (27, "Confederacy", "Harrisburg Road", "HA", ["Beckham's Stuart Horse Artillery"]),
    # ----- Confederacy, evening of July 2 (Pickett deploys for July 3)
    (30, "Confederacy", "Chambersburg Pike", "GEN", ["George E. Pickett"]),
    (30, "Confederacy", "Chambersburg Pike", "INF", ["Garnett's Brigade (Pickett)", "Kemper's Brigade (Pickett)", "Armistead's Brigade (Pickett)"]),
    (30, "Confederacy", "Chambersburg Pike", "PAR", ["Dearing's Battalion"]),
]

# ---------------------------------------------------------------- opening deployment
# To make the battle big from the first turn, every force that reached the field on July 1 (arrivals up to
# OPENING_CUTOFF) starts the scenario on the map instead of arriving later: the day's marches are compressed.
# Each group takes the arrivals of one side on one road between two turns, and is placed along its anchor line
# (miles), earliest arrivals first, filling the nearest free tiles. Later arrivals keep their timetable.
OPENING_CUTOFF = 12
OPENING = [  # (side, road, first turn, last turn, label, anchor line)
    ("Union", "Emmitsburg Road", 1, 1, "Wadsworth's division of the I Corps, coming up behind Buford",
     [(-0.80, -0.30), (-0.88, 0.05)]),
    ("Union", "Emmitsburg Road", 2, 3, "The rest of the I Corps on the Emmitsburg Road",
     [(-0.42, -0.98), (-0.65, -1.40), (-0.98, -1.85)]),
    ("Union", "Emmitsburg Road", 10, 12, "Sickles's III Corps marching up from Emmitsburg",
     [(-1.22, -2.25), (-1.50, -2.75), (-1.80, -3.15)]),
    ("Union", "Taneytown Road", 3, 8, "Howard's XI Corps on the Taneytown Road",
     [(-0.08, -1.10), (-0.12, -1.70), (-0.16, -2.30), (-0.20, -2.90)]),
    ("Union", "Baltimore Pike", 9, 10, "Slocum's XII Corps on the Baltimore Pike",
     [(0.48, -1.35), (0.70, -1.85), (0.95, -2.40)]),
    ("Confederacy", "Chambersburg Pike", 1, 5, "Hill, Pender's division and Lee, behind Heth on Herr Ridge",
     [(-2.25, 0.75), (-2.30, -0.45)]),
    ("Confederacy", "Chambersburg Pike", 9, 10, "Anderson's division along the Fairfield Road",
     [(-1.85, -0.72), (-2.30, -0.90), (-2.55, -1.05)]),
    ("Confederacy", "Middletown Road", 4, 5, "Ewell and Rodes's division north of Oak Hill",
     [(-0.65, 1.55), (-0.95, 1.40), (-1.25, 1.40), (-1.55, 1.55)]),
    ("Confederacy", "Harrisburg Road", 6, 7, "Early's division on the Harrisburg Road",
     [(0.55, 1.35), (0.80, 1.55), (1.05, 1.50)]),
    ("Confederacy", "Harrisburg Road", 12, 12, "Johnson's division, east of Early",
     [(1.15, 1.30), (1.40, 1.15)]),
]


def opening_group(turn, side, entry):
    """The OPENING group an arrival belongs to, or None if it keeps its place in the timetable."""
    if turn > OPENING_CUTOFF:
        return None
    for g in OPENING:
        if g[0] == side and g[1] == entry and g[2] <= turn <= g[3]:
            return g
    raise ValueError("no opening group for %s on the %s, turn %d" % (side, entry, turn))


def timetable():
    """Arrivals that still come in during the scenario (after the opening deployment)."""
    return [a for a in ARRIVALS if a[0] > OPENING_CUTOFF]


# Free-play name pools for generals (used outside the scenario)
FREE_PLAY_GENERALS = {
    "Union": ["George G. Meade", "John F. Reynolds", "Winfield S. Hancock", "Oliver O. Howard", "Abner Doubleday",
              "Daniel E. Sickles", "Henry W. Slocum", "George Sykes", "John Sedgwick", "John Gibbon", "John Buford",
              "Gouverneur K. Warren", "Henry J. Hunt", "David M. Gregg", "Judson Kilpatrick"],
    "Confederacy": ["Robert E. Lee", "James Longstreet", "Richard S. Ewell", "A. P. Hill", "Henry Heth", "William D. Pender",
                    "Robert E. Rodes", "Jubal A. Early", "Edward Johnson", "Richard H. Anderson", "Lafayette McLaws",
                    "John B. Hood", "George E. Pickett", "J. E. B. Stuart", "E. Porter Alexander"],
}


def unit_name(side, key):
    return (U if side == "Union" else C)[key]


def check():
    """Sanity checks on the timetable."""
    seen = {}
    names = set()
    for turn, side, entry, key, inst in ARRIVALS:
        assert key in (U if side == "Union" else C), (side, key)
        assert any(e[0] == entry and e[1] == side for e in ENTRIES), entry
        k = (side, key, turn)
        if k in seen and seen[k] != entry:
            raise ValueError("%s arrives at two entries on turn %d" % (k, turn))
        seen[k] = entry
        for n in inst:
            if n is None:
                continue
            assert n not in names, "duplicate name " + n
            names.add(n)
    for side, key, inst, x, y in START:
        if inst:
            assert inst not in names, inst
            names.add(inst)
    for turn, side, entry, key, inst in ARRIVALS:
        opening_group(turn, side, entry)  # raises if an early arrival has no place in the opening deployment
    return names


if __name__ == "__main__":
    n = check()
    print("OK - %d named units, %d arrival lines" % (len(n), len(ARRIVALS)))
    for side in ("Union", "Confederacy"):
        total = sum(len(a[4]) for a in ARRIVALS if a[1] == side) + sum(1 for s in START if s[0] == side)
        opening = sum(len(a[4]) for a in ARRIVALS if a[1] == side and a[0] <= OPENING_CUTOFF) + sum(1 for s in START if s[0] == side)
        print(side, total, "units,", opening, "on the field at the start")
