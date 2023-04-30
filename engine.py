from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from events.map_events import BaseMapEvent

if TYPE_CHECKING:
    from game_map.game_map import GameMap
    from tcod import Console

from loguru import logger

# TODO overhaul rendering system. There should be some tree of renderable objects.
# def render_bar(console: Console, current_value: int, maximum_value: int, total_width: int) -> None:
#     bar_width = int(float(current_value) / maximum_value * total_width)

#     console.draw_rect(x=0, y=constants.map_height + 2, width=20, height=1, ch=1, bg=color.bar_empty)

#     if bar_width > 0:
#         console.draw_rect(x=0, y=constants.map_height + 2, width=bar_width, height=1, ch=1, bg=color.bar_filled)

#     console.print(x=1, y=constants.map_height + 2, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text)


# def render_names_at_mouse_location(console: Console, x: int, y: int, engine: Engine) -> None:
#     mouse_x, mouse_y = engine.mouse_location

#     names_at_mouse_location = engine.game_map.get_names_at_location(x=mouse_x, y=mouse_y)

#     console.print(x=x, y=y, string=names_at_mouse_location)


class Engine:
    _instance: Engine | None = None

    mouse_location: tuple[int, int]
    game_map: GameMap
    ticks: int
    map_events: list[BaseMapEvent]

    def __new__(cls, game_map: GameMap):
        if cls._instance is None:
            logger.remove()
            logger.add("log.txt", level="INFO", rotation="1 week")
            print("Creating the Engine")
            cls._instance = super().__new__(cls)
            cls._instance.mouse_location = (0, 0)
            cls._instance.game_map = game_map
            cls._instance.ticks = 0
            cls._instance.map_events = []
        return cls._instance

    @property
    def time(self) -> datetime:
        return datetime(1, 1, 1) + timedelta(seconds=self.ticks * 15)

    @classmethod
    def instance(cls, game_map: GameMap | None = None):
        if cls._instance is None:
            if game_map is None:
                raise ValueError("Engine must be initialized with a GameMap first.")
            cls._instance = cls(game_map)
        return cls._instance

    def render(self, console: Console) -> None:
        self.game_map.render(console)

    def tick(self) -> None:
        for interactable in self.game_map.interactables:
            interactable.update()
        
        for actor in self.game_map.actors:
            actor.update()

        for event in self.map_events:
            self.game_map.handle_event(event)

        self.map_events = []

        self.ticks += 1
        self.game_map.update_fov()

        for actor in self.game_map.actors:
            actor.ai.update()
            if actor.ai.harness is not None:
                actor.ai.harness.get_next_action().perform()
