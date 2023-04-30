import random

from example.entity_factories import spawn_health_potion, spawn_human, spawn_orc
from example.tree import Tree
from game_map import tile_types
from game_map.game_map import GameMap


def spawn_tree(game_map: GameMap, x: int, y: int):
    tree = Tree(
        x=x,
        y=y,
    )
    game_map.spawn_interactable(tree)


# TODO belongs not to Trip but games based on it
def populate_island(
    island: GameMap,
    maximum_monsters: int = 10,
    maximum_items: int = 5,
):
    spawn_human(island, island.width // 2, island.height // 2)

    number_of_monsters = random.randint(1, maximum_monsters)
    number_of_items = random.randint(1, maximum_items)

    while number_of_monsters > 0:
        x = random.randint(0, island.width - 1)
        y = random.randint(0, island.height - 1)

        if not any(entity.x == x and entity.y == y for entity in island.entities) and island.tiles[x, y][0]:
            spawn_orc(island, x, y)
            number_of_monsters -= 1

    while number_of_items > 0:
        x = random.randint(0, island.width - 1)
        y = random.randint(0, island.height - 1)

        if not any(entity.x == x and entity.y == y for entity in island.entities) and island.tiles[x, y][0]:
            if random.random() < 0.7:
                spawn_health_potion(island, x, y)
            number_of_items -= 1

    # TODO it's just tile_type
    for x in range(island.width):
        for y in range(island.height):
            if island.tiles[x, y] == tile_types.forrest:
                if random.random() < 0.05:
                    spawn_tree(island, x, y)

    return island
