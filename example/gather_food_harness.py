
from __future__ import annotations
from actions import InteractAction, MovementAction, PickupAction, WaitAction
from components.consumable import Food
from events.trigger import TickTrigger
from harnesses.action_in_area_harness import ActionInAreaHarness
from typing import TYPE_CHECKING
from engine import Engine

if TYPE_CHECKING:
    from actions import Action
    from entity import Actor, Interactable

class GatherFoodHarness(ActionInAreaHarness):
    def __init__(self, actor: Actor, radius: int):
        super().__init__(actor, radius, stop_triggers=[TickTrigger(5)])
        self.pointer = 0
        self.interactable: Interactable | None = None 
        self.next_interactable()


    def get_next_action(self) -> Action:
        game_map = Engine.instance().game_map
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                x = self.actor.x + dx
                y = self.actor.y + dy
                item = game_map.get_item_at_location(x, y)
                if item and isinstance(item.consumable, Food) and not self.actor.inventory.is_full():
                    return PickupAction(self.actor, item)
                
        if not self.interactable:
            print("No interactables around, just wait")
            return WaitAction(self.actor)
        path = self.get_path_to(self.interactable.x, self.interactable.y)
        if len(path) > 1:
            print(f"MovementAction", len(path))
            return MovementAction(self.actor, path[0][0] - self.actor.x, path[0][1] - self.actor.y)
        
        print(f"Interact with {self.interactable}")
        action = InteractAction(self.actor, self.interactable)
        self.next_interactable()
        return action
    
    def next_interactable(self) -> None:
        if len(self.interactables) == 0:
            return None
        self.interactable = self.interactables[self.pointer]
        self.pointer += 1
        if self.pointer >= len(self.interactables):
            self.pointer = 0
          
        

    def __str__(self) -> str:
        return "Gathering food"