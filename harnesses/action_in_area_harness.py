
from __future__ import annotations
from abc import ABC, abstractmethod
from actions import Action
from engine import Engine
from game_map.game_map import GameMap
from harnesses.base_harness import BaseHarness

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from events.trigger import StopTrigger
    from entity import Actor, Interactable


class ActionInAreaHarness(BaseHarness, ABC):
    interactables: list[Interactable]

    def __init__(self, actor: Actor, radius: int, stop_triggers: list[StopTrigger] = []):
        super().__init__(actor, stop_triggers=stop_triggers)
        self.radius = radius
        game_map = Engine.instance().game_map

        self.interactables = []

        # TODO optimize
        for x in range(game_map.width):
            for y in range(game_map.height):
                d = GameMap.chebyshev_distance((x, y), (self.actor.x, self.actor.y))
                if d > self.radius:
                    continue
                interactable = game_map.get_interactable_at_location(x, y)
                if interactable and game_map.fovs[self.actor].explored[x, y]:
                    self.interactables.append(interactable)

        self.interactables.sort(key=lambda i: GameMap.chebyshev_distance((i.x, i.y), (self.actor.x, self.actor.y)))
        if len(self.interactables) == 0:
            self.stop()

    @abstractmethod
    def get_next_action(self) -> Action:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass