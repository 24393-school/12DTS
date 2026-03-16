from __future__ import annotations

import random
import typing
from profile import run

STRING_FORMATTING_TABLE = str.maketrans("", "", "[]'")

# going to use your arcana to modify une effects, just here so I don't forget
class Spell:
    def __init__(self, arcana_cost: int, colour: list[str], effect: typing.Callable):
        self.arcana_cost = arcana_cost
        self.colour = colour
        self.effect = effect


# this is going to be all of the rune abilities here. they will take, and return the game state, just mutating it
def isaz_effect(arcana, mask, enemy_name):
    print(
        "Ice forms over all of your runestones, and snow begins to fly in the air... +10 arcana, and all other "
        "runes will be considered blue this round"
    )
    arcana += 10
    mask = "blue"
    return arcana, mask, 0


def sōwulō_effect(arcana, mask, enemy_name):
    print("radiant light shines from the heavens, and your soul glows bright with warmth")
    return arcana, mask, 0


# class for enhancements for rune. Going to give bonuses or abilities etc
class Enhancement:
    def __init__(self, name: str, tooltip: str, effect: typing.Callable):
        self.name = name
        self.tooltip = tooltip
        self.effect = effect


# this will be what is on a side of a runestone. It will give points and have an effect on trigger. The colour is for synergies
class Rune:
    RUNE_TYPE_DATA = {
        "isaz": ("isaz", "ᛁ", "blue", "turns all your runes blue this round", isaz_effect),
        "sōwulō": ("sōwulō", "ᛊ", "yellow", "", sōwulō_effect),
    }

    @classmethod
    def create_rune(cls, type) -> Rune:
        return Rune(*Rune.RUNE_TYPE_DATA[type])

    def __init__(
            self,
            name: str,
            glyph: str,
            colour: str,
            tooltip: str,
            effect: typing.Callable,
            ## enhancement: typing.Callable,
    ):
        self.name = name
        self.glyph = glyph
        self.colour = colour
        self.tooltip = tooltip
        self.effect = effect
        ## self.enhancement = enhancement

    def activate(self, arcana, mask):
        arcana, mask = self.effect(arcana, mask)
        return arcana, mask


# this will be the "die" that the runes ar own. it will be rolled to get a rune
class Runestone:
    RUNESTONE_TYPE_DATA = {"base": ("stone", 3, [])}

    @classmethod
    def create_runestone(cls, type, rune_overide: list = None) -> Runestone:
        if not rune_overide:
            return Runestone(*Runestone.RUNESTONE_TYPE_DATA[type])
        else:
            return Runestone(
                Runestone.RUNESTONE_TYPE_DATA[type][0], Runestone.RUNESTONE_TYPE_DATA[type][1], rune_overide
            )

    def __init__(self, material: str, sides: int, runes: list[Rune, bool]):
        self.material = material
        self.sides = sides
        self.runes = runes

        if len(self.runes) > sides:
            for i in range(sides - len(self.runes)):
                self.runes.append(None)

        self.mask = ""
        self.info = f"{self.sides}-sided {self.material} runestone, with the runes {([r.name for r in self.runes])}".translate(
            STRING_FORMATTING_TABLE
        )
        self.nickname = input(f"enter a nickname for your {self.info} for ease of use ")

    def throw(self, arcana, enemy_name):
        print("you toss the runestone high into the air...")
        try:

            face = self.runes[random.randint(0, self.sides - 1)]

            if face:
                print(
                    f"it lands on the glyph {face.glyph},\nThe rune {face.name}\nThe rune begins to glow with {face.colour} power..."
                )
                x = face.activate(arcana, self.mask, enemy_name)
                return x
            else:
                print("it comes up blank")

        except IndexError:
            print("it comes up blank")

    def __str__(self) -> str:
        return self.info


def runestone_explain(runestones):
    for runestone, i in zip(runestones, range(len(runestones))):
        if runestone.nickname:
            print(f"{i + 1}. {runestone.nickname}: A {runestone}")
        else:
            print(f"{i + 1}. A {runestone}")

# x = create_rune("isaz")

# die = Runestone("none", 2, [x, x])

# print(die)
