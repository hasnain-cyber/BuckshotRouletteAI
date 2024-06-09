from enum import Enum


class ItemType(Enum):
    MAGNIFYING_GLASS = 1
    CIGARETTES = 2
    BEER = 3
    HANDCUFFS = 4
    SAW = 5
    BURNER_PHONE = 6
    EXPIRED_MEDICINE = 7
    ADRENALINE = 8
    INVERTER = 9

    def properties(self):
        return {
            ItemType.MAGNIFYING_GLASS: {"name": "Magnifying Glass"},
            ItemType.CIGARETTES: {"name": "Cigarettes"},
            ItemType.BEER: {"name": "Beer"},
            ItemType.HANDCUFFS: {"name": "Handcuffs"},
            ItemType.SAW: {"name": "Saw"},
            ItemType.BURNER_PHONE: {"name": "Burner Phone"},
            ItemType.EXPIRED_MEDICINE: {"name": "Expired Medicine"},
            ItemType.ADRENALINE: {"name": "Adrenaline"},
            ItemType.INVERTER: {"name": "Inverter"}
        }[self]

    @property
    def name(self):
        return self.properties()['name']

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
