from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import textwrap

from components.base_component import BaseComponent
from engine import Engine
from events.base_event import BaseEvent

# from chromadb.utils import embedding_functions  # type: ignore


if TYPE_CHECKING:
    from datetime import datetime

    from chromadb.api.models.Collection import Collection  # type: ignore

    from entity import Actor

# Global counter. Could be a static variable of Observation class but it would be easier to shot yourself in the foot.
observation_id: int = 1


@dataclass
class Observation:
    """An observation made by an actor."""

    text: str
    event: BaseEvent | None = None
    gametime: datetime = field(default_factory=lambda: Engine.instance().time)
    id: int = field(default_factory=lambda: Observation.get_id())
    embedding: list[float] | None = None

    @staticmethod
    def get_id() -> int:
        global observation_id
        observation_id += 1
        return observation_id

    def __str__(self) -> str:
        formatted_datime = self.gametime.strftime("%y-%m-%d %H:%M")
        return f"[{formatted_datime}]: {self.text}"


class ObservationLog(BaseComponent):
    parent: Actor
    emb_collection: Collection | None = None

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.observations: list[Observation] = []

    def add(self, text: str, event: BaseEvent | None = None) -> None:
        """Add a observation to this log."""
        self.observations.append(Observation(text, event))

        print(f"Observation added: {text}")

        if len(self.observations) > self.capacity:
            self.observations.pop(0)

    def update(self) -> None:
        return super().update()

    def __str__(self) -> str:
        """Represent the log as text suitable for LLMs.

        It is supposed to be overloaded by agents.
        """
        return str(self.observations)

    # def make_embeddings(self) -> None:
    #     """Generate embeddings for the observations in this log.

    #     Batched instead of on-the-fly generation for efficiency.
    #     """
    #     if self.emb_collection is None:
    #         self.emb_collection = chroma_client.create_collection(
    #             name=f"{self.parent.name}_collection".lower() if self.parent else "sample_collection",
    #             embedding_function=_generate_embeddings,
    #         )

    #     observations_without_embeddings = [
    #         observation for observation in self.observations if observation.embedding is None
    #     ]

    #     embeddings = _generate_embeddings([observation.text for observation in observations_without_embeddings])

    #     self.emb_collection.add(
    #         embeddings=embeddings,
    #         documents=[str(observation) for observation in observations_without_embeddings],
    #         ids=[str(observation.id) for observation in observations_without_embeddings],
    #     )

    # TODO probably it would make sense to properly store Observation objects in the database
    # def query(self, text: str, amount: int = 1) -> list[str]:
    #     if self.emb_collection is None:
    #         self.make_embeddings()
    #     assert self.emb_collection is not None

    #     result = self.emb_collection.query(
    #         query_embeddings=_generate_embeddings([text]),
    #         n_results=amount,
    #     )

    #     print(f"Query {text} result: {result}")

    #     return result["documents"][0]  # type: ignore

    # @staticmethod
    # def wrap(string: str, width: int) -> Iterable[str]:
    #     """Return a wrapped text message."""
    #     for line in string.splitlines():  # Handle newlines in messages.
    #         yield from textwrap.wrap(
    #             line,
    #             width,
    #             expand_tabs=True,
    #         )

    def report(self, from_time: datetime, to_time: datetime | None = None) -> str:
        """Return the observations in the log as a string."""
        if to_time is None:
            to_time = Engine.instance().time
        filtered_observations: list[Observation] = []
        for observation in self.observations:
            if observation.gametime >= from_time and observation.gametime <= to_time:
                filtered_observations.append(observation)

        return "\n".join(map(str, filtered_observations))