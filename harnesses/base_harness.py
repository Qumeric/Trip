from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import numpy as np
import tcod

from actions import Action
from engine import Engine
from events.base_event import BaseEvent
from events.trigger import StopTrigger

if TYPE_CHECKING:
    from entity import Actor


class BaseHarness(ABC):
    actor: Actor

    def __init__(
        self,
        actor: Actor,
        stop_triggers: list[StopTrigger],
    ):
        self.game_map = Engine.instance().game_map
        self.actor = actor
        self.stop_triggers = stop_triggers

    def get_path_to(self, dest_x: int, dest_y: int) -> list[tuple[int, int]]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        cost = np.array(self.game_map.tiles["walkable"], dtype=np.int8)

        # TODO this implementation might be not fitting for all cases
        for entity in self.game_map.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[entity.x, entity.y] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.actor.x, self.actor.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path: list[list[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        return [(index[0], index[1]) for index in path]

    @abstractmethod
    def get_next_action(self) -> Action:
        """Returns the next proposed action."""

    def stop(self) -> None:
        """Stop the harness."""
        self.actor.harness = None

    def handle_event(self, event: BaseEvent) -> None | str:
        """Handle events for this harness."""
        for trigger in self.stop_triggers:
            if trigger.handle(event):
                self.stop()
                return trigger.report()
        return None

    # def update(self) -> None:
    #     return super().update()
