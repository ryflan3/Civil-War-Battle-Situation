"""Generates the Gettysburg scenario's clock and its historical messages:
  jsons/TileResources.json  the clock in the top bar: the day of July and the hour, as two counters
  jsons/Events.json         the pop-up messages: each army's opening briefing and orders, and the history of the battle
                            hour by hour
  jsons/GlobalUniques.json  the uniques that run them (the rest of that file is hand-written and kept as it is)

How it works: at the end of each turn, every army sets its clock to the next turn's time and queues the next turn's
messages, which pop up when that turn starts. Turn 0 is set up by the scenario builder (tools/cwtool ScenarioBuilder.kt):
it starts the clock at 7 AM, July 1 and queues each army's opening briefing. Unciv's New Game screen starts a
scenario with an odd turn count, so nothing here runs at turn start.

The history messages can be switched off from any of them (the [History off] counter); the last-light reminder
on turn 46 always shows. Everything only runs in the scenario (the [Gettysburg Scenario] buildings exist there only).
Run from the repository root:  python3 tools/gen_events.py
"""
import json, os, sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import gettysburg_oob as oob
from gen_buildings import SCENARIO_TAG

DAY, HOUR, HISTORY_OFF = "July", "Hour", "History off"   # counters; DAY and HOUR are also in ScenarioBuilder.kt
IN_SCENARIO = "<if [%s] is constructed>" % SCENARIO_TAG
HISTORY_ON = "<when number of [%s] is less than [1]>" % HISTORY_OFF
LAST_CLOCK_TURN = 60     # the scenario's maxTurns


def event_name(key):
    return "Gettysburg: " + key


def opening_event(side):   # queued by ScenarioBuilder.kt for turn 0: "Gettysburg: Union briefing"
    return event_name("%s briefing" % side)


# ---------------------------------------------------------------- facts taken from the order of battle

def hq(side):
    return next(e[0] for e in oob.ENTRIES if e[1] == side and e[4])


def positions(side):
    return [o[0] for o in oob.OBJECTIVES if o[1] == side]


def names(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def turns(side, entry, first, last):
    """'turns 3-6' for the arrivals of a side on a road between two turns; fails if the timetable changed."""
    ts = sorted({a[0] for a in oob.timetable() if a[1] == side and a[2] == entry and first <= a[0] <= last})
    assert ts and ts[0] == first and ts[-1] == last, (side, entry, first, last, ts)
    return "turn %d" % first if first == last else "turns %d-%d" % (first, last)


def p(text, **kw):
    return dict(text=text, **kw)


def header(text):
    return p(text, header=3)


SEP = {"separator": True}
CONTINUE = {"text": "Continue"}
HISTORY_OFF_CHOICE = {"text": "Continue (no more history messages)",
                      "uniques": ["Set [%s] to [1] <hidden from users>" % HISTORY_OFF]}

# ---------------------------------------------------------------- turn 0: briefing and orders, one pair per army

OTHER = {"Union": "Confederacy", "Confederacy": "Union"}
COMMANDER = {"Union": "Meade", "Confederacy": "Lee"}

BRIEFING = {
    "Union": [
        header("The Battle of Gettysburg"),
        p("General Meade: you took command of the Army of the Potomac three days ago. Lee's Army of Northern Virginia "
          "has invaded Pennsylvania, and your seven infantry corps are strung out across northern Maryland, keeping "
          "between Lee and Washington and Baltimore."),
        p("At dawn, John Buford's cavalry division holds the ridges west of Gettysburg, a market town where ten roads "
          "meet. A Confederate division under Henry Heth is marching down the Chambersburg Pike toward it. Buford's "
          "troopers will fight on foot with their breech-loading carbines and try to hold until John Reynolds brings "
          "up the I Corps."),
        p("Lee's corps are converging on Gettysburg from the west and the north. Most of yours are still hours away. "
          "Today is a race."),
    ],
    "Confederacy": [
        header("The Battle of Gettysburg"),
        p("General Lee: after your victory at Chancellorsville, the Army of Northern Virginia has carried the war into "
          "Pennsylvania. But Jeb Stuart's cavalry is off riding around the Union army, and you are marching blind."),
        p("This morning Henry Heth's division of A. P. Hill's corps is marching down the Chambersburg Pike toward "
          "Gettysburg, a market town where ten roads meet, and has run into Union cavalry on the ridges west of town. "
          "Ewell's corps is coming down from the north."),
        p("You have told your generals not to bring on a general engagement until the army is concentrated. But only "
          "Buford's cavalry and the head of the Union I Corps stand in the way, and the rest of the Union army is "
          "strung out on the roads from Maryland."),
    ],
}

REINFORCEMENTS = {
    "Union": "The rest of your army marches in on its roads at its historical hours: the rest of the I Corps on the "
             "Emmitsburg Road (%s), the XI Corps on the Taneytown Road (%s), the XII Corps on the Baltimore Pike (%s) "
             "and the III Corps on the Emmitsburg Road (%s). The II, V and VI Corps, the Artillery Reserve and more "
             "cavalry follow overnight and on July 2." % (
                 turns("Union", "Emmitsburg Road", 2, 3), turns("Union", "Taneytown Road", 3, 6),
                 turns("Union", "Baltimore Pike", 9, 10), turns("Union", "Emmitsburg Road", 10, 11)),
    "Confederacy": "Most of your army is already on the field. Longstreet's corps arrives on the Chambersburg Pike on "
                   "the morning of July 2 (%s), Stuart's cavalry on the Harrisburg Road (%s) and Pickett's division on "
                   "the Chambersburg Pike that evening (%s)." % (
                       turns("Confederacy", "Chambersburg Pike", 15, 17), turns("Confederacy", "Harrisburg Road", 27, 27),
                       turns("Confederacy", "Chambersburg Pike", 30, 30)),
}

ADVICE = {
    "Union": "Advice: Buford's cavalry should delay, not die - trade ground for time until the infantry comes up. "
             "The heights south of town are where the Union army made its stand.",
    "Confederacy": "Advice: strike before the Union corps come up. Every hour you wait, more of them arrive.",
}


def orders(side):
    own, neutral, enemy = positions(side), positions(oob.NEUTRAL), positions(OTHER[side])
    held = ("You hold %s." % names(own)) if own else "You hold none of them yet; the Union holds %s." % names(enemy)
    return [
        header("Your orders, General %s" % COMMANDER[side]),
        p("Hold the Field", header=4),
        p("Seven KEY POSITIONS decide the battle: %s. At nightfall on July 3 - the end of turn %d - the army holding "
          "more of them wins." % (names(o[0] for o in oob.OBJECTIVES), oob.LAST_TURN), link="Victory/Hold the Field"),
        p("%s %s start NEUTRAL: they belong to %s, which both armies are at war with. Attack and take them - a brigade "
          "or two will do it - before the enemy does. Neutral positions count for no one."
          % (held, names(neutral), oob.NEUTRAL), link="Nation/" + oob.NEUTRAL),
        p("Decisive Victory", header=4),
        p("Capture the enemy's army headquarters at %s and the battle is won at once - but it is far stronger than any "
          "other town and needs artillery and several brigades. Lose your own, at %s, and you lose."
          % (hq(OTHER[side]), hq(side)), link="Victory/Decisive Victory"),
        SEP,
        p(REINFORCEMENTS[side]),
        p("Hold your entry towns: if the enemy takes one, the reinforcements still due on that road are lost. The "
          "'Arrivals' buildings in the Civilopedia list every unit and its turn."),
        p("The top bar shows the day of July (the calendar) and the hour on the 24-hour clock (the watch) next to the "
          "turn number. Click the turn number to see the victory status."),
        p(ADVICE[side]),
    ]


# ---------------------------------------------------------------- the battle, hour by hour (shown to both armies)
# (turn the message is shown, key, title, paragraphs)

HISTORY = [
    (3, "Reynolds falls", "Reynolds falls", [
        "Buford's dismounted troopers held Heth's division west of town for more than two hours. Around 10:15, John "
        "Reynolds led the Iron Brigade into Herbst's Woods on McPherson's Ridge and was shot from the saddle - the "
        "highest-ranking officer killed in the battle. Abner Doubleday took command of the I Corps.",
        "The Iron Brigade swept down on Archer's brigade at Willoughby Run and captured James Archer himself, the first "
        "of Lee's generals taken prisoner since Lee had taken command. North of the pike, Davis's Mississippians drove "
        "back Cutler's brigade until a Union counterattack trapped some two hundred of them in the unfinished railroad cut.",
    ]),
    (6, "Oak Hill", "The guns on Oak Hill", [
        "Oliver O. Howard, now the senior Union officer on the field, sent most of his XI Corps through the town to the "
        "fields north of it - but kept a division and its guns on Cemetery Hill as a rallying point. It was the most "
        "important decision of the day.",
        "Robert Rodes's division of Ewell's corps came down from the north onto Oak Hill and opened fire on the flank of "
        "the I Corps. Its attack went in piecemeal: Iverson's North Carolinians marched across an open field toward a "
        "stone wall on Oak Ridge where Baxter's brigade lay hidden, and lost two-thirds of their men in minutes.",
    ]),
    (9, "The Union line breaks", "The Union line breaks", [
        "Jubal Early's division came in on the Harrisburg Road and struck the XI Corps flank. Francis Barlow had pushed "
        "his division forward onto a low rise, now Barlow's Knoll; John B. Gordon's Georgians routed it, and Barlow "
        "fell badly wounded. West of town, the I Corps made its last stand at the Lutheran Seminary until Perrin's "
        "South Carolinians broke through.",
        "Both Union corps streamed back through the streets of Gettysburg, and thousands were captured in the town. On "
        "Cemetery Hill, Howard and Winfield Scott Hancock - sent ahead by Meade - rallied the survivors. Hancock called "
        "it the strongest natural position for a battle he had ever seen, and Meade ordered his whole army to Gettysburg.",
    ]),
    (10, "If practicable", "\"If practicable\"", [
        "From Seminary Ridge, Lee watched the Union rout and sent Ewell an order: take Cemetery Hill if practicable, "
        "but avoid a general engagement until the rest of the army came up.",
        "Ewell's men were tired and disorganized, Johnson's division was still on the road, and the hill bristled with "
        "Union guns. Ewell did not attack - one of the most debated decisions of the war. Meanwhile Slocum's XII Corps "
        "came up the Baltimore Pike, Sickles's III Corps the Emmitsburg Road, and Wadsworth's battered division dug in "
        "on Culp's Hill.",
    ]),
    (12, "Nightfall July 1", "Nightfall, July 1", [
        "The first day was a Confederate victory. Two Union corps had been beaten and driven through the town, losing "
        "some 9,000 men, about a third of them captured; Lee's army lost about 6,000.",
        "But the Union held the high ground south of town - Cemetery Hill and Culp's Hill - and the rest of Meade's "
        "army was marching through the night to join it.",
        "Your battle: click the turn number in the top bar to see who holds how many key positions.",
    ]),
    (13, "Meade arrives", "Meade arrives", [
        "Around midnight George Gordon Meade, in command of the Army of the Potomac for barely four days, reached "
        "Cemetery Hill and rode the lines by moonlight. He decided to stand and fight.",
        "Through the night and into the morning the Union corps closed up, and the line took the shape of a fishhook: "
        "from Culp's Hill, around Cemetery Hill and south along Cemetery Ridge toward the Round Tops. Longstreet's "
        "divisions marched through the night from Cashtown.",
    ]),
    (15, "Lee's plan", "Lee's plan for July 2", [
        "The evening before, Longstreet had urged Lee to slip around the Union left and make Meade attack them on "
        "ground of their choosing. Lee had pointed at Cemetery Hill: \"The enemy is there, and I am going to attack him "
        "there.\"",
        "His plan: Longstreet's corps would attack the Union left, moving up the Emmitsburg Road, while Ewell "
        "demonstrated against Culp's Hill and Cemetery Hill, ready to attack in earnest if the chance came. An early "
        "scouting party reported the Round Tops empty.",
        "This morning Longstreet's corps reaches the Chambersburg Pike (%s), and the Union II and V Corps come up the "
        "Taneytown and Hanover Roads (%s and %s)." % (
            turns("Confederacy", "Chambersburg Pike", 15, 17), turns("Union", "Taneytown Road", 14, 16),
            turns("Union", "Hanover Road", 17, 18)),
    ]),
    (24, "Sickles moves forward", "Sickles moves forward", [
        "Daniel Sickles disliked the low ground given to his III Corps at the south end of Cemetery Ridge. Without "
        "orders, he moved the whole corps half a mile forward to the higher ground along the Emmitsburg Road, its "
        "corner at the Peach Orchard. The new line was too long for his men and left a gap. Meade rode out to object, "
        "but the Confederate guns opened before it could be pulled back.",
        "Longstreet was late: to stay out of sight of the Union signal station on Little Round Top, his columns had "
        "countermarched for hours. The Union VI Corps, after marching some thirty-four miles through the night, came "
        "up the Baltimore Pike.",
    ]),
    (26, "Longstreet attacks", "Longstreet attacks", [
        "About 4 o'clock Hood's division went in against the Union left; Hood was wounded almost at once. Texans, "
        "Arkansans and Georgians fought through the boulders of Devil's Den and took it, while Law's Alabamians "
        "climbed Big Round Top toward Little Round Top.",
        "Gouverneur K. Warren, Meade's chief engineer, found Little Round Top held only by signalmen and sent for help. "
        "Strong Vincent's brigade reached the summit minutes ahead of the Alabamians.",
        "Jeb Stuart had reached Lee's headquarters that afternoon, after a week-long ride around the Union army that "
        "had left Lee without his cavalry's eyes.",
    ]),
    (28, "Wheatfield and Peach Orchard", "The Wheatfield and the Peach Orchard", [
        "The fighting rolled north. In the Wheatfield, brigades from three Union corps were fed in one after another, "
        "and the field changed hands again and again. Before going in, the Irish Brigade knelt to receive absolution "
        "from their chaplain, Father William Corby.",
        "At the Peach Orchard, Barksdale's Mississippians broke the III Corps salient, and a cannonball took off "
        "Sickles's leg. On Little Round Top, Joshua Chamberlain's 20th Maine, at the very end of the Union line and "
        "almost out of ammunition, fixed bayonets and charged downhill, routing the 15th Alabama.",
    ]),
    (29, "The 1st Minnesota", "The 1st Minnesota", [
        "With Sickles's line gone, Anderson's division struck at Cemetery Ridge itself. Wright's Georgians reached the "
        "crest near the Angle before being driven back.",
        "Hancock saw Wilcox's Alabamians heading for a gap in the line and ordered the 262 men of the 1st Minnesota to "
        "charge them. In a few minutes the regiment lost 215 men - 82 percent - but it bought the time to close the gap.",
    ]),
    (30, "Culp's Hill at dusk", "Dusk: Culp's Hill and East Cemetery Hill", [
        "At last Ewell attacked. Most of the XII Corps had been sent to the crumbling Union left, leaving George S. "
        "Greene's New York brigade alone on Culp's Hill behind log breastworks Greene had insisted on building. It held "
        "the summit through the dark, though Johnson's men took empty works lower on the hill.",
        "On East Cemetery Hill, the Louisiana Tigers and North Carolinians broke into the Union batteries in the "
        "twilight and fought hand to hand among the guns, until a brigade sent by Hancock drove them off. July 2 was "
        "the bloodiest day of the battle. The Union line had bent, but it had not broken.",
    ]),
    (31, "Council of war", "Council of war", [
        "Late that night Meade gathered his generals in the cramped Leister farmhouse behind Cemetery Ridge. They voted "
        "to stay and fight, and to wait for Lee to attack. As they left, Meade told John Gibbon: \"If Lee attacks "
        "tomorrow, it will be in your front.\"",
        "Lee had decided to attack again in the morning. George Pickett's fresh Virginia division had come up.",
        "Your battle: one more day. Hold the Field is decided at the end of turn %d, at 7 PM tomorrow. Click the turn "
        "number in the top bar to see the count." % oob.LAST_TURN,
    ]),
    (33, "Culp's Hill at dawn", "Culp's Hill at dawn", [
        "At first light the XII Corps, back on its hill, opened fire on Johnson's men in the captured works. The fight "
        "for Culp's Hill lasted seven hours, the longest of the battle, until the Confederates were driven off in the "
        "late morning.",
        "Longstreet was not ready to attack at the same hour, and Lee changed his plan: a massive assault on the center "
        "of the Union line, aimed at a copse of trees on Cemetery Ridge. Longstreet later wrote that he told Lee no "
        "fifteen thousand men ever arrayed for battle could take that position.",
    ]),
    (41, "The cannonade", "The great cannonade", [
        "At about 1 PM two signal guns fired, and some 150 Confederate cannon opened on Cemetery Ridge in the largest "
        "bombardment of the war. Many shells flew high and burst behind the ridge, among the reserves, the wagons and "
        "Meade's headquarters. Henry Hunt's guns answered, then fell silent to save ammunition for the infantry assault "
        "he knew was coming; the Confederates took the silence for batteries knocked out.",
        "Three miles to the east, Stuart's cavalry tried to get around the Union right and was stopped on what is now "
        "East Cavalry Field by Gregg's division and George Custer's Michigan Brigade.",
    ]),
    (43, "Pickett's Charge", "Pickett's Charge", [
        "About 3 o'clock some 12,500 men of Pickett's, Pettigrew's and Trimble's commands stepped out of the woods on "
        "Seminary Ridge and marched three-quarters of a mile across open fields toward the copse of trees and the Angle.",
        "Union guns on Cemetery Hill and Little Round Top tore at their flanks; at the fences of the Emmitsburg Road, "
        "canister and massed musketry met them. Lewis Armistead, his hat on the point of his sword, led a few hundred "
        "men over the stone wall at the Angle and fell mortally wounded among the Union guns - the high-water mark of "
        "the Confederacy. Webb's Philadelphia Brigade held, and Stannard's Vermonters swung out to fire into the "
        "attackers' flank.",
    ]),
    (44, "All my fault", "\"It is all my fault\"", [
        "Within an hour it was over: more than half of the men who made the charge were killed, wounded or captured. "
        "Garnett was dead, Kemper badly wounded; on the Union side, Hancock lay wounded too.",
        "Lee rode out to meet the survivors: \"It is all my fault.\" When he told Pickett to look to his division, "
        "Pickett is said to have answered: \"General Lee, I have no division.\"",
    ]),
    (47, "Nightfall July 3", "Nightfall, July 3", [
        "Night fell on some 50,000 men killed, wounded, captured or missing in three days - the costliest battle ever "
        "fought in North America. On July 4 Lee waited for an attack that never came, then began his retreat to "
        "Virginia in a pouring rain, his wagons of wounded strung out for miles. That same day, Vicksburg surrendered "
        "to Grant.",
        "On November 19, Abraham Lincoln dedicated a cemetery for the Union dead beside the one on Cemetery Hill, in a "
        "speech of two minutes: \"...that these dead shall not have died in vain - that this nation, under God, shall "
        "have a new birth of freedom.\"",
        "Your battle: Hold the Field is decided from the end of this turn.",
    ]),
]

# shown even with the history messages off
LAST_LIGHT = (46, "Last light", "Last light", [
    "Two turns of daylight are left: this one and turn %d (7 PM). At the end of turn %d the army holding more key "
    "positions holds the field; neutral positions count for no one. Click the turn number in the top bar to see the "
    "count." % (oob.LAST_TURN, oob.LAST_TURN),
    "Late in the afternoon of July 3, Judson Kilpatrick sent Elon Farnsworth's cavalry charging into Confederate "
    "infantry south of Big Round Top; Farnsworth was killed. Meade did not counterattack.",
])


def timed_event(turn, key, title, paragraphs, history=True):
    return {
        "name": event_name(key),
        "text": oob.turn_label(turn),
        "civilopediaText": [header(title)] + [p(x) for x in paragraphs],
        "choices": [CONTINUE, HISTORY_OFF_CHOICE] if history else [CONTINUE],
    }


def build():
    events, triggers = [], []
    for side in ("Union", "Confederacy"):
        orders_name = event_name("%s orders" % side)
        events.append({
            "name": opening_event(side),
            "text": oob.turn_label(0),
            "civilopediaText": BRIEFING[side],
            "choices": [{"text": "Your orders, General", "uniques": ["Triggers a [%s] event <hidden from users>" % orders_name]}],
        })
        events.append({
            "name": orders_name,
            "text": oob.turn_label(0),
            "civilopediaText": orders(side),
            "choices": [{"text": "To arms!"},
                        {"text": "To arms! (no history messages)", "uniques": ["Set [%s] to [1] <hidden from users>" % HISTORY_OFF]}],
        })
    for entry in HISTORY + [LAST_LIGHT]:
        turn, key, title, paragraphs = entry
        history = entry is not LAST_LIGHT
        events.append(timed_event(turn, key, title, paragraphs, history))
        when = "<upon turn end> <after turn number [%d]> <before turn number [%d]> %s" % (turn - 1, turn, IN_SCENARIO)
        triggers.append("Triggers a [%s] event %s%s" % (event_name(key), when, " " + HISTORY_ON if history else ""))
    # the clock: at the end of each turn, set it to the time of the next one
    last_day = None
    for t in range(1, LAST_CLOCK_TURN + 1):
        day, hour = oob.clock(t)
        when = "<upon turn end> <after turn number [%d]> <before turn number [%d]> %s" % (t - 1, t, IN_SCENARIO)
        if day != last_day:
            triggers.append("Set [%s] to [%d] %s" % (DAY, day, when))
            last_day = day
        triggers.append("Set [%s] to [%d] %s" % (HOUR, hour, when))
    assert len({e["name"] for e in events}) == len(events)
    return events, triggers


def resources():
    common = ["Stockpiled", "Cannot be traded"]
    return [
        {"name": DAY, "resourceType": "Strategic", "uniques": common, "civilopediaText": [
            p("The scenario's calendar: the day of July. It is shown in the top bar next to the turn number."),
            p("July 1: turns 0-12. The night of July 1-2: turns 13-14. July 2: turns 15-30. The night of July 2-3: "
              "turns 31-32. July 3: turns 33-%d." % oob.LAST_TURN)]},
        {"name": HOUR, "resourceType": "Strategic", "uniques": common, "civilopediaText": [
            p("The scenario's clock: the hour at the start of this turn, on the 24-hour clock (13 is 1 PM). It is shown "
              "in the top bar next to the turn number."),
            p("Each daylight turn is one hour, from 7 AM on July 1 and from 5 AM on July 2 and 3. Each night passes in "
              "two turns, at 11 PM and 2 AM.")]},
        {"name": HISTORY_OFF, "resourceType": "Strategic", "uniques": common + ["Not shown on world screen"],
         "civilopediaText": [p("1 when you have turned off the scenario's history messages, otherwise 0.")]},
    ]


def is_generated(unique):
    return any("[%s]" % n in unique for n in (DAY, HOUR, HISTORY_OFF)) or "[Gettysburg: " in unique


def _hand_written_style(obj):
    """JSON in the layout of the hand-written files: one unique or one Civilopedia line per line."""
    def one(v):
        return json.dumps(v, ensure_ascii=False)
    out = []
    for k, v in obj.items():
        if isinstance(v, list):
            out.append('    %s: [\n%s\n    ]' % (one(k), ",\n".join("        " + one(x) for x in v)))
        else:
            out.append('    %s: %s' % (one(k), one(v)))
    return "{\n" + ",\n".join(out) + "\n}\n"


def write():
    events, triggers = build()
    with open(os.path.join(ROOT, "jsons", "Events.json"), "w") as f:
        json.dump(events, f, indent=4, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(ROOT, "jsons", "TileResources.json"), "w") as f:
        json.dump(resources(), f, indent=4, ensure_ascii=False)
        f.write("\n")
    # GlobalUniques.json is hand-written: keep its own uniques and replace the generated ones
    path = os.path.join(ROOT, "jsons", "GlobalUniques.json")
    glob = json.load(open(path), object_pairs_hook=OrderedDict)
    glob["uniques"] = [u for u in glob["uniques"] if not is_generated(u)] + triggers
    with open(path, "w") as f:
        f.write(_hand_written_style(glob))
    print("Wrote %d events, %d clock and message triggers" % (len(events), len(triggers)))


if __name__ == "__main__":
    write()
