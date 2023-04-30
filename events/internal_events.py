from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from events.base_event import BaseEvent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from components.consumable import Consumable
  from entity import Item

@dataclass
class BaseInternalEvent(BaseEvent, ABC):
    pass


@dataclass
class TickEvent(BaseInternalEvent):
    pass


@dataclass
class HealthLossEvent(BaseInternalEvent):
    amount: int

@dataclass
class HealEvent(BaseInternalEvent):
    amount: int

@dataclass
class ConsumeEvent(BaseInternalEvent):
    consumable: Consumable