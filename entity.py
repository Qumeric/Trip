from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from components.base_component import BaseComponent
from components.consumable import Consumable
from components.inventory import Inventory
from components.needs import Needs
from components.observation_log import ObservationLog
from events.internal_events import BaseInternalEvent, ConsumeEvent, HealthLossEvent, TickEvent
from events.map_events import AttackEvent, BaseMapEvent, DropEvent, PickupEvent, SpawnEvent, UseEvent
from game_map.render_order import RenderOrder

if TYPE_CHECKING:
    from components.ai import BaseAI


class Entity(ABC):
    _next_id = 1

    def __init__(
        self,
        name: str,
        char: str,
        x: int,
        y: int,
        color: tuple[int, int, int],
        render_order: RenderOrder,
        blocks_movement: bool,
    ):
        self.name = name
        self.char = char
        self.x = x
        self.y = y
        self.color = color
        self.render_order = render_order
        self.blocks_movement = blocks_movement
        self.id = Entity._next_id
        Entity._next_id += 1

    def __hash__(self):
        return hash(self.id)

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    @abstractmethod
    def update(self):
        pass


class Actor(Entity):
    def __init__(
        self,
        name: str,
        char: str,
        x: int,
        y: int,
        color: tuple[int, int, int],
        ai_fun: Callable[[Actor], BaseAI],
        needs: Needs,
        inventory: Inventory,
        observation_log: ObservationLog,
        eyesight: int = 8,
    ):
        super().__init__(name, char, x, y, color, RenderOrder.ACTOR, True)
        self.ai = ai_fun(self)
        self.needs = needs
        self.inventory = inventory
        self.observation_log = observation_log
        self.eyesight = eyesight

    def handle_internal_event(self, event: BaseInternalEvent):
        match event:
            case HealthLossEvent(amount):
                observation = f"You have lost {amount} hp"
            case ConsumeEvent(consumable):
                observation = f"You consumed {consumable.name}"
            case TickEvent():
                self.ai.handle_event(event)
                return
            case _:
                raise NotImplementedError(f"Unhandled event {event}")

        self.observation_log.add(observation, event)
        self.ai.handle_event(event)

    def handle_external_event(self, event: BaseMapEvent) -> None:
        match event:
            case SpawnEvent(x, y, entity):
                observation = f"{entity.name} appeared at [{x}, {y}]"
            case AttackEvent(x, y, actor, target):
                observation = f"{actor.name} attacked {target.name} at [{x}, {y}]"
            case PickupEvent(x, y, actor, item):
                observation = f"{actor.name} picked up {item.name} at [{x}, {y}]"
            case DropEvent(x, y, actor, item):
                observation = f"{actor.name} dropped {item.name} at [{x}, {y}]"
            case UseEvent(x, y, actor, item):
                observation = f"{actor.name} used {item.name} at [{x}, {y}]"
            case _:
                raise NotImplementedError(f"Unhandled event {event}")

        self.observation_log.add(observation, event)

    def update(self):
        self.handle_internal_event(HealthLossEvent(1))  # TODO example
        self.handle_internal_event(TickEvent())

        for component in self.__dict__.values():
            if isinstance(component, BaseComponent):
                component.update()
        return super().update()
    

    # TODO does it even work with @dataclass and field?
    def __setattr__(self, name: str, value: Any):
        # If the attribute being set is an instance of Component, update its parent
        if isinstance(value, BaseComponent):
            value.parent = self
        super().__setattr__(name, value)


class Interactable(Entity, ABC):
    """Entity which is not alive and can be interacted with
    Blocks movement
    """
    # TODO think about how it should be in game
    def __init__(
        self,
        name: str,
        char: str,
        x: int,
        y: int,
        color: tuple[int, int, int],
    ):
        super().__init__(name, char, x, y, color, RenderOrder.INTERACTABLE, True)

    @abstractmethod
    def interact(self, actor: Actor):
        pass


class Item(Entity, ABC):
    def __init__(
        self,
        name: str,
        char: str,
        x: int,
        y: int,
        color: tuple[int, int, int],
        consumable: Consumable
    ):
        super().__init__(name, char, x, y, color, RenderOrder.INTERACTABLE, False)
        self.consumable = consumable

    # TODO prob we want create instances
    def update(self):
        pass
