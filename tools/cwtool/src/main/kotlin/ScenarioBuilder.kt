package cwtool

import com.badlogic.gdx.files.FileHandle
import com.unciv.Constants
import com.unciv.UncivGame
import com.unciv.logic.GameInfo
import com.unciv.logic.GameStarter
import com.unciv.logic.city.managers.CityFounder
import com.unciv.logic.civilization.AlertType
import com.unciv.logic.civilization.PlayerType
import com.unciv.logic.civilization.PopupAlert
import com.unciv.logic.civilization.diplomacy.DiplomacyFlags
import com.unciv.logic.civilization.managers.quests.QuestManager
import com.unciv.logic.files.UncivFiles
import com.unciv.logic.map.HexCoord
import com.unciv.models.metadata.GameParameters
import com.unciv.models.metadata.GameSetupInfo
import com.unciv.models.metadata.Player
import com.unciv.models.ruleset.PerpetualConstruction
import com.unciv.models.ruleset.RulesetCache
import java.io.File

val VICTORIES = arrayListOf("Hold the Field", "Decisive Victory")
const val KEY_POSITION = "Key Position"  // the building that marks an objective city (gettysburg_oob.OBJECTIVE_BUILDING)
/** The city-state that holds the neutral key positions (gettysburg_oob.NEUTRAL): at war with both armies for good */
const val NEUTRAL = "Adams County"
/** The clock in the top bar (gen_events.py DAY and HOUR): the day of July and the hour. gen_events.py sets it at the end
 *  of every turn for the next one; the builder starts it at turn 0, 7 AM on July 1 (gettysburg_oob.clock(0)). */
const val CLOCK_DAY = "July"
const val CLOCK_HOUR = "Hour"
/** Each army's opening briefing (gen_events.opening_event), shown when its first turn starts */
fun openingBriefing(civ: String) = "Gettysburg: $civ briefing"

/** One scenario file per difficulty. While a scenario is selected, Unciv's New Game screen locks the game options and
 *  uses the difficulty saved in the scenario, so the difficulty (the AI armies' strength) is chosen from the scenario list. */
val SCENARIOS = linkedMapOf(
    // No four-digit year in the names: Unciv's New Game screen would display "1863" as "1,863"
    "Battle of Gettysburg" to "Veterans",
    "Battle of Gettysburg (Easiest - Militia)" to "Militia",
    "Battle of Gettysburg (Easier - Volunteers)" to "Volunteers",
    "Battle of Gettysburg (Harder - Regulars)" to "Regulars",
    "Battle of Gettysburg (Hardest - Iron Brigade)" to "Iron Brigade",
)

fun buildScenario(tilesJson: File, mapFile: File, outFile: File, difficulty: String = "Veterans") {
    initUnciv()
    val ruleset = RulesetCache[MOD]!!
    val data = com.badlogic.gdx.utils.JsonReader().parse(tilesJson.readText())
    val hasNeutral = data.get("cities").any { it.getString("civ") == NEUTRAL }

    val params = GameParameters().apply {
        baseRuleset = MOD
        mods = LinkedHashSet()
        this.difficulty = difficulty
        speed = "Battle Pace"
        startingEra = "Civil War era"
        numberOfCityStates = 0
        minNumberOfCityStates = 0
        maxNumberOfCityStates = 0
        noBarbarians = true
        noCityRazing = true  // key positions must be held, not burned
        espionageEnabled = false
        nuclearWeaponsEnabled = false
        noStartBias = false
        victoryTypes = ArrayList(VICTORIES)
        maxTurns = 60
        // The Spectator is the scenario builder's seat: NewGameScreen removes it and hands the first turn to the right side
        players = arrayListOf(Player("Union", PlayerType.Human), Player("Confederacy", PlayerType.Human), Player(Constants.spectator, PlayerType.Human))
        // the neutral key positions' owner: GameStarter sets up a city-state for it (and gives it a start, removed below)
        if (hasNeutral) players.add(Player(NEUTRAL, PlayerType.AI))
    }
    val setup = GameSetupInfo(params)
    setup.mapParameters.name = "Gettysburg"
    setup.mapFile = FileHandle(mapFile)
    val game: GameInfo = GameStarter.startNewGame(setup)
    UncivGame.Current.gameInfo = game

    val union = game.getCivilization("Union")
    val confed = game.getCivilization("Confederacy")
    val sides = listOf(confed, union)
    val neutral = if (hasNeutral) game.getCivilization(NEUTRAL) else null

    // 1. remove the default starting armies GameStarter placed on the starting locations
    for (civ in sides + listOfNotNull(neutral)) for (u in civ.units.getCivUnits().toList()) u.destroy()

    // 2. found the entry cities (capital = army headquarters first), each with its timetable building,
    //    then the key positions on their landmarks
    for (c in data.get("cities")) {
        val civ = game.getCivilization(c.getString("civ"))
        val city = CityFounder().foundCity(civ, HexCoord.of(c.getInt("x"), c.getInt("y")))
        city.name = c.getString("name")
        if (c.getBoolean("objective")) city.cityConstructions.addBuilding(KEY_POSITION)
        val arrivals = (if (civ.civID == "Union") "Union" else "Confederate") + " Arrivals: " + city.name
        if (ruleset.buildings.containsKey(arrivals)) city.cityConstructions.addBuilding(arrivals)
        // the armies' cities have a Supply Depot (the era gives every new city one); the neutral ones have no stores
        if (civ == neutral) city.cityConstructions.removeBuilding("Supply Depot")
        else if (!city.cityConstructions.isBuilt("Supply Depot")) city.cityConstructions.addBuilding("Supply Depot")
        // nothing can be raised in the scenario: produce "Nothing", so the game never stops to ask "Pick construction"
        city.cityConstructions.editQueue { clear(); add(PerpetualConstruction.Idle.name) }
        println("City ${city.name} (${civ.civID}) capital=${city.isCapital()} buildings=${city.cityConstructions.getBuiltBuildings().map { it.name }.toList()}")
    }

    // 3. at war from the first shot, and a war that cannot end in peace (minimumWarDuration in ModOptions).
    //    Declared before the armies are placed: Unciv only lets units into enemy territory once at war.
    union.diplomacyFunctions.makeCivilizationsMeet(confed)
    union.getDiplomacyManager(confed)!!.declareWar()
    // The neutral key positions must be taken by force: both armies are at war with their holder from the start.
    // Declaring the war ourselves sets the same no-peace countdown, which also disables the "Negotiate Peace" button.
    if (neutral != null) {
        for (army in sides) {
            army.diplomacyFunctions.makeCivilizationsMeet(neutral)
            army.getDiplomacyManager(neutral)!!.declareWar()
            neutral.getDiplomacyManager(army)!!.removeFlag(DiplomacyFlags.RecentlyAttacked)
        }
        // A declaration of war makes a city-state ask everyone else for help ("War against [Confederacy]: kill 3 of
        // their units"). Both armies are at war with Adams County, so that request means nothing here: drop it.
        val requests = QuestManager::class.java.getDeclaredField("unitsToKillForCiv").apply { isAccessible = true }
        (requests.get(neutral.questManager) as MutableMap<*, *>).clear()
    }

    // 4. the armies on the field at the start: the 7:00 AM positions and the opening deployment
    for (u in data.get("startUnits")) {
        val civ = game.getCivilization(u.getString("civ"))
        val unit = civ.units.placeUnitNearTile(HexCoord.of(u.getInt("x"), u.getInt("y")), u.getString("unit"))
            ?: error("could not place ${u.getString("name")}")
        val name = u.getString("name", null)
        if (name != null) {
            unit.instanceName = name
            game.unitNamesTaken.add(name)
            if (ruleset.unitPromotions.containsKey(name)) unit.promotions.addPromotion(name, true)
        }
        unit.currentMovement = unit.getMaxMovement().toFloat()
        val wanted = HexCoord.of(u.getInt("x"), u.getInt("y"))
        if (unit.currentTile.position != wanted) error("${unit.name} '${unit.instanceName}' landed on ${unit.currentTile.position}, not $wanted")
    }
    println("Placed ${data.get("startUnits").size} units")

    // 5. both commanders have maps of the country: reveal the terrain (units stay hidden by fog of war)
    for (tile in game.tileMap.values) for (civ in sides) tile.setExplored(civ, true)

    game.gameParameters.victoryTypes = ArrayList(VICTORIES)
    // Default seats on the New Game screen: you command the Union against an AI Lee (the Human/AI buttons swap sides).
    // Set only now: Unciv records the explored area (the camera's scroll limits) for human players only, and either
    // side may end up human.
    confed.playerType = PlayerType.AI
    game.gameParameters.players.first { it.chosenCiv == "Confederacy" }.playerType = PlayerType.AI
    // The neutral civ is not a seat: off the New Game screen's player list, it stays AI-run
    game.gameParameters.players.removeIf { it.chosenCiv == NEUTRAL }
    game.currentPlayer = Constants.spectator
    // Update sight first, then clear: updating adds first-contact messages. The Spectator seat must meet both armies
    // here too, or it meets them when the New Game screen loads the file and the Union is told "We have encountered Spectator!"
    for (civ in game.civilizations) civ.cache.updateSightAndResources()
    for (civ in game.civilizations) {
        civ.popupAlerts.clear()
        civ.notifications.clear()
    }
    // Turn 0's clock and briefings are set here, not by "upon turn start" uniques: when the New Game screen starts a
    // scenario, the first turn starts with the turn counter still at 1.
    for (civ in sides) {
        civ.resourceStockpiles.add(CLOCK_DAY, 1)
        civ.resourceStockpiles.add(CLOCK_HOUR, 7)
        civ.popupAlerts.add(PopupAlert(AlertType.Event, openingBriefing(civ.civID)))
    }
    outFile.parentFile.mkdirs()
    outFile.writeText(UncivFiles.gameInfoToString(game, forceZip = true))
    println("Scenario written: ${outFile.path} (${outFile.length()} bytes, $difficulty). Civs: ${game.civilizations.map { it.civID }}, current=${game.currentPlayer}, turn=${game.turns}")
}

/** Loads the scenario exactly like NewGameScreen does, then plays [turns] turns. The human side's moves are made by the AI too. */
fun simulateScenario(scenarioFile: File, turns: Int, humanSide: String = "Union", historyOff: Boolean = false) {
    initUnciv()
    val game = UncivFiles.gameInfoFromString(scenarioFile.readText())
    UncivGame.Current.gameInfo = game
    // --- same steps as NewGameScreen.startNewGame for scenarios
    game.civilizations.removeIf { it.civID == Constants.spectator }
    for (civ in game.civilizations) { civ.playerType = PlayerType.AI; civ.diplomacy.remove(Constants.spectator) }
    game.getCivilization(humanSide).playerType = PlayerType.Human
    // as if the player chose "no history messages" in the opening orders (gen_events.HISTORY_OFF)
    if (historyOff) game.getCivilization(humanSide).resourceStockpiles.add("History off", 1)
    if (game.currentPlayer == Constants.spectator) { game.currentPlayer = ""; game.nextTurn(); game.turns-- }
    println("Start: current=${game.currentPlayer} turn=${game.turns} human=$humanSide" +
        " clock=July ${game.getCivilization(humanSide).resourceStockpiles[CLOCK_DAY]}, ${game.getCivilization(humanSide).resourceStockpiles[CLOCK_HOUR]}:00" +
        " popups=${game.getCivilization(humanSide).popupAlerts.map { "${it.type}(${it.value})" }}")
    val union = game.getCivilization("Union")
    val confed = game.getCivilization("Confederacy")
    println("  at war: ${union.isAtWarWith(confed)}, barbarians in game: ${game.civilizations.any { it.isBarbarian }}, razing allowed: ${!game.gameParameters.noCityRazing}")
    for (civ in listOf(union, confed)) {
        val explored = game.tileMap.values.count { it.isExplored(civ) }
        val enemy = if (civ == union) confed else union
        val enemyUnitsSeen = enemy.units.getCivUnits().count { civ.viewableTiles.contains(it.currentTile) }
        println("  ${civ.civID}: ${civ.units.getCivUnits().count()} units, explored ${explored}/${game.tileMap.values.size} tiles, sees ${enemyUnitsSeen}/${enemy.units.getCivUnits().count()} enemy units, key positions ${keyPositions(civ)}")
    }
    val neutral = game.getCivilizationOrNull(NEUTRAL)
    if (neutral != null) println("  $NEUTRAL (neutral): key positions ${keyPositions(neutral)}, at war with Union ${union.isAtWarWith(neutral)}, with Confederacy ${confed.isAtWarWith(neutral)}")
    val human = game.getCivilization(humanSide)
    var lastNames = game.civilizations.associate { it.civID to it.units.getCivUnits().map { u -> u.instanceName ?: u.name }.toList() }
    val totalLost = HashMap<String, Int>()
    val keysHeld = game.civilizations.associate { it.civID to keyPositions(it) }.toMutableMap()
    for (t in 1..turns) {
        com.unciv.logic.civilization.managers.TurnManager(human).automateTurn()
        game.nextTurn()
        // the pop-ups the human player would have to click through this turn
        if (human.popupAlerts.isNotEmpty()) println("  popups for $humanSide: ${human.popupAlerts.map { "${it.type}(${it.value.take(30)})" }}")
        human.popupAlerts.clear()
        val line = StringBuilder("Turn ${game.turns} (July ${human.resourceStockpiles[CLOCK_DAY]}, ${human.resourceStockpiles[CLOCK_HOUR]}:00):")
        for (civ in game.civilizations.filter { it.isMajorCiv() }) {
            val names = civ.units.getCivUnits().map { u -> u.instanceName ?: u.name }.toList()
            val new = names.toMutableList().apply { lastNames[civ.civID].orEmpty().forEach { remove(it) } }
            val lost = lastNames[civ.civID].orEmpty().toMutableList().apply { names.forEach { remove(it) } }
            totalLost[civ.civID] = (totalLost[civ.civID] ?: 0) + lost.size
            val mil = civ.units.getCivUnits().count { it.isMilitary() }
            line.append(" | ${civ.civID}: units=${names.size} mil=$mil lost=${lost.size} (total ${totalLost[civ.civID]}) cities=${civ.cities.size} keys=${keyPositions(civ).size}")
            if (new.isNotEmpty()) line.append(" NEW=${new.size}")
        }
        println(line)
        for (civ in game.civilizations.filter { it.isMajorCiv() })
            for (n in civ.notifications.map { it.text }.filter { listOf("destroyed", "disband", "killed", "captured", "lost", "defeated").any { k -> it.contains(k, true) } }.distinct().take(12))
                println("    [${civ.civID}] $n")
        lastNames = game.civilizations.associate { it.civID to it.units.getCivUnits().map { u -> u.instanceName ?: u.name }.toList() }
        for (civ in game.civilizations.filter { it.isMajorCiv() }) {
            val now = keyPositions(civ)
            val gained = now - keysHeld[civ.civID].orEmpty().toSet()
            if (gained.isNotEmpty()) println("    ${civ.civID} took $gained")
            keysHeld[civ.civID] = now
        }
        val victory = game.victoryData
        if (victory != null) {
            println("VICTORY: ${victory.winningCiv} by ${victory.victoryType} on turn ${victory.victoryTurn}; key positions " +
                game.civilizations.filter { it.isMajorCiv() }.joinToString { "${it.civID} ${keyPositions(it)}" })
            break
        }
    }
}

/** Names of the key positions (objective cities) [civ] holds. */
fun keyPositions(civ: com.unciv.logic.civilization.Civilization) =
    civ.cities.filter { it.cityConstructions.isBuilt(KEY_POSITION) }.map { it.name }.sorted()
