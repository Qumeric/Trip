from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from numpy.typing import NDArray
from tcod.console import Console
from tcod.map import compute_fov
import numpy as np

from entity import Item
from events.map_events import BaseMapEvent

from . import tile_types

if TYPE_CHECKING:
    from entity import Actor, Entity, Interactable
    from harnesses.base_harness import BaseHarness


@dataclass
class Fov:
    visible: NDArray[np.bool_]
    explored: NDArray[np.bool_]


class GameMap:
    def __init__(self, width: int, height: int):
        self.width, self.height = width, height
        # self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")
        self.actors: set[Actor] = set()
        self.interactables: set[Interactable] = set()
        self.items: set[Item] = set()

        self.fovs: dict[Actor, Fov] = {}
        # TODO probably should be decoulped from map, instead put it in GameWorld which will store maps
        self.harnesses: dict[Actor, BaseHarness] = {}

        self.focused_actor: Actor | None = None

    # @property
    # def actors(self) -> Iterator[Actor]:
    #     """Iterate over this maps living actors."""
    #     yield from (entity for entity in self.entities if isinstance(entity, Actor) and entity.is_alive)

    # @property
    # def items(self) -> Iterator[Item]:
    #     yield from (entity for entity in self.entities if isinstance(entity, Item))

    # @property
    # def buildings(self) -> Iterator[Building]:
    #     yield from (entity for entity in self.entities if isinstance(entity, Building))

    @property
    def entities(self) -> set[Actor | Interactable | Item]:
        return self.actors | self.interactables | self.items

    @property
    def focused_fov(self) -> Fov:
        if self.focused_actor is None:
            raise ValueError("No actor is focused. Perhaps there are no actors on the map?")
        return self.fovs[self.focused_actor]

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_neighbors(self, x: int, y: int):
        neighbors = [(x + dx, y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if dx != 0 or dy != 0]
        return [(nx, ny) for nx, ny in neighbors if self.in_bounds(nx, ny)]
    
    @staticmethod
    def chebyshev_distance(a: tuple[int, int], b: tuple[int, int]):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def handle_event(self, event: BaseMapEvent) -> None:
        for actor in self.actors:
            fov = self.fovs[actor]
            if fov.visible[event.x, event.y]:
                actor.handle_external_event(event)

    def update_fov(self) -> None:
        for actor in self.actors:
            fov = self.fovs[actor]
            fov.visible[:] = compute_fov(
                self.tiles["transparent"],
                (actor.x, actor.y),
                radius=actor.eyesight,
            )

            fov.explored |= fov.visible

    def can_spawn_at(self, x: int, y: int) -> bool:
        """Return True if an entity can spawn at this location."""
        return self.in_bounds(x, y) and not self.get_blocking_entity_at_location(x, y)

    def spawn_actor(self, actor: Actor) -> None:
        self.actors.add(actor)
        self.fovs[actor] = Fov(
            visible=np.full((self.width, self.height), fill_value=False, order="F"),
            explored=np.full((self.width, self.height), fill_value=False, order="F"),
        )
        if self.focused_actor is None:
            self.focused_actor = actor
        # spawn_signal.send(
        #     self,
        #     event=SpawnEvent(entity.x, entity.y, entity),
        # )

    def spawn_interactable(self, interactable: Interactable) -> None:
        self.interactables.add(interactable)

    def spawn_item(self, item: Item) -> None:
        self.items.add(item)

    def get_blocking_entity_at_location(
        self,
        location_x: int,
        location_y: int,
    ) -> Entity | None:
        for entity in self.entities:
            if entity.blocks_movement and entity.x == location_x and entity.y == location_y:
                return entity

        return None
    
    def get_interactable_at_location(
        self,
        location_x: int,
        location_y: int,
    ) -> Interactable | None:
        for interactable in self.interactables:
            if interactable.x == location_x and interactable.y == location_y:
                return interactable

        return None

    def get_item_at_location(
        self,
        location_x: int,
        location_y: int,
    ) -> Item | None:
        for item in self.items:
            if item.x == location_x and item.y == location_y:
                return item

        return None
    # def get_actor_at_location(self, x: int, y: int) -> Actor | None:
    #     for actor in self.actors:
    #         if actor.x == x and actor.y == y:
    #             return actor

    #     return None

    # def get_building_at_location(self, x: int, y: int) -> Building | None:
    #     for building in self.buildings:
    #         if building.x == x and building.y == y:
    #             return building

    #     return None

    # def get_entities_at_location(self, x: int, y: int) -> list[Entity]:
    #     return [entity for entity in self.entities if entity.x == x and entity.y == y]

    # def get_names_at_location(self, x: int, y: int) -> str:
    #     if not self.in_bounds(x, y) or not self.visible[x, y]:
    #         return ""

    #     entities = self.get_entities_at_location(x, y)
    #     names = ", ".join(map(lambda entity: entity.name, entities))

    #     return names.capitalize()

    def render(self, console: Console) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        console.rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.focused_fov.visible, self.focused_fov.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        entities_sorted_for_rendering = sorted(self.entities, key=lambda x: x.render_order.value)

        for entity in entities_sorted_for_rendering:
            if self.focused_fov.visible[entity.x, entity.y]:
                console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)
