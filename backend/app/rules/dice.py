import random
import secrets


def roll_d100() -> int:
    return secrets.randbelow(100) + 1


def roll_d10() -> int:
    return secrets.randbelow(10) + 1


def roll_dice(sides: int) -> int:
    return secrets.randbelow(sides) + 1
