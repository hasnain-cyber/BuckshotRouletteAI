from typing import Dict

from datatypes.Item import Item


class Entity:
    def __init__(self, current_health: int = 0, items: Dict[Item, int] = None):
        self.current_health = current_health
        self.items = items if items is not None else {}

    def __str__(self):
        return f"Health: {self.current_health}, Items: {self.items}"
