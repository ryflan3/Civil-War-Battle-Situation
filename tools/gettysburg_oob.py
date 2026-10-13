"""Order of battle and arrival timetable for the Gettysburg scenario.

Turn numbers are Unciv's turn counter (shown in the top bar). Turn 0 = 7:00 AM, July 1, 1863.
Each daylight turn is about one hour; each night is compressed into two turns.

Everything else (Buildings.json arrival timetables, UnitNameGroups.json, the scenario save)
is generated from this file, so edit the battle here.

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


LAST_TURN = 47  # 7:00 PM, July 3 - "Hold the Field" is decided from here on

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
    return names


if __name__ == "__main__":
    n = check()
    print("OK - %d named units, %d arrival lines" % (len(n), len(ARRIVALS)))
    for side in ("Union", "Confederacy"):
        total = sum(len(a[4]) for a in ARRIVALS if a[1] == side) + sum(1 for s in START if s[0] == side)
        print(side, total, "units")
