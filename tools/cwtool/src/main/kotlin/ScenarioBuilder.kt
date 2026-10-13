package cwtool

import com.badlogic.gdx.files.FileHandle
import com.unciv.Constants
import com.unciv.UncivGame
import com.unciv.logic.GameInfo
import com.unciv.logic.GameStarter
import com.unciv.logic.city.managers.CityFounder
import com.unciv.logic.civilization.PlayerType
import com.unciv.logic.files.UncivFiles
import com.unciv.logic.map.HexCoord
import com.unciv.models.metadata.GameParameters
import com.unciv.models.metadata.GameSetupInfo
import com.unciv.models.metadata.Player
import com.unciv.models.ruleset.RulesetCache
import java.io.File

val VICTORIES = arrayListOf("Hold the Field", "Decisive Victory")
const val KEY_POSITION = "Key Position"  // the building that marks an objective city (gettysburg_oob.OBJECTIVE_BUILDING)

/** One scenario file per difficulty. While a scenario is selected, Unciv's New Game screen locks the game options and
 *  uses the difficulty saved in the scenario, so the difficulty (the AI armies' strength) is chosen from the scenario list. */
val SCENARIOS = linkedMapOf(
    "Gettysburg - July 1, 1863" to "Veterans",
    "Gettysburg - July 1, 1863 (Easiest - Militia)" to "Militia",
    "Gettysburg - July 1, 1863 (Easier - Volunteers)" to "Volunteers",
    "Gettysburg - July 1, 1863 (Harder - Regulars)" to "Regulars",
    "Gettysburg - July 1, 1863 (Hardest - Iron Brigade)" to "Iron Brigade",
)

fun buildScenario(tilesJson: File, mapFile: File, outFile: File, difficulty: String = "Veterans") {
    initUnciv()
    val ruleset = RulesetCache[MOD]!!
    val data = com.badlogic.gdx.utils.JsonReader().parse(tilesJson.readText())

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
    }
    val setup = GameSetupInfo(params)
    setup.mapParameters.name = "Gettysburg"
    setup.mapFile = FileHandle(mapFile)
    val game: GameInfo = GameStarter.startNewGame(setup)
    UncivGame.Current.gameInfo = game

    val union = game.getCivilization("Union")
    val confed = game.getCivilization("Confederacy")
    val sides = listOf(confed, union)

    // 1. remove the default starting armies GameStarter placed on the starting locations
    for (civ in sides) for (u in civ.units.getCivUnits().toList()) u.destroy()

    // 2. found the entry cities (capital = army headquarters first), each with its timetable building,
    //    then the key positions on their landmarks
    for (c in data.get("cities")) {
        val civ = game.getCivilization(c.getString("civ"))
        val city = CityFounder().foundCity(civ, HexCoord.of(c.getInt("x"), c.getInt("y")))
        city.name = c.getString("name")
        if (c.getBoolean("objective")) city.cityConstructions.addBuilding(KEY_POSITION)
        val arrivals = (if (civ.civID == "Union") "Union" else "Confederate") + " Arrivals: " + city.name
        if (ruleset.buildings.containsKey(arrivals)) city.cityConstructions.addBuilding(arrivals)
        if (!city.cityConstructions.isBuilt("Supply Depot")) city.cityConstructions.addBuilding("Supply Depot")
        println("City ${city.name} (${civ.civID}) capital=${city.isCapital()} buildings=${city.cityConstructions.getBuiltBuildings().map { it.name }.toList()}")
    }

    // 3. at war from the first shot, and a war that cannot end in peace (minimumWarDuration in ModOptions).
    //    Declared before the armies are placed: Unciv only lets units into enemy territory once at war.
    union.diplomacyFunctions.makeCivilizationsMeet(confed)
    union.getDiplomacyManager(confed)!!.declareWar()

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
    game.currentPlayer = Constants.spectator
    for (civ in sides) {
        civ.popupAlerts.clear()
        civ.notifications.clear()
        civ.cache.updateSightAndResources()
    }
    outFile.parentFile.mkdirs()
    outFile.writeText(UncivFiles.gameInfoToString(game, forceZip = true))
    println("Scenario written: ${outFile.path} (${outFile.length()} bytes, $difficulty). Civs: ${game.civilizations.map { it.civID }}, current=${game.currentPlayer}, turn=${game.turns}")
}

/** Loads the scenario exactly like NewGameScreen does, then plays [turns] turns. The human side's moves are made by the AI too. */
fun simulateScenario(scenarioFile: File, turns: Int, humanSide: String = "Union") {
    initUnciv()
    val game = UncivFiles.gameInfoFromString(scenarioFile.readText())
    UncivGame.Current.gameInfo = game
    // --- same steps as NewGameScreen.startNewGame for scenarios
    game.civilizations.removeIf { it.civID == Constants.spectator }
    for (civ in game.civilizations) { civ.playerType = PlayerType.AI; civ.diplomacy.remove(Constants.spectator) }
    game.getCivilization(humanSide).playerType = PlayerType.Human
    if (game.currentPlayer == Constants.spectator) { game.currentPlayer = ""; game.nextTurn(); game.turns-- }
    println("Start: current=${game.currentPlayer} turn=${game.turns} human=$humanSide")
    val union = game.getCivilization("Union")
    val confed = game.getCivilization("Confederacy")
    println("  at war: ${union.isAtWarWith(confed)}, barbarians in game: ${game.civilizations.any { it.isBarbarian }}, razing allowed: ${!game.gameParameters.noCityRazing}")
    for (civ in listOf(union, confed)) {
        val explored = game.tileMap.values.count { it.isExplored(civ) }
        val enemy = if (civ == union) confed else union
        val enemyUnitsSeen = enemy.units.getCivUnits().count { civ.viewableTiles.contains(it.currentTile) }
        println("  ${civ.civID}: ${civ.units.getCivUnits().count()} units, explored ${explored}/${game.tileMap.values.size} tiles, sees ${enemyUnitsSeen}/${enemy.units.getCivUnits().count()} enemy units, key positions ${keyPositions(civ)}")
    }
    val human = game.getCivilization(humanSide)
    var lastNames = game.civilizations.associate { it.civID to it.units.getCivUnits().map { u -> u.instanceName ?: u.name }.toList() }
    val totalLost = HashMap<String, Int>()
    val keysHeld = game.civilizations.associate { it.civID to keyPositions(it) }.toMutableMap()
    for (t in 1..turns) {
        com.unciv.logic.civilization.managers.TurnManager(human).automateTurn()
        game.nextTurn()
        val line = StringBuilder("Turn ${game.turns}:")
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
