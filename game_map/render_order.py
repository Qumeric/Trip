from enum import Enum, auto


class RenderOrder(Enum):
    ITEM = auto()
    INTERACTABLE = auto()
    ACTOR = auto()
