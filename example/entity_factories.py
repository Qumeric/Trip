from components.ai import HarnessFactory, ManualInputAI, SingleHarnessAI
from components.consumable import HealingConsumable
from components.inventory import Inventory
from components.needs import Needs
from components.observation_log import ObservationLog
from entity import Actor, Item
from example.gather_food_harness import GatherFoodHarness
from game_map.game_map import GameMap
from harnesses.do_nothing_harness import DoNothingHarness
from harnesses.explore_harness import ExploreHarness


def do_nothing_ai(actor: Actor):
    return SingleHarnessAI(DoNothingHarness(actor))


def explore_ai(actor: Actor):
    return SingleHarnessAI(ExploreHarness(actor))


def manual_input_ai(actor: Actor):
    return ManualInputAI(
        [
            HarnessFactory(harness_name="Do nothing", harness_f=lambda: DoNothingHarness(actor)),
            HarnessFactory(harness_name="Explore", harness_f=lambda: ExploreHarness(actor)),
            HarnessFactory(harness_name="Gather food", harness_f=lambda: GatherFoodHarness(actor, radius=15)),
        ]
    )


def spawn_human(game_map: GameMap, x: int, y: int) -> Actor:
    human = Actor(
        inventory=Inventory(10),
        needs=Needs(max_hp=1000, max_hunger=1000, max_thirst=1000, max_sleepiness=1000, max_lonliness=1000),
        observation_log=ObservationLog(512),
        ai_fun=manual_input_ai,
        name="human",
        char="@",
        x=x,
        y=y,
        color=(0, 0, 0),
    )
    game_map.spawn_actor(human)
    return human


def spawn_orc(game_map: GameMap, x: int, y: int) -> Actor:
    orc = Actor(
        inventory=Inventory(),
        needs=Needs(max_hp=1000, max_hunger=1000, max_thirst=1000, max_sleepiness=1000, max_lonliness=1000),
        observation_log=ObservationLog(256),
        ai_fun=do_nothing_ai,
        name="orc",
        x=x,
        y=y,
        char="o",
        color=(63, 127, 63),
    )
    game_map.spawn_actor(orc)
    return orc


def spawn_health_potion(game_map: GameMap, x: int, y: int):
    health_potion = Item(
        name="health potion",
        x=x,
        y=y,
        char="!",
        color=(255, 0, 0),
        consumable=HealingConsumable(name="Health Potion", amount=4),
    )
    game_map.spawn_item(health_potion)
    return health_potion
