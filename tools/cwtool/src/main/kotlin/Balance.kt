package cwtool

import com.unciv.Constants
import com.unciv.UncivGame
import com.unciv.logic.civilization.Civilization
import com.unciv.logic.civilization.PlayerType
import com.unciv.logic.civilization.managers.TurnManager
import com.unciv.logic.civilization.managers.UnitManager
import com.unciv.logic.files.FileConversions
import com.unciv.logic.files.UncivFiles
import com.unciv.logic.map.mapunit.MapUnit
import java.io.File
import kotlin.random.Random

/**
 * Balance test: plays one whole battle and prints a one-line RESULT.
 *
 * Unciv's combat luck depends only on the turn and the tile, so the same scenario file always plays out the same way.
 * To sample different battles, [seed] gives the cities and the game fresh random ids and shuffles the order in which
 * each army's units act: neutral changes that alter the AI's choices (and from then on where and when fights happen)
 * without favouring either side.
 *
 * [mode] "AI": both armies are run by Unciv's AI (a Spectator watches).
 *        "Union" / "Confederacy": that side is the human seat, played by Unciv's unit automation, as in [simulateScenario].
 *        Its units choose their promotions like the AI's do, as a player would: by default Unciv's automation never
 *        promotes a human player's units, and over a whole battle that alone makes the automated side lose most games.
 */
fun balanceRun(scenarioFile: File, mode: String, seed: Int, lastTurn: Int = 49) {
    initUnciv()
    UncivGame.Current.settings.automatedUnitsChoosePromotions = true
    val rng = Random(seed)
    // Fresh random ids (cities, game) for every seed, replaced in the saved text so all references stay consistent:
    // Unciv uses them in some combat rolls and AI tie-breaks, so each build of a scenario otherwise plays its own way.
    val uuid = Regex("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
    val fresh = HashMap<String, String>()
    val json = uuid.replace(FileConversions.unzip(scenarioFile.readText().trim())) { m ->
        fresh.getOrPut(m.value) { java.util.UUID(rng.nextLong(), rng.nextLong()).toString() }
    }
    val game = UncivFiles.gameInfoFromString(json)
    UncivGame.Current.gameInfo = game
    val unitListField = UnitManager::class.java.getDeclaredField("unitList").apply { isAccessible = true }
    for (civ in game.civilizations) {
        @Suppress("UNCHECKED_CAST")
        val units = unitListField.get(civ.units) as List<MapUnit>
        unitListField.set(civ.units, units.shuffled(rng))
    }

    val human: Civilization?
    if (mode == "AI") {
        // keep the Spectator as the only human: nextTurn() then plays both armies' turns
        for (civ in game.civilizations) if (!civ.isSpectator()) civ.playerType = PlayerType.AI
        human = null
    } else {
        game.civilizations.removeIf { it.civID == Constants.spectator }
        for (civ in game.civilizations) { civ.playerType = PlayerType.AI; civ.diplomacy.remove(Constants.spectator) }
        human = game.getCivilization(mode).apply { playerType = PlayerType.Human }
        if (game.currentPlayer == Constants.spectator) { game.currentPlayer = ""; game.nextTurn(); game.turns-- }
    }

    val union = game.getCivilization("Union")
    val confed = game.getCivilization("Confederacy")
    val neutral = game.getCivilizationOrNull(NEUTRAL)
    fun neutralKeys() = if (neutral == null || neutral.isDefeated()) 0 else keys(neutral)
    val startUnits = mapOf("Union" to union.units.getCivUnitsSize(), "Confederacy" to confed.units.getCivUnitsSize())
    val arrived = HashMap<String, Int>()
    val keysAt = LinkedHashMap<Int, String>()
    var firstConfed4: Int? = null
    var hqLost: String? = null
    var prevNames = mapOf("Union" to unitIds(union), "Confederacy" to unitIds(confed))
    val lost = HashMap<String, Int>()

    while (game.turns < lastTurn && game.victoryData == null) {
        if (human != null) TurnManager(human).automateTurn()
        game.nextTurn()
        for (civ in listOf(union, confed)) {
            val now = unitIds(civ)
            arrived[civ.civID] = (arrived[civ.civID] ?: 0) + (now - prevNames[civ.civID]!!).size
            lost[civ.civID] = (lost[civ.civID] ?: 0) + (prevNames[civ.civID]!! - now).size
        }
        prevNames = mapOf("Union" to unitIds(union), "Confederacy" to unitIds(confed))
        val uk = keys(union); val ck = keys(confed)
        if (game.turns in setOf(6, 12, 20, 30, 40, 47)) keysAt[game.turns] = "$uk-$ck-${neutralKeys()}"
        if (ck >= 4 && firstConfed4 == null) firstConfed4 = game.turns
        if (hqLost == null) {
            if (!union.cities.any { it.name == "Taneytown Road" }) hqLost = "Union@${game.turns}"
            if (!confed.cities.any { it.name == "Chambersburg Pike" }) hqLost = "Confederacy@${game.turns}"
        }
    }
    val v = game.victoryData
    fun mil(c: Civilization) = c.units.getCivUnits().count { it.isMilitary() }
    println("RESULT mode=$mode seed=$seed winner=${v?.winningCiv ?: "none"} by=${v?.victoryType?.replace(' ', '_') ?: "-"} turn=${v?.victoryTurn ?: game.turns}" +
        " keysU=${keys(union)} keysC=${keys(confed)} keysN=${neutralKeys()} keyTimeline=${keysAt.entries.joinToString(",") { "t${it.key}:${it.value}" }}" +
        " confed4keysAt=${firstConfed4 ?: "-"} hqLost=${hqLost ?: "-"}" +
        " unitsU=${startUnits["Union"]}+${arrived["Union"] ?: 0}-${lost["Union"] ?: 0} milU=${mil(union)}" +
        " unitsC=${startUnits["Confederacy"]}+${arrived["Confederacy"] ?: 0}-${lost["Confederacy"] ?: 0} milC=${mil(confed)}" +
        " heldU=${keyPositions(union).joinToString("|").replace(' ', '_')} heldC=${keyPositions(confed).joinToString("|").replace(' ', '_')}")
}

private fun unitIds(civ: Civilization) = civ.units.getCivUnits().map { it.id }.toSet()
private fun keys(civ: Civilization) = civ.cities.count { it.cityConstructions.isBuilt(KEY_POSITION) }
