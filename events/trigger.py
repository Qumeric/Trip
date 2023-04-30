from abc import ABC, abstractmethod

from events.base_event import BaseEvent
from events.internal_events import HealthLossEvent, TickEvent


class StopTrigger(ABC):
    @abstractmethod
    def handle(self, event: BaseEvent) -> bool:
        pass

    @abstractmethod
    def report(self) -> str:
        pass


class HealthLossTrigger(StopTrigger):
    def __init__(self, amount_to_act: int) -> None:
        super().__init__()
        self.amount_to_act = amount_to_act
        self.hp_loss = 0

    def handle(self, event: BaseEvent) -> bool:
        if not isinstance(event, HealthLossEvent):
            return False
        self.hp_loss += event.amount
        return self.hp_loss >= self.amount_to_act

    def report(self) -> str:
        return f"You have lost {self.hp_loss} hp."


class TickTrigger(StopTrigger):
    def __init__(self, amount_to_act: int) -> None:
        super().__init__()
        self.amount_to_act = amount_to_act
        self.ticks = 0

    def handle(self, event: BaseEvent) -> bool:
        if not isinstance(event, TickEvent):
            return False
        self.ticks += 1

        print(f"Handle tick: {self.ticks}/{self.amount_to_act}")
        return self.ticks >= self.amount_to_act

    def report(self) -> str:
        return f"{self.ticks} has passed."
