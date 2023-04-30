from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Entity


class BaseComponent(ABC):
    parent: Entity  # Owning entity instance.

    @abstractmethod
    def update(self) -> None:
        """Perform any logic that needs to happen on this component's turn."""
