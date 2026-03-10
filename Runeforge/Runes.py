from __future__ import annotations

import random
import typing


# class for enhancements for rune. Going to give bonuses or abilities etc
class Enhancement:
    def __init__(self, name: str, tooltip: str, effect: typing.Callable):
        self.name = name
        self.tooltip = tooltip
        self.effect = effect


# this will be what is on a side of a runestone. It will give points and have an effect on trigger. The colour is for synergies
class Rune:
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
        (arcana, mask) = self.effect(arcana, mask)
        return arcana, mask


# this will be the "die" that the runes ar own. it will be rolled to get a rune
class Runestone:
    def __init__(self, material: str, sides: int, runes: list[Rune]):
        self.material = material
        self.sides = sides
        self.runes = runes
        self.mask = ""
        self.nickname = input("enter a nickname for your runestone for ease of use")

    def throw(self, arcana):
        print("you toss the runestone high into the air...")
        try:
            face = self.runes[random.randint(0, self.sides - 1)]
            print(
                f"it lands on the glyph {face.glyph}\nThe rune {face.name}\nThe rune begins to glow with {face.colour} power..."
            )
            face.activate(arcana, self.mask)

        except IndexError:
            print("it comes up blank")

    def __str__(self) -> str:
        return f"A {self.sides}-sided {self.material} runestone, with the runes {([r.name for r in self.runes])}".translate(
            STRING_FORMMATING_TABLE
        )


# this is going to be all of the rune abilities here
def isaz_effect(arcana, mask):
    print(
        "Ice forms over all of your runestones, and snow begins to fly in the air... +10 arcana, and all other "
        "runes will be considered blue this round"
    )
    return 10, "blue"


def create_rune(rune_name):
    return Rune(*RUNE_DATA[rune_name])


def sōwulō_effect():
    pass


RUNE_DATA = {
    "isaz": ("isaz", "ᛁ", "blue", "turns all your runes blue this round", isaz_effect),
    "sōwulō": ("sōwulō", "ᛊ", "yellow", "", sōwulō_effect),
}

STRING_FORMMATING_TABLE = str.maketrans("", "", "[]'")

x = create_rune("isaz")

die = Runestone("none", 2, [x, x])

print(die)
