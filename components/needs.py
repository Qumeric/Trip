from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast

from components.base_component import BaseComponent
from events.internal_events import HealthLossEvent

if TYPE_CHECKING:
    from entity import Actor


# TODO it is very concrete, should be more abstract
# Users should be able to pass custom stuff here
@dataclass
class Needs(BaseComponent):
    max_hp: int

    max_hunger: int
    max_thirst: int
    max_sleepiness: int
    max_lonliness: int

    hunger = 0
    thirst = 0
    sleepiness = 0
    lonliness = 0

    parent: Actor = field(init=False)

    def __post_init__(self):
        self.hp = self.max_hp

    def report(self):
        return f"Hunger: {self.hunger}/{self.max_hunger},\
Thirst: {self.thirst}/{self.max_thirst},\
Sleepiness: {self.sleepiness}/{self.max_sleepiness},\
Lonliness: {self.lonliness}/{self.max_lonliness}"

    # TODO it shall be possible to have different change rates for different creatures
    def update(self):
        self.hunger += 1
        self.thirst += 1
        self.sleepiness += 1
        self.lonliness += 1

        if self.hunger >= self.max_hunger:
            self.parent.observation_log.add(text="I am starving!", event=None)
            self.parent.handle_internal_event(HealthLossEvent(1))
            self.hunger = self.max_hunger

        if self.thirst >= self.max_thirst:
            self.parent.observation_log.add(text="I am dying of thirst!", event=None)
            self.parent.handle_internal_event(HealthLossEvent(1))
            self.thirst = self.max_thirst

        if self.sleepiness >= self.max_sleepiness:
            self.parent.observation_log.add(text="I am extremely tired!", event=None)
            self.parent.handle_internal_event(HealthLossEvent(1))
            self.thirst = self.max_sleepiness

        if self.lonliness >= self.max_lonliness:
            self.parent.observation_log.add(text="I am extremely lonely!", event=None)
            self.parent.handle_internal_event(HealthLossEvent(1))
            self.lonliness = self.max_lonliness

    # # TODO unify with hp etc.
    # def eat(self, food: Food):
    #     self.hunger -= food.nutrition
    #     self.thirst -= food.water_content
    #     self.hunger = max(self.hunger, 0)
    #     self.thirst = max(self.thirst, 0)

    #     self.parent.observation_log.add(
    #         text=f"I am less hungry and thirsty! Hunger now: {self.hunger}, Thirst now: {self.thirst}", event=None
    #     )
