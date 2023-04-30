from abc import ABC, abstractmethod

from engine import Engine
from entity import Actor, Interactable, Item
from events.map_events import PickupEvent
import game_map
from game_map.game_map import GameMap


class Action(ABC):
    def __init__(self, actor: Actor) -> None:
        super().__init__()
        self.engine = Engine.instance()
        self.instant = False
        self.actor = actor

    @abstractmethod
    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.
        This method must be overridden by Action subclasses.
        """


class MovementAction(Action):
    def __init__(self, actor: Actor, dx: int, dy: int):
        super().__init__(actor)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> tuple[int, int]:
        """Returns this actions destination."""
        return self.actor.x + self.dx, self.actor.y + self.dy

    # TODO Prob unneeded. Each Actor etc should provides means of interaction, there is no target except for movement?
    # @property
    # def target_actor(self) -> Actor | None:
    #     """Return the actor at this actions destination."""
    #     return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            raise ValueError("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            raise ValueError("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            raise ValueError("That way is blocked.")

        # move_signal.send(
        #     self,
        #     event=MoveEvent(
        #         self.entity.x,
        #         self.entity.y,
        #         self.entity,
        #         self.dx,
        #         self.dy,
        #     ),
        # )
        self.actor.move(self.dx, self.dy)


class WaitAction(Action):
    def perform(self) -> None:
        pass


class ItemAction(Action):
    def __init__(self, entity: Actor, item: Item, target_xy: tuple[int, int] | None = None):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        self.item.consumable.activate(self)


class InteractAction(Action):
    def __init__(self, actor: Actor, interactable: Interactable):
        super().__init__(actor)
        self.interactable = interactable

    def perform(self) -> None:
        d = GameMap.chebyshev_distance((self.actor.x, self.actor.y), (self.interactable.x, self.interactable.y))
        if d > 1:
            raise ValueError(f"Too far away to interact with that. Distance: {d}")

        self.interactable.interact(self.actor)


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def __init__(self, actor: Actor, item: Item):
        super().__init__(actor)
        self.item = item

    def perform(self) -> None:
        actor_location_x = self.actor.x
        actor_location_y = self.actor.y
        inventory = self.actor.inventory

        game_map = Engine.instance().game_map
        if game_map.chebyshev_distance((actor_location_x, actor_location_y), (self.item.x, self.item.y)) <= 2:
            if len(inventory.items) >= inventory.capacity:
                raise ValueError("Your inventory is full.")

            self.engine.game_map.entities.remove(self.item)
            # item.parent = self.entity.inventory
            inventory.items.append(self.item)

            self.actor.handle_external_event(PickupEvent(self.item.x, self.item.y, actor=self.actor, item=self.item))
            return

        raise ValueError("There is nothing here to pick up.")
