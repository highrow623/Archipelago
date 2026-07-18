from typing import Literal, TypeAlias, get_args

from BaseClasses import CollectionState, MultiWorld
import Options

from worlds.pseudoregalia import PseudoregaliaWorld as NewPseudoWorld
import worlds.pseudoregalia.options as new_options
from worlds.pseudoregalia_old import PseudoregaliaWorld as OldPseudoWorld
import worlds.pseudoregalia_old.options as old_options

"""
options:
    logic:
        game_version
        spawn_point (dungeon changes logic for dungeon slide -> dungeon escape lower)
    can_create:
        game_version
        split_sun_greaves
        split_cling_gem
        randomize_time_trials
        randomize_goats
        randomize_chairs
        randomize_books
        randomize_notes
"""

GameVersion: TypeAlias = Literal["map_patch", "full_gold"]
LogicLevel: TypeAlias = Literal["normal", "hard", "expert", "lunatic"]
SpawnPoint: TypeAlias = Literal["castle_main", "castle_gazebo", "dungeon_mirror", "library", "underbelly_south",
                                "underbelly_big_room", "bailey_main", "keep_main", "keep_north", "theatre_main"]

def setup(
        *, game_version: GameVersion = "map_patch", logic_level: LogicLevel = "normal", obscure_logic: bool = False,
        spawn_point: SpawnPoint = "castle_main", progressive_breaker: bool = True, progressive_slide: bool = True,
        split_sun_greaves: bool = False, split_cling_gem: bool = False, randomize_time_trials: bool = False,
        randomize_goats: bool = False, randomize_chairs: bool = False, randomize_books: bool = False,
        randomize_notes: bool = False) -> MultiWorld:
    mw = MultiWorld(2)
    mw.worlds[1] = NewPseudoWorld(mw, 1)
    mw.worlds[2] = OldPseudoWorld(mw, 2)
    mw.state = CollectionState(mw)

    mw.worlds[1].options = new_options.PseudoregaliaOptions(
        progression_balancing=Options.ProgressionBalancing(Options.ProgressionBalancing.default),
        accessibility=Options.Accessibility(Options.Accessibility.default),
        local_items=Options.LocalItems([]),
        non_local_items=Options.NonLocalItems([]),
        start_inventory=Options.StartInventory({}),
        start_hints=Options.StartHints([]),
        start_location_hints=Options.StartLocationHints([]),
        exclude_locations=Options.ExcludeLocations([]),
        priority_locations=Options.PriorityLocations([]),
        item_links=Options.ItemLinks([]),
        plando_items=Options.PlandoItems([]),
        game_version=new_options.GameVersion(getattr(new_options.GameVersion, f"option_{game_version}")),
        logic_level=new_options.LogicLevel(getattr(new_options.LogicLevel, f"option_{logic_level}")),
        obscure_logic=new_options.ObscureLogic(1 if obscure_logic else 0),
        spawn_point=new_options.SpawnPoint(getattr(new_options.SpawnPoint, f"option_{spawn_point}")),
        progressive_breaker=new_options.ProgressiveBreaker(1 if progressive_breaker else 0),
        progressive_slide=new_options.ProgressiveSlide(1 if progressive_slide else 0),
        split_sun_greaves=new_options.SplitSunGreaves(1 if split_sun_greaves else 0),
        split_cling_gem=new_options.SplitClingGem(1 if split_cling_gem else 0),
        start_with_breaker=new_options.StartWithBreaker(0),
        start_with_map=new_options.StartWithMap(0),
        randomize_time_trials=new_options.RandomizeTimeTrials(1 if randomize_time_trials else 0),
        randomize_goats=new_options.RandomizeTimeTrials(1 if randomize_goats else 0),
        randomize_chairs=new_options.RandomizeTimeTrials(1 if randomize_chairs else 0),
        randomize_books=new_options.RandomizeTimeTrials(1 if randomize_books else 0),
        randomize_notes=new_options.RandomizeTimeTrials(1 if randomize_notes else 0),
        major_key_hints=new_options.MajorKeyHints(1),
    )
    mw.worlds[2].options = old_options.PseudoregaliaOptions(
        progression_balancing=Options.ProgressionBalancing(Options.ProgressionBalancing.default),
        accessibility=Options.Accessibility(Options.Accessibility.default),
        local_items=Options.LocalItems([]),
        non_local_items=Options.NonLocalItems([]),
        start_inventory=Options.StartInventory({}),
        start_hints=Options.StartHints([]),
        start_location_hints=Options.StartLocationHints([]),
        exclude_locations=Options.ExcludeLocations([]),
        priority_locations=Options.PriorityLocations([]),
        item_links=Options.ItemLinks([]),
        plando_items=Options.PlandoItems([]),
        game_version=old_options.GameVersion(getattr(old_options.GameVersion, f"option_{game_version}")),
        logic_level=old_options.LogicLevel(getattr(old_options.LogicLevel, f"option_{logic_level}")),
        obscure_logic=old_options.ObscureLogic(1 if obscure_logic else 0),
        spawn_point=old_options.SpawnPoint(getattr(old_options.SpawnPoint, f"option_{spawn_point}")),
        progressive_breaker=old_options.ProgressiveBreaker(1 if progressive_breaker else 0),
        progressive_slide=old_options.ProgressiveSlide(1 if progressive_slide else 0),
        split_sun_greaves=old_options.SplitSunGreaves(1 if split_sun_greaves else 0),
        split_cling_gem=old_options.SplitClingGem(1 if split_cling_gem else 0),
        start_with_breaker=old_options.StartWithBreaker(0),
        start_with_map=old_options.StartWithMap(0),
        randomize_time_trials=old_options.RandomizeTimeTrials(1 if randomize_time_trials else 0),
        randomize_goats=old_options.RandomizeTimeTrials(1 if randomize_goats else 0),
        randomize_chairs=old_options.RandomizeTimeTrials(1 if randomize_chairs else 0),
        randomize_books=old_options.RandomizeTimeTrials(1 if randomize_books else 0),
        randomize_notes=old_options.RandomizeTimeTrials(1 if randomize_notes else 0),
        major_key_hints=old_options.MajorKeyHints(1),        
    )

    mw.worlds[1].generate_early()
    mw.worlds[2].generate_early()

    mw.worlds[1].create_regions()
    mw.worlds[2].create_regions()

    mw.worlds[1].create_items()
    mw.worlds[2].create_items()

    mw.worlds[1].set_rules()
    mw.worlds[2].set_rules()

    return mw

def compare_create():
    # the new apworld will not create entrances if the rule always evaluates to false as an optimization. this happens
    # on lower logic levels, so we set logic_level to lunatic here to create all entrances
    mws = {
        "map_patch_false": setup(logic_level="lunatic"),
        "full_gold_false": setup(logic_level="lunatic", game_version="full_gold"),
        "map_patch_true": setup(logic_level="lunatic", split_sun_greaves=True, split_cling_gem=True,
                                randomize_time_trials=True, randomize_goats=True, randomize_chairs=True,
                                randomize_books=True, randomize_notes=True),
        "full_gold_true": setup(logic_level="lunatic", game_version="full_gold", split_sun_greaves=True,
                                split_cling_gem=True, randomize_time_trials=True, randomize_goats=True,
                                randomize_chairs=True, randomize_books=True, randomize_notes=True),
    }
    for description, mw in mws.items():
        def err(msg):
            print(f"{description}: {msg}")

        new_regions = set(region.name for region in mw.worlds[1].get_regions())
        old_regions = set(region.name for region in mw.worlds[2].get_regions())
        for region in new_regions:
            if region not in old_regions:
                err(f"region {region} is in the new world but not the old world")
        for region in old_regions:
            if region not in old_regions:
                err(f"region {region} is in the old world but not the new world")

        new_entrances = {entrance.name: entrance for entrance in mw.worlds[1].get_entrances()}
        old_entrances = {entrance.name: entrance for entrance in mw.worlds[2].get_entrances()}
        for entrance_name, new_entrance in new_entrances.items():
            if entrance_name not in old_entrances:
                err(f"entrance {entrance_name} is in the new world but not the old world")
                continue
            if new_entrance.parent_region is None or new_entrance.connected_region is None:
                err(f"entrance {entrance_name} is pooly formed in the new world")
                continue
            old_entrance = old_entrances[entrance_name]
            if old_entrance.parent_region is None or old_entrance.connected_region is None:
                err(f"entrance {entrance_name} is poorly formed in the old world")
                continue
            if new_entrance.parent_region.name != old_entrance.parent_region.name:
                err(f"entrance {entrance_name} has mismatching parent regions")
            if new_entrance.connected_region.name != old_entrance.connected_region.name:
                err(f"entrance {entrance_name} has mismatching connected regions")
        for entrance_name in old_entrances:
            if entrance_name not in new_entrances:
                err(f"entrance {entrance_name} is in the old world but not the new world")

        new_locations = {location.name: location for location in mw.worlds[1].get_locations()}
        old_locations = {location.name: location for location in mw.worlds[2].get_locations()}
        for location_name, new_location in new_locations.items():
            if location_name not in old_locations:
                err(f"location {location_name} is in the new world but not the old world")
                continue
            old_location = old_locations[location_name]
            if new_location.parent_region is not None and old_location.parent_region is None:
                err(f"location {location_name} parent region is defined for new location but not old")
            elif new_location.parent_region is None and old_location.parent_region is not None:
                err(f"location {location_name} parent region is defined for old location but not old")
            elif new_location.parent_region is not None and old_location.parent_region is not None \
                    and new_location.parent_region.name != old_location.parent_region.name:
                err(f"location {location_name}: parent regions don't match; "
                    f"new: {new_location.parent_region.name}, old: {old_location.parent_region.name}")
            if new_location.address is not None and old_location.address is None:
                err(f"location {location_name} address is defined for new location but not old")
            elif new_location.address is None and old_location.address is not None:
                err(f"location {location_name} address is defined for old location but not old")
            elif new_location.address is not None and old_location.address is not None \
                    and new_location.address != old_location.address:
                err(f"location {location_name}: addresses don't match; "
                    f"new: {new_location.address}, old: {old_location.address}")
            if new_location.item is not None and old_location.item is None:
                err(f"location {location_name} item is defined for new location but not old")
            elif new_location.item is None and old_location.item is not None:
                err(f"location {location_name} item is defined for old location but not old")
            elif new_location.item is not None and old_location.item is not None \
                    and new_location.item.name != old_location.item.name:
                err(f"location {location_name}: items don't match; "
                    f"new: {new_location.item.name}, old: {old_location.item.name}")
        for location_name in old_locations:
            if location_name not in new_locations:
                err(f"location {location_name} is in the old world but not the new world")

def compare_origins():
    for spawn_point in get_args(SpawnPoint):
        mw = setup(spawn_point=spawn_point)
        new_origin = mw.worlds[1].origin_region_name
        old_origin = mw.worlds[2].origin_region_name
        if new_origin != old_origin:
            print(f"{spawn_point}: origin regions don't match; new: {new_origin}, old: {old_origin}")

def compare_logic():
    # TODO
    pass

if __name__ == "__main__":
    compare_create()
    compare_origins()
    compare_logic()
