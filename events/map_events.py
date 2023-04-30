from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

from events.base_event import BaseEvent

if TYPE_CHECKING:
    from entity import Actor, Entity, Item

@dataclass
class BaseMapEvent(BaseEvent, ABC):
    x: int
    y: int


@dataclass
class ActorEvent(BaseMapEvent, ABC):
    actor: Actor


@dataclass
class SpawnEvent(BaseMapEvent):
    entity: Entity


@dataclass
class AttackEvent(ActorEvent):
    target: Actor


@dataclass
class PickupEvent(ActorEvent):
    item: Item


@dataclass
class DropEvent(ActorEvent):
    item: Item


@dataclass
class UseEvent(ActorEvent):
    item: Actor
# @dataclass
# class MoveEvent(ActorEvent):
#     dx: int
#     dy: int
