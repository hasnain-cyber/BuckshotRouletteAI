from enum import Enum
from typing import List

from PySide6.QtGui import QColor

from datatypes.Entity import Entity
from datatypes.ItemType import ItemType


class BulletType(Enum):
    LIVE = 1
    BLANK = 2
    UNKNOWN = 3

    def properties(self):
        return {
            BulletType.LIVE: {"name": "Live", "color": QColor(255, 0, 0)},
            BulletType.BLANK: {"name": "Blank", "color": QColor(128, 128, 128)},
            BulletType.UNKNOWN: {"name": "Unknown", "color": QColor(0, 0, 255)}
        }[self]

    @property
    def name(self):
        return self.properties()['name']

    @property
    def color(self):
        return self.properties()['color']

    def __str__(self):
        return self.name


class State:
    def __init__(self, player: Entity = Entity(), enemy: Entity = Entity(),
                 bullets: List[BulletType] = None,
                 n_live_bullets: int = 0, max_health: int = 0,
                 is_handcuffed: bool = False, is_sawed_off: bool = False):
        self.player = player
        self.enemy = enemy
        self.bullets = bullets if bullets is not None else []
        self.n_live_bullets = n_live_bullets
        self.max_health = max_health
        self.is_handcuffed = is_handcuffed
        self.is_sawed_off = is_sawed_off

        # Set test state
        self.player.current_health = 1
        self.enemy.current_health = 2
        self.max_health = 2
        self.bullets = [BulletType.LIVE, BulletType.UNKNOWN]
        self.n_live_bullets = 1
        self.player.items = {ItemType.SAW: 1}
        self.enemy.items = {}

    def __str__(self):
        bullet_names = [bullet.name for bullet in self.bullets]
        return (f"Player: {{{self.player}}}, Enemy: {{{self.enemy}}}, "
                f"Bullets: {bullet_names}, Live Bullets: {self.n_live_bullets}, "
                f"Max Health: {self.max_health}, Is Handcuffed: {self.is_handcuffed}, "
                f"Is Sawed Off: {self.is_sawed_off}")
