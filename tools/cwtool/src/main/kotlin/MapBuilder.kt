package cwtool

import com.badlogic.gdx.files.FileHandle
import com.badlogic.gdx.utils.JsonReader
import com.badlogic.gdx.utils.JsonValue
import com.unciv.logic.files.FileConversions
import com.unciv.logic.map.MapParameters
import com.unciv.logic.map.MapShape
import com.unciv.logic.map.MapSize
import com.unciv.logic.map.MapType
import com.unciv.logic.map.TileMap
import com.unciv.logic.map.tile.RoadStatus
import com.unciv.models.ruleset.Ruleset
import com.unciv.models.ruleset.RulesetCache
import java.io.File

const val MAP_DESCRIPTION = "The Battle of Gettysburg, July 1-3, 1863. About 250 yards per hex. " +
    "Key terrain: Cemetery Hill, East Cemetery Hill, Culp's Hill, Little Round Top and the Angle. " +
    "Union entry roads: Taneytown Road (HQ), Emmitsburg Road, Baltimore Pike, Hanover Road. " +
    "Confederate entry roads: Chambersburg Pike (HQ), Middletown Road, Harrisburg Road."

fun JsonValue.ints(name: String) = get(name).asIntArray()

/** Builds the Unciv TileMap from the rasterized geography exported by tools/gettysburg_geo.py */
fun buildTileMap(tilesJson: File, ruleset: Ruleset): Pair<TileMap, JsonValue> {
    val data = JsonReader().parse(tilesJson.readText())
    val width = data.getInt("width")
    val height = data.getInt("height")
    val map = TileMap(width, height, ruleset, false)
    map.mapParameters = MapParameters().apply {
        name = "Gettysburg"
        type = MapType.empty
        shape = MapShape.rectangular
        mapSize = MapSize(width, height)
        worldWrap = false
        noRuins = true
        noNaturalWonders = true
        baseRuleset = MOD
        createdWithVersion = com.unciv.UncivGame.VERSION.text
    }
    map.description = MAP_DESCRIPTION

    for (t in data.get("tiles")) {
        val tile = map[t.getInt("x"), t.getInt("y")]
        tile.baseTerrain = t.getString("base")
        tile.naturalWonder = if (t.get("wonder").isNull) null else t.getString("wonder")
        tile.setTerrainFeatures(ArrayList(t.get("features").asStringArray().toList()))
        if (t.getBoolean("road")) tile.roadStatus = RoadStatus.Road
    }
    for (r in data.get("rivers")) {
        val (x1, y1, x2, y2) = r.asIntArray()
        val a = map[x1, y1]; val b = map[x2, y2]
        when (map.getNeighborTileClockPosition(a, b)) {
            4 -> a.hasBottomRightRiver = true
            6 -> a.hasBottomRiver = true
            8 -> a.hasBottomLeftRiver = true
            10 -> b.hasBottomRightRiver = true
            12 -> b.hasBottomRiver = true
            2 -> b.hasBottomLeftRiver = true
            else -> error("not neighbors: $x1,$y1 $x2,$y2")
        }
    }
    // re-run transients so every tile is normalized against the ruleset (natural wonders, feature validity)
    map.setTransients(ruleset)
    for (s in data.get("startingLocations"))
        map.addStartingLocation(s.getString("nation"), map[s.getInt("x"), s.getInt("y")])
    return map to data
}

fun buildMap(tilesJson: File, outFile: File) {
    initUnciv()
    val ruleset = RulesetCache[MOD]!!
    val (map, _) = buildTileMap(tilesJson, ruleset)
    map.assignContinents(TileMap.AssignContinentsMode.Reassign)
    outFile.parentFile.mkdirs()
    FileConversions.writeJson(FileHandle(outFile), map, true)
    // round-trip check
    val loaded = FileConversions.readJson(FileHandle(outFile), TileMap::class.java)!!
    loaded.setTransients(ruleset)
    val wonders = loaded.values.mapNotNull { it.naturalWonder }
    val roads = loaded.values.count { it.roadStatus == RoadStatus.Road }
    val rivers = loaded.values.count { it.hasBottomRiver || it.hasBottomLeftRiver || it.hasBottomRightRiver }
    val features = loaded.values.groupingBy { it.terrainFeatures.joinToString("+") }.eachCount()
    println("Map written: ${outFile.path} (${outFile.length()} bytes), tiles=${loaded.values.size}, roads=$roads, river tiles=$rivers")
    println("Landmarks (${wonders.size}): $wonders")
    println("Feature combos: $features")
}
