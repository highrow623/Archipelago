from argparse import Namespace
import random
from typing import Any, Literal, TypeAlias, get_args

from BaseClasses import CollectionState, MultiWorld
from Generate import get_seed_name

from test.general import gen_steps
from worlds import AutoWorld
from worlds.AutoWorld import call_all
from worlds.pseudoregalia import PseudoregaliaWorld as NewPseudoWorld
from worlds.pseudoregalia_old import PseudoregaliaWorld as OldPseudoWorld

new_game = NewPseudoWorld.game
old_game = OldPseudoWorld.game

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

def setup_one_mw(game: str, args_obj: dict[str, Any], seed: int | None) -> MultiWorld:
    mw = MultiWorld(1)
    mw.game[1] = game
    mw.player_name = {
        1: f"{game} Tester"
    }
    mw.set_seed(seed)
    random.seed(mw.seed)
    mw.seed_name = get_seed_name(random)
    args = Namespace()
    for name, option in AutoWorld.AutoWorldRegister.world_types[game].options_dataclass.type_hints.items():
        setattr(args, name, {
            1: option.from_any(args_obj.get(name, option.default)),
        })
    mw.set_options(args)
    mw.state = CollectionState(mw)
    for step in gen_steps:
        call_all(mw, step)
    return mw

def setup(
        *, game_version: GameVersion = "map_patch", logic_level: LogicLevel = "normal", obscure_logic: bool = False,
        spawn_point: SpawnPoint = "castle_main", progressive_breaker: bool = True, progressive_slide: bool = True,
        split_sun_greaves: bool = False, split_cling_gem: bool = False, randomize_time_trials: bool = False,
        randomize_goats: bool = False, randomize_chairs: bool = False, randomize_books: bool = False,
        randomize_notes: bool = False, seed: int | None = None) -> tuple[MultiWorld, MultiWorld]:
    args_obj = {
        "game_version": game_version,
        "logic_level": logic_level,
        "obscure_logic": obscure_logic,
        "spawn_point": spawn_point,
        "progressive_breaker": progressive_breaker,
        "progressive_slide": progressive_slide,
        "split_sun_greaves": split_sun_greaves,
        "split_cling_gem": split_cling_gem,
        "randomize_time_trials": randomize_time_trials,
        "randomize_goats": randomize_goats,
        "randomize_chairs": randomize_chairs,
        "randomize_books": randomize_books,
        "randomize_notes": randomize_notes,
    }
    new_mw = setup_one_mw(new_game, args_obj, seed)
    old_mw = setup_one_mw(old_game, args_obj, new_mw.seed)
    return new_mw, old_mw

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
    for description, (new_mw, old_mw) in mws.items():
        def err(msg):
            print(f"{description}: {msg}")

        new_regions = set(region.name for region in new_mw.worlds[1].get_regions())
        old_regions = set(region.name for region in old_mw.worlds[1].get_regions())
        for region in new_regions:
            if region not in old_regions:
                err(f"region {region} is in the new world but not the old world")
        for region in old_regions:
            if region not in old_regions:
                err(f"region {region} is in the old world but not the new world")

        new_entrances = {entrance.name: entrance for entrance in new_mw.worlds[1].get_entrances()}
        old_entrances = {entrance.name: entrance for entrance in old_mw.worlds[1].get_entrances()}
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

        new_locations = {location.name: location for location in new_mw.worlds[1].get_locations()}
        old_locations = {location.name: location for location in old_mw.worlds[1].get_locations()}
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
        new_mw, old_mw = setup(spawn_point=spawn_point)
        new_origin = new_mw.worlds[1].origin_region_name
        old_origin = old_mw.worlds[1].origin_region_name
        if new_origin != old_origin:
            print(f"{spawn_point}: origin regions don't match; new: {new_origin}, old: {old_origin}")

def compare_logic():
    # TODO
    pass

if __name__ == "__main__":
    compare_create()
    compare_origins()
    compare_logic()
