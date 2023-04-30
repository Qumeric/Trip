from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from loguru import logger
import numpy as np

from actions import MovementAction
from entity import Actor
from events.trigger import HealthLossTrigger, TickTrigger
from harnesses.base_harness import BaseHarness

if TYPE_CHECKING:
    from actions import Action


class ExploreHarness(BaseHarness):
    def __init__(self, actor: Actor):
        super().__init__(actor, stop_triggers=[HealthLossTrigger(10), TickTrigger(5)])

    def create_dijkstra_map(self):
        """
        Idea from http://www.roguebasin.com/index.php/The_Incredible_Power_of_Dijkstra_Maps
        Implementation is mine (more efficient)
        """
        game_map = self.game_map
        dijkstra_map = np.full((game_map.width, game_map.height), np.inf)

        queue: deque[tuple[int, int, int]] = deque()

        fov = game_map.focused_fov
        logger.info("Explored tiles:", sum(fov.explored.flatten()))
        logger.info("Visible tiles:", sum(fov.visible.flatten()))
        for x in range(game_map.width):
            for y in range(game_map.height):
                # Cheating because agents have no way to know what tiles are walkable but it's fine for now
                # TODO: shall draw boundary around explored area for efficiency
                if not fov.explored[x, y] and game_map.tiles["walkable"][x, y]:
                    dijkstra_map[x, y] = 0
                    queue.append((x, y, 0))

        while queue:
            x, y, distance = queue.popleft()
            neighbors = game_map.get_neighbors(x, y)
            for nx, ny in neighbors:
                if (
                    dijkstra_map[nx, ny] == np.inf
                    and game_map.tiles["walkable"][nx, ny]
                    and game_map.get_blocking_entity_at_location(nx, ny) is None
                ):
                    dijkstra_map[nx, ny] = distance + 1
                    queue.append((nx, ny, distance + 1))

        def _print():
            for y in range(game_map.height):
                printed_row = False
                for x in range(game_map.width):
                    if fov.visible[x, y]:
                        print(dijkstra_map[x, y], end=" ")
                        printed_row = True
                if printed_row:
                    print()

        return dijkstra_map

    def autoexplore(self) -> tuple[int, int]:
        dijkstra_map = self.create_dijkstra_map()
        min_val = np.inf
        dest_x, dest_y = 0, 0
        ds = [(dx, dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if dx != 0 or dy != 0]
        for dx, dy in ds:
            nx, ny = self.actor.x + dx, self.actor.y + dy
            if dijkstra_map[nx, ny] < min_val:
                min_val = dijkstra_map[nx, ny]
                dest_x, dest_y = dx, dy
        logger.info(f"Autoexplore: {dest_x}, {dest_y}. Minval {min_val}")
        return dest_x, dest_y
    
    def get_next_action(self) -> Action:
        return MovementAction(self.actor, *self.autoexplore())

    def __str__(self) -> str:
        return "Explore"
