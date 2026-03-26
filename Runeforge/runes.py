from __future__ import annotations

import random
import typing

COLOURS = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "PURPLE": "\033[95m",
    "RESET": "\033[0m",
}


STRING_FORMATTING_TABLE = str.maketrans("", "", "[]'")


# going to use your arcana to modify une effects, just here so I don't forget
class Spell:
    def __init__(
        self,
        name,
        arcana_cost: int,
        colour: list[str] | None = None,
        info: str | None = None,
    ):
        self.name = name
        self.arcana_cost = arcana_cost
        self.colour = colour

        self.info = info or ""

    def cast(self, world_state: WorldState):
        world_state.player.arcana -= self.arcana_cost


class ArcaneBolt(Spell):
    def __init__(self):
        super().__init__("Arcane Bolt", 5, None, "Deals arcane damage to your enemy")

    def cast(self, world_state: WorldState):
        super().cast(world_state)
        print(
            f"you channel your {COLOURS['PURPLE']}ARCANA{COLOURS['RESET']} into a bolt of energy, and loose it at the enemy"
        )
        damage = random.randint(5, 10)
        print(f"{COLOURS['RED']}{damage} damage{COLOURS['RESET']}")
        world_state.current_enemy.current_hp -= damage


# this is going to be all the rune abilities here. they will take, and return the game state, just mutating it. they also now use their pasrent rune, and its parent runestone


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
        parent: Runestone,
        name: str,
        glyph: str,
        colour: str,
        tooltip: str,
        ## enhancement: typing.Callable,
    ):
        self.parent = parent
        self.colour = colour
        self.name = name
        self.glyph = glyph
        ## self.name = f"{COLOURS[self.colour.upper()]}{name}{COLOURS['RESET']}"
        ## self.glyph = f"{COLOURS[self.colour.upper()]}{glyph}{COLOURS['RESET']}"
        self.colour = colour
        self.tooltip = tooltip

        ## self.enhancement = enhancement

    def activate(
        self, world_state: WorldState
    ):  # this is the base metod to be overriden
        pass

    def __str__(self):
        return self.name


class IsazRune(Rune):
    def __init__(self, parent: Runestone):
        super().__init__(
            parent, "Isaz", "ᛁ", "blue", "turns your runes blue this round"
        )

    def activate(self, world_state: WorldState):
        print(
            f"Ice forms over all of your runestones, and snow begins to fly in the air...  {COLOURS['PURPLE']}+10 ARCANA{COLOURS['RESET']}, and all other "
            "runes will be considered blue this round"
        )
        world_state.player.arcana += 10
        self.parent.mask = "blue"


class SowuloRune(Rune):
    def __init__(self, parent: Runestone):
        super().__init__(parent, "Sōwulō", "ᛊ", "yellow", "")

    def activate(self, world_state: WorldState):
        print(
            "radiant light shines from the heavens, and your soul glows bright with warmth"
        )


# this will be the "die" that the runes ar own. it will be rolled to get a rune
class Runestone:
    RUNESTONE_TYPE_DATA = {"base": ("stone", 3), "coin": ("metal", 2)}

    @property
    def info(self):

        info = f"{self.sides}-sided {self.material} runestone, with the runes"

        return (
            f"{self.sides}-sided {self.material} runestone, with the runes"
            + f" {[r.name for r in self.runes]}".translate(STRING_FORMATTING_TABLE)
        )

    @classmethod  # creates a blank runestone of a certain type
    def create_runestone(cls, base) -> Runestone:
        return Runestone(
            Runestone.RUNESTONE_TYPE_DATA[base][0],
            Runestone.RUNESTONE_TYPE_DATA[base][1],
            [],
        )

    def __init__(self, material: str, sides: int, runes: list[Rune]):
        self.material = material
        self.sides = sides
        self.runes = runes

        self.mask = ""
        self.nickname = None

    def give_nickname(self):
        self.nickname = input(f"enter a nickname for your {self.info} for ease of use ")

    def add_runes(self, runes: list[typing.Callable]):
        for rune in runes:
            if len(self.runes) < self.sides:
                self.runes.append(rune(self))

            else:
                print("your rune is full!")

    def throw(self, world_state: WorldState):

        print("you toss the runestone high into the air...")

        choice = random.randint(0, self.sides - 1)
        if choice >= len(self.runes):
            print("it comes up blank")
        else:
            face = self.runes[choice]

            print(
                f"it lands on the glyph {face.glyph},\nThe rune {face.name}\nThe rune begins to glow with {COLOURS[face.colour.upper()]}{face.colour}{COLOURS['RESET']} power..."
            )
            face.activate(world_state)

    def __str__(self) -> str:
        return self.nickname or self.info


class RunestoneBag(list[Runestone]):
    def explain(self) -> str:

        if self:
            explanation = ""

            for i, runestone in enumerate(self, 1):
                explanation += f"{i}. {runestone.nickname + ':' if runestone.nickname else ''} A {runestone.info}\n"

            return explanation

        else:
            return "empty"


class SpellBook(list):
    def explain(self) -> str:
        explanation = ""

        for i, spell in enumerate(self, 1):
            explanation += f"{i}. {spell.name}: A {spell.colour if spell.colour else 'colourless'} spell, costing {COLOURS['PURPLE']}{spell.arcana_cost} ARCANA{COLOURS['RESET']}. {spell.info}"

        return explanation


class Enemy:
    def __init__(self, name, max_hp, attack_power):
        self.name = name
        self.max_hp = max_hp
        self.current_hp = self.max_hp
        self.attack_powe = attack_power


# For use later to hold the player's stuff
class Player:
    def __init__(
        self,
        runestone_bag: RunestoneBag = RunestoneBag(),
        spells: SpellBook = SpellBook(),
        runestone_capacity: int = 1,
        arcana: int = 0,
    ) -> None:
        self.runestone_bag = runestone_bag
        self.spells = spells
        self.runestone_capacity = runestone_capacity
        self.arcana = arcana
        self.current_attack = 0


class WorldState:
    def __init__(self, player: Player, current_enemy: Enemy):
        self.player = player
        self.current_enemy = current_enemy


## x = create_rune("isaz")

## die = Runestone("none", 2, [x, x])

## print(die)
