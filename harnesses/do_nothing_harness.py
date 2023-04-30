from actions import Action, WaitAction
from entity import Actor
from harnesses.base_harness import BaseHarness


class DoNothingHarness(BaseHarness):
    def __init__(self, actor: Actor):
        super().__init__(actor, stop_triggers=[])

    def get_next_action(self) -> Action:
        return WaitAction(self.actor)

    def __str__(self) -> str:
        return "Do nothing"
