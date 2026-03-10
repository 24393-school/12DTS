from __future__ import annotations

import random

# class for enhancements for rune. Going to give bonuses or abilities etc
class Enhancement:
    def __init__(self, name: str, tooltip: str, effect: callable()):
        self.name = name
        self.tooltip = tooltip
        self.effect = effect

# this will be what is on a side of a runestone. It will give points and have an effect on trigger. The colour is for synergies
class Rune:
    def __init__(self, name: str, colour: str, tooltip: str, effect: callable(), enhancement: callable()):
        self.name = name
        self.colour = colour
        self.tooltip = tooltip
        self.effect = effect
        self.enhancement = enhancement

    def activate(self):
        arcana, mask, = self.effect()

# this will be the "die" that the runes ar own. it will be rolled to get a rune
class Runestone:

    def __init__(self, affinity: str, sides: int, runes: list[Rune]):
        self.affinity = affinity
        self.sides = sides
        self.runes = runes
        self.mask = None

    def throw(self):
        print("you toss the runestone high into the air...")
        try:
            face = self.runes[random.randint(0, self.sides)]
            print(f"it lands on the glyph {face.name}. The rune begins to glow with power...")
            face.activate()

        except IndexError:
            print("it comes up blank")

# this is going to be all of the rune abilities here
def isa_effect():
    print("ice forms over all of your runestones, and snow begins to fly in the air... +10 arcana, and all other "
          "runes will be considered blue this round")
    return 10, "blue"




def create_rune(rune_name):
    return Rune(*RUNE_DATA[rune_name])


RUNE_DATA = {
    "isa": ("isa", "blue", "turns all your rune blue this round", isa_effect, None)
}

x = create_rune("isa")

die = Runestone("none", 2, [x])

die.throw()
