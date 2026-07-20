import argparse
from argparse import Namespace
import itertools
import random
import re
from typing import Any, Literal, TypeAlias, get_args

from BaseClasses import CollectionState, ItemClassification, MultiWorld
from Generate import get_seed_name

from test.general import gen_steps
from worlds import AutoWorld
from worlds.AutoWorld import call_all
from worlds.pseudoregalia import PseudoregaliaWorld as NewPseudoWorld
from worlds.pseudoregalia_old import PseudoregaliaWorld as OldPseudoWorld

new_game = NewPseudoWorld.game
old_game = OldPseudoWorld.game

# setup all args for logic checking. the idea is to combine all these variations in all combinations
arg_categories = [
    {
        "mp": {},
        "fg": {"game_version": "full_gold"},
    },
    {
        "normal": {},
        "normal_obscure": {"obscure_logic": True},
        "hard": {"logic_level": "hard"},
        "hard_obscure": {"logic_level": "hard", "obscure_logic": True},
        "expert": {"logic_level": "expert"},
        "lunatic": {"logic_level": "lunatic"},
    },
    {
        "castle": {},
        "gazebo": {"spawn_point": "castle_gazebo"},
        "dungeon": {"spawn_point": "dungeon_mirror"},
        "library": {"spawn_point": "library"},
        "ub_south": {"spawn_point": "underbelly_south"},
        "ub_main": {"spawn_point": "underbelly_big_room"},
        "bailey": {"spawn_point": "bailey_main"},
        "keep": {"spawn_point": "keep_main"},
        "keep_north": {"spawn_point": "keep_north"},
        "theatre": {"spawn_point": "theatre_main"},
    },
    {
        "no_split": {},
        "split": {"split_sun_greaves": True, "split_cling_gem": True},
    },
    {
        "progressive": {},
        "no_progressive": {"progressive_breaker": False, "progressive_slide": False},
    },
    {
        "extra_checks": {},
        "no_extra_checks": {"randomize_time_trials": True, "randomize_goats": True, "randomize_chairs": True,
                            "randomize_books": True, "randomize_notes": True},
    },
]
logic_args = {}
for variation in itertools.product(*(category.keys() for category in arg_categories)):
    desc = "-".join(variation)
    args = {}
    for i, category_desc in enumerate(variation):
        args.update(arg_categories[i][category_desc])
    logic_args[desc] = args

GameVersion: TypeAlias = Literal["map_patch", "full_gold"]
LogicLevel: TypeAlias = Literal["normal", "hard", "expert", "lunatic"]
SpawnPoint: TypeAlias = Literal["castle_main", "castle_gazebo", "dungeon_mirror", "library", "underbelly_south",
                                "underbelly_big_room", "bailey_main", "keep_main", "keep_north", "theatre_main"]

def setup_one_mw(game: str, args_dict: dict[str, Any], seed: int | None) -> MultiWorld:
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
            1: option.from_any(args_dict.get(name, option.default)),
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

def fill(new_mw: MultiWorld, old_mw: MultiWorld):
    # have to put this import here for some reason
    from Fill import distribute_items_restrictive
    distribute_items_restrictive(new_mw)
    call_all(new_mw, "post_fill")
    call_all(new_mw, "finalize_multiworld")
    assert len(new_mw.get_unfilled_locations()) == 0, f"{new_game}: seed {new_mw.seed}: fill did not fill all locations"

    # just copying item placements over serves our purposes in this script but I don't think it's technically "proper"
    for old_location in old_mw.get_unfilled_locations():
        new_location = new_mw.get_location(old_location.name, 1)
        old_location.item = old_mw.worlds[1].create_item(new_location.item.name)

def compare_create():
    # the new apworld will not create entrances if the rule always evaluates to false as an optimization. this happens
    # on lower logic levels, so we set logic_level to lunatic here to create all entrances
    mws = {
        "mp-min_locations": setup(logic_level="lunatic"),
        "fg-min_locations": setup(logic_level="lunatic", game_version="full_gold"),
        "mp-max_locations": setup(logic_level="lunatic", split_sun_greaves=True, split_cling_gem=True,
                                  randomize_time_trials=True, randomize_goats=True, randomize_chairs=True,
                                  randomize_books=True, randomize_notes=True),
        "fg-max_locations": setup(logic_level="lunatic", game_version="full_gold", split_sun_greaves=True,
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

def build_sphere_repr(mw: MultiWorld, initial_str: str) -> list[str]:
    """Generates a line-by-line string representation of the multiworld's spheres."""
    repr: list[str] = [initial_str]
    for i, sphere in enumerate(mw.get_spheres()):
        repr.append(f"  Sphere {i}")
        sorted_sphere = sorted(sphere, key=lambda loc: loc.name)
        for location in sorted_sphere:
            item_repr = location.item.name
            # print progression items in color/bold
            if location.item.classification & ItemClassification.progression != 0:
                item_repr = f"\033[96m\033[1m{item_repr}\033[0m"
            repr.append(f"    {location.name}: {item_repr}")
    return repr

# https://stackoverflow.com/questions/68627535/how-to-get-the-length-of-a-string-without-calculating-the-formatting-of-the-text
def len_no_ansi(string):
    """Gets the length of a string without ANSI escape codes."""
    return len(re.sub(
        r'[\u001B\u009B][\[\]()#;?]*((([a-zA-Z\d]*(;[-a-zA-Z\d\/#&.:=?%@~_]*)*)?\u0007)|((\d{1,4}(?:;\d{0,4})*)?[\dA-PR-TZcf-ntqry=><~]))', '', string))

def print_spheres(new_mw: MultiWorld, old_mw: MultiWorld):
    """Prints both multiworld's spheres side-by-side for easy comparison."""
    new_strs = build_sphere_repr(new_mw, "New MultiWorld Spheres")
    old_strs = build_sphere_repr(old_mw, "Old MultiWorld Spheres")
    old_start = 10 + max(len_no_ansi(s) for s in new_strs)

    # make both lists have the same size so zip doesn't miss any strings
    new_strs_count = len(new_strs)
    old_strs_count = len(old_strs)
    if new_strs_count > old_strs_count:
        old_strs.extend([""] * (new_strs_count - old_strs_count))
    elif old_strs_count > new_strs_count:
        new_strs.extend([""] * (old_strs_count - new_strs_count))

    for new_str, old_str in zip(new_strs, old_strs, strict=True):
        buffer = " " * (old_start-len_no_ansi(new_str))
        print(f"{new_str}{buffer}{old_str}")

def compare_logic():
    for description, args in logic_args.items():
        new_mw, old_mw = setup(**args)
        fill(new_mw, old_mw)
        def err(msg: str):
            print(f"-d {description} -s {new_mw.seed}: {msg}")

        new_spheres = list(new_mw.get_spheres())
        old_spheres = list(old_mw.get_spheres())
        if len(new_spheres) != len(old_spheres):
            err(f"different number of spheres; new {len(new_spheres)}, old {len(old_spheres)}")
            # print_spheres(new_mw, old_mw)
            continue
        for i, (new_sphere, old_sphere) in enumerate(zip(new_spheres, old_spheres, strict=True)):
            new_sphere_names = set(location.name for location in new_sphere)
            old_sphere_names = set(location.name for location in old_sphere)
            if new_sphere_names != old_sphere_names:
                err(f"sphere {i} has a different set of locations")
                # print_spheres(new_mw, old_mw)
                break

def check_seed(seed: int, description: str):
    args = logic_args[description]
    new_mw, old_mw = setup(seed=seed, **args)
    fill(new_mw, old_mw)
    print_spheres(new_mw, old_mw)

def main():
    parser = argparse.ArgumentParser(prog="Pseudoregalia Logic Comparer")
    parser.add_argument("-r", "--reps", default=1, type=int, help="how many logic checker repetitions to do")
    parser.add_argument("-s", "--seed", type=int, help="gen seed, when checking details about an individual seed")
    parser.add_argument("-d", "--desc", help="logic arg description, when checking details about an individual seed")
    args = parser.parse_args()

    if args.seed and args.desc:
        check_seed(args.seed, args.desc)
    else:
        compare_create()
        compare_origins()
        for _ in range(args.reps):
            compare_logic()

if __name__ == "__main__":
    main()
