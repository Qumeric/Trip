from random import randint
from components.consumable import Food
from engine import Engine
from entity import Actor, Interactable, Item
from game_map.game_map import GameMap


def spawn_apple(game_map: GameMap, x: int, y: int):
    apple = Item(
        x=x,
        y=y,
        char="a",
        color=(255, 0, 0),
        name="Apple",
        consumable=Food(name="Apple", nutrition=10, water_content=8),
    )
    game_map.spawn_item(apple)
    return apple


class Tree(Interactable):
    max_apples: int
    apples: int

    def __init__(self, x: int, y: int, max_apples: int = 10):
        super().__init__("Tree", "T", x, y, (255, 255, 255))
        self.max_apples = max_apples
        self.apples = 0

    def update(self):
        if self.apples < self.max_apples:
            self.apples += 1

    def interact(self, actor: Actor):
        game_map = Engine.instance().game_map

        if self.apples == 0:
            return

        apples_to_drop = randint(1, self.apples)
        attempts = apples_to_drop * 2

        while apples_to_drop > 0 and attempts > 0:
            dx = randint(1, 3)
            dy = randint(1, 3)
            sx = randint(0, 1) * 2 - 1
            sy = randint(0, 1) * 2 - 1
            x = self.x + dx * sx
            y = self.y + dy * sy

            if game_map.can_spawn_at(x, y):
                spawn_apple(
                    game_map,
                    x,
                    y,
                )
                apples_to_drop -= 1
            attempts -= 1

        return super().interact(actor)
