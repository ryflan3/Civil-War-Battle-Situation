# Civil War Battle Situation — an Unciv mod

![Civil War Battle Situation](preview.png)

A Civil War ruleset for [Unciv](https://github.com/yairm210/Unciv), starting with the **Battle of Gettysburg, July 1–3, 1863**.

* **Gettysburg scenario** – both armies at their 7:00 AM positions on July 1. Every brigade, artillery battalion and corps commander then arrives on its historical road at its historical hour: 93 Union and 77 Confederate units in total.
* **Gettysburg map** – a 34 × 37 hex map of the battlefield (about 250 yards per hex). It includes Seminary, Cemetery, McPherson's and Herr Ridges, Oak Hill, Culp's Hill and the Round Tops, Devil's Den, the Wheatfield and Peach Orchard, the town, the stone wall at the Angle, the unfinished railroad cut, Willoughby Run, Plum Run, Rock Creek and the ten roads that met at Gettysburg.
* **30 units** with original pixel art (map sprites, full-color portraits and icons), for the Union, the Confederacy and a neutral base set. Each is modeled on its real weapons and tactics, from the Springfield rifle-musket and the 12-pounder Napoleon to Berdan's Sharps rifles, Custer's Spencers and Hurt's Whitworths.
* **30 named generals** with personal abilities (Hancock the Superb, Buford's eye for ground, Hunt's artillery, Lee, Longstreet, Stuart…), plus sepia portraits of Meade and Lee.
* **15 landmarks** with their own art and history. Five of them are *key terrain* that decides who holds the field.

![The Gettysburg map](docs/gettysburg_map.png)

---

## Install

You need **Unciv 4.22.9 or newer** (the scenario was built with 4.22.9, and older versions may refuse to load it).

1. In Unciv, open **Mods** → **Download mod from URL**.
2. Paste `https://github.com/ryflan3/Civil-War-Battle-Situation` and press **Download**.
3. Unciv installs it as **Civil War Battle Situation**. Keep that folder name, because the scenario refers to the ruleset by it.

Once the repository has the `unciv-mod` topic (see *Final steps* below), it also appears in Unciv's built-in mod list.

## Play the Battle of Gettysburg

1. **New Game** → **Map Type: Scenario** → choose **Gettysburg - July 1, 1863**.
2. In the player list, set the side you want to command to **Human** and the other to **AI** (or both Human for hotseat).
3. Pick a **difficulty**. In this scenario difficulty changes the strength of AI-controlled armies: Militia −15%, Volunteers −5%, Veterans normal, Regulars +10%, Iron Brigade +20%.
4. **Start game!**

**Scale.** One hex is about 250 yards. One turn is about one hour of daylight, and each night is compressed into two turns.

| Turn | Time |
|---|---|
| 0 – 12 | July 1, 7 AM – 7 PM |
| 13 – 14 | Night of July 1–2 |
| 15 – 30 | July 2, 5 AM – 8 PM |
| 31 – 32 | Night of July 2–3 |
| 33 – 47 | July 3, 5 AM – 7 PM |

**Reinforcements** appear at the start of their turn in or next to their entry city: Taneytown Road (Meade's HQ), Emmitsburg Road, Baltimore Pike and Hanover Road for the Union; Chambersburg Pike (Lee's HQ), Middletown Road and Harrisburg Road for the Confederacy. The full timetable is in [docs/ORDER_OF_BATTLE.md](docs/ORDER_OF_BATTLE.md), and in-game in the Civilopedia under each "Arrivals" building. If the enemy captures an entry city, the reinforcements still due on that road are lost. In the scenario, cities cannot raise extra combat units: the armies are the historical ones.

**Victory**

* **Hold the Field** – from the end of turn 47 (nightfall, July 3), the army with more military units standing on the five gold-starred **key terrain** landmarks (Cemetery Hill, East Cemetery Hill, Culp's Hill, Little Round Top, the Angle) wins.
* **Decisive Victory** – capture the enemy army's headquarters at any time.

**Tactics of 1863**

* Rifle-muskets made frontal attacks costly. Fight from woods, walls, breastworks and high ground.
* Attack a unit from several sides: every extra adjacent unit adds a flanking bonus.
* Artillery must **Set Up** before firing and needs line of sight, so put it on hills.
* Generals inspire troops within range, but a general caught by the enemy is killed.

## Other ways to play

* **Custom map:** New Game → **Map Type: Custom** → map **Gettysburg** (the ruleset switches automatically). Each side starts with a Supply Train (founds an HQ), Pioneers and a small army, and builds the rest. The arrival timetable only runs in the scenario.
* **Random maps:** pick **Civil War Battle Situation** as the base ruleset on any generated map.
* **Map editor:** the Gettysburg map can be opened and edited in Unciv's map editor.

## The rules in brief

**Armies**

* **Union – Arsenal of the Union:** +15% Strength for artillery when attacking (better ammunition and Hunt's artillery organization). +5 HP healing for land units (Letterman's ambulance system). Union infantry get +10% (60 rounds per man, standardized Springfields).
* **Confederacy – Lee's Invincibles:** +15% Strength for cavalry when attacking (superb horsemen). +5 HP healing in enemy territory (foraging). Confederate infantry get +10% when attacking (the Rebel Yell).

**Unit types**

| Type | Role |
|---|---|
| Infantry | Brigades with rifle-muskets. Can build Breastworks (+50% defense) in 2 turns. |
| Skirmisher | Sharpshooters: range 2, +50% vs artillery, strong in rough terrain, usually slip away from melee. |
| Cavalry | Fast and far-seeing, can move after attacking and often withdraw. Weak when charging infantry. |
| Artillery | Must set up; entering rough terrain ends its move. Napoleons fire canister (+50% defending vs infantry and cavalry). Rifled guns have range 3 and win counter-battery duels. The Whitworth reaches 4 hexes. |
| Commander | Generals: an aura of +15% within 2 hexes, plus a personal ability. |
| Support | Supply Train (founds depots), Pioneers (breastworks, roads, clearing woods), Field Hospital / Union Ambulance Corps (heal adjacent units). |

Elite units: **Iron Brigade**, **Michigan Cavalry Brigade** (Spencer repeaters), **Texas Brigade**, **Stonewall Brigade** and the **Whitworth Battery**. Full stats are in [docs/UNITS.md](docs/UNITS.md).

**Terrain**

| Terrain | Move | Defense | Notes |
|---|---|---|---|
| Meadow (Grassland) / Fields (Plains) | 1 | – | open ground |
| Ridge | 1 | +15% | elevation 1: see and shoot over lower ground |
| Hill | 2 | +25% | elevation 1, rough |
| Woods (Forest) | 2 | +25% | blocks line of sight |
| Orchard | 1 | +10% | |
| Boulders | 3 | +50% | rough, blocks line of sight |
| Town | 2 | +30% | blocks line of sight |
| Stone Wall | 2 | +40% | |
| Farmstead | 1 | +20% | stone houses and barns |
| Railroad Cut | 2 | −25% | a trap: steep walls, nowhere to fire from |
| Marsh | 3 | −15% | |
| Creeks | – | – | crossing uses all movement, attacking across is −20%; roads have bridges |
| Roads | ⅓ | – | marching columns move three times as fast |

The landmarks (Cemetery Hill, Culp's Hill, Little Round Top, Big Round Top, Devil's Den, the Angle, the Peach Orchard, the Wheatfield, the Lutheran Seminary, Oak Hill, McPherson's Ridge, Barlow's Knoll, Benner's Hill, the town square) are special tiles with their own art, defense and elevation. Each has a Civilopedia entry with its history.

---

## Final steps for you

1. **Make the mod branch the default branch.** Unciv downloads a mod from the repository's *default* branch. This work was pushed to `claude/unciv-civil-war-mod-j2xmgj`. Either rename that branch to `main` (GitHub → *Settings* → *Branches* → rename), or open a pull request into `main` and merge it. Then make sure `main` is the default branch.
2. **Add GitHub topics** so Unciv's mod browser lists the mod: on the repository page, click the gear next to *About* and add `unciv-mod`, `unciv-mod-rulesets` and `unciv-mod-maps`.
3. **Install and test in Unciv** (see *Install* above), then play a few turns of the scenario as each side.
4. **Optional:** add a `LICENSE` file if you want others to reuse the mod (MIT or CC-BY are common for Unciv mods).

## Editing the mod

Most JSON files and **all images** are generated by the scripts in `tools/`. Edit the scripts, not the generated files, then rebuild.

| You want to change… | Edit |
|---|---|
| Unit stats and abilities | `tools/gen_units.py` |
| Promotions and generals' abilities | `tools/gen_promotions.py` |
| The order of battle, arrival times and entry roads | `tools/gettysburg_oob.py` |
| The map's geography | `tools/gettysburg_geo.py` |
| Graphics | `tools/art/*.py` |
| Nations, terrain, eras, victories, difficulties, global rules | the hand-written files in `jsons/` (`Nations.json`, `Terrains.json`, `Eras.json`, `VictoryTypes.json`, `Difficulties.json`, `GlobalUniques.json`, `ModOptions.json`, …) |

Then run:

```bash
tools/build_all.sh              # regenerate everything and run Unciv's validator
tools/build_all.sh --simulate   # ...and let the AI play the whole battle as a smoke test
```

This needs Python 3 with Pillow, Java 21 and internet access. The first run downloads the official `Unciv.jar` (4.22.9) and Gradle. The build uses the real Unciv engine to pack the texture atlas (`game.atlas`/`game.png`), write `maps/Gettysburg` and `scenarios/Gettysburg - July 1, 1863`, and run Unciv's own ruleset validator.

You can also simply start the desktop version of Unciv with this folder in its `mods` directory: it re-packs the atlas itself whenever images change.

### Repository layout

```
jsons/          ruleset (Units, UnitTypes, UnitPromotions, Nations, Terrains, Buildings, TileImprovements, ...)
jsons/TileSets/ how the HexaRealm and FantasyHex tilesets layer the new terrain
Images/         source images (unit sprites, portraits, icons, terrain overlays, leaders, emblems)
game.atlas, game.png, Atlases.json   packed textures the game loads
maps/Gettysburg                       the map (also usable in the map editor)
scenarios/Gettysburg - July 1, 1863   the scenario save
docs/           order of battle, unit reference, map picture
tools/          generators and the Unciv-engine build tool (tools/cwtool)
```

## How it was checked

* Unciv 4.22.9's own ruleset validator (the in-game "Locate mod errors" check) reports **no problems**.
* The map and the scenario were written and read back by the real Unciv 4.22.9 engine.
* The scenario was loaded the same way the New Game screen loads it, and the AI played all 48 turns from both seats. Every arrival appeared on its turn with its historical name, and the battles ended in Union victories (historically correct), with heavy Confederate losses after the July 2 attacks.

## Notes

* All graphics were drawn from scratch by the scripts in `tools/art`; no images were copied from Unciv or elsewhere. Flags are shown as the armies carried them in 1863, for historical accuracy.
* Lee's greetings *"If the enemy is there tomorrow, we must attack him"* and *"It is all my fault"* are his recorded words. The other leader lines are written for the game.
