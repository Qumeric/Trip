from __future__ import annotations

# TODO maybe it shall be moved from components? It is kinda weird...
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from rich import print

from components.base_component import BaseComponent
from engine import Engine
from events.base_event import BaseEvent

if TYPE_CHECKING:
    from entity import Actor
    from harnesses.base_harness import BaseHarness


class BaseAI(BaseComponent):
    parent: Actor
    harness: BaseHarness | None


    @abstractmethod
    def update(self) -> None:
        """Perform any logic that needs to happen on this component's turn."""
        if self.harness == None:
            self.start_time = Engine.instance().time

    @abstractmethod
    def handle_event(self, event: BaseEvent) -> None:
        """Handle an event that occured on the map."""


class SingleHarnessAI(BaseAI):
    def __init__(self, harness: BaseHarness):
        self.harness = harness

    def update(self) -> None:
        pass

    def handle_event(self, event: BaseEvent) -> None:
        pass

@dataclass
class HarnessFactory:
    harness_name: str
    harness_f: Callable[[],BaseHarness]

    def __call__(self) -> BaseHarness:
        return self.harness_f()


class ManualInputAI(BaseAI):
    harness: BaseHarness | None

    # TODO harnesses should be either created every time (probably better) or updated
    def __init__(self, harness_factories: list[HarnessFactory]):
        self.harness = None
        self.harness_factories = harness_factories

    def update(self) -> None:
        super().update()
        if self.harness is not None:
            return
        print("Choose harness:")
        for harness_factory in self.harness_factories:
            print(f"{self.harness_factories.index(harness_factory)}: {harness_factory.harness_name}")

        factory_index = int(input())
        harness_factory = self.harness_factories[factory_index]
        self.harness = harness_factory()

    def handle_event(self, event: BaseEvent) -> None:
        super().handle_event(event)
        if self.harness is None:
            return
        report = self.harness.handle_event(event)
        if report is not None:
            print(f"Harness interrupted due to: {report}")
            self.harness = None
