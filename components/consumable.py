from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from events.internal_events import ConsumeEvent

if TYPE_CHECKING:
    from entity import Actor, Item
    from actions import Action, ItemAction


class Consumable(BaseComponent):
    parent: Item

    def __init__(self, name: str):
        self.name = name

    def update(self) -> None:
        pass

    def get_action(self, consumer: Actor) -> Action:
        """Try to return the action for this item."""
        return ItemAction(consumer, self.parent)

    @abstractmethod
    def activate(self, action: ItemAction) -> None:
        """Invoke this items ability.

        `action` is the context for this activation.
        """

    def consume(self, consumer: Actor) -> None:
        """Remove the consumed item from its containing inventory."""
        item = self.parent
        inventory = consumer.inventory
        inventory.items.remove(item)
        inventory.parent.observation_log.add(f"I consumed the {self.parent.name}")


class Food(Consumable):
    def __init__(self, name: str, nutrition: int, water_content: int):
        super().__init__(name)
        self.nutrition = nutrition
        self.water_content = water_content

    def activate(self, action: ItemAction) -> None:
        consumer = action.actor
        self.consume(consumer)
        consumer.handle_internal_event(ConsumeEvent(self))

class HealingConsumable(Consumable):
    def __init__(self, name: str, amount: int):
        super().__init__(name)
        self.amount = amount

    def activate(self, action: ItemAction) -> None:
        consumer = action.actor
        self.consume(consumer)
        consumer.handle_internal_event(ConsumeEvent(self))

