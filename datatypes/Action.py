from enum import Enum
from typing import Union, Tuple

from datatypes.ItemType import ItemType


class FireTargetType(Enum):
    PLAYER = 1
    ENEMY = 2

    def properties(self):
        return {
            FireTargetType.PLAYER: {"name": "Player"},
            FireTargetType.ENEMY: {"name": "Enemy"}
        }[self]

    @property
    def name(self):
        return self.properties()['name']

    def __str__(self):
        return self.name


class ActionType(Enum):
    FIRE = 1
    USE_ITEM = 2
    NONE = 3

    def properties(self):
        return {
            ActionType.FIRE: {"name": "Fire"},
            ActionType.USE_ITEM: {"name": "Use Item"},
            ActionType.NONE: {"name": "None"}
        }[self]

    @property
    def name(self):
        return self.properties()['name']

    def __str__(self):
        return self.name


class Action:
    def __init__(self, action_type: ActionType,
                 target: Union[FireTargetType, ItemType, Tuple[ItemType, ItemType]]):
        self.action_type = action_type
        self.target = target

    def __str__(self):
        if isinstance(self.target, tuple):
            return f"{self.action_type}: {self.target[0]}, {self.target[1]}"
        else:
            return f"{self.action_type}: {self.target}"

    def __repr__(self):
        return self.__str__()
