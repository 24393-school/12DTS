# imports
from __future__ import annotations

import random
import typing

# text colour library
from rich import print
from rich.text import Text

# will phase this out soon as I'm switching to Rich
COLOURS = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "PURPLE": "\033[95m",
    "RESET": "\033[0m",
}

# Table to use on list comprehension strings to clean them
STRING_FORMATTING_TABLE = str.maketrans("", "", "[]'")


# going to use your arcana to modify une effects, just here so I don't forget
# spell class, to use at end of turn. Each has a name and a cost, with an optional colour and/or info
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


# each spell will be its own subclass. Origeonally I had a callable class variable, but now i've changed it to subclasses


# most basic spell. uses arcana and hits an enemy
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


# class for enhancements for rune. Going to give bonuses or abilities etc. WIP. unused currently.
class Enhancement:
    def __init__(self, name: str, tooltip: str, effect: typing.Callable):
        self.name = name
        self.tooltip = tooltip
        self.effect = effect


# this will be what is on a side of a runestone. It will give arcana and have an effect on trigger. The colour is for synergies
class Rune:
    def __init__(
        self,
        parent: Runestone,  # this is the runestone they are on (so they can interact with it)
        name: str,  # this is the runes name (not glyph)
        glyph: str,  # this is the runic glyph
        colour: str,
        tooltip: str,  # a brief description
    ):
        self.parent = parent
        self.colour = colour
        self.name = name
        self.glyph = glyph
        self.colour = colour
        self.tooltip = tooltip

        ## self.enhancement: Enhancement = enhancement      This will be where enhancements go (once i ad them)

    # this is the base method to be overriden by subclasses
    def activate(self, world_state: WorldState):
        pass

    def __str__(self):
        return self.name


# simmilar situation to spells, here. I origeonally had them as having a variable for effect, but they ended up needing a parameter which was essentially 'self', so I am now doing them as subclasses


# Ice rune. first oone implemented, it changes the colour of your other runestones for the round, ad gives you arcana
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
        for runestone in world_state.player.runestone_bag:
            runestone.mask = "blue"  # this is the part that temporarily changes the runestone's colour


# sun rune. no effect currently
class SowuloRune(Rune):
    def __init__(self, parent: Runestone):
        super().__init__(parent, "Sōwulō", "ᛊ", "yellow", "")

    def activate(self, world_state: WorldState):
        print(
            "radiant light shines from the heavens, and your soul glows bright with warmth"
        )


# this will be the "die" that the runes are on. it will be 'thrown' to get a rune, which is then triggeres
class Runestone:
    def __init__(self, material: str, sides: int, runes: list[Rune]):
        self.material = material
        self.sides = sides
        self.runes = runes

        self.mask = ""
        self.nickname = None

    RUNESTONE_TYPE_DATA = {
        "base": ("stone", 3),
        "coin": ("metal", 2),
    }  # a dict of the base rune templates

    @property
    def info(
        self,
    ):  # this property gives the longhand information about the runes on the runestone. The nasty list comprehension ternery is for nice formmating

        return Text.assemble(
            f"{self.sides}-sided {self.material} runestone, with the runes ",
            *[
                Text.assemble(
                    Text(rune.name, f"{rune.colour}"),
                    f"{', ' if self.runes.index(rune) != len(self.runes) else ' and ' if self.runes.index(rune) == len(self.runes) - 1 else ''} ",
                )
                for rune in self.runes
            ],
        )

    @classmethod  # creates a blank runestone of a certain type
    def create_runestone(cls, base) -> Runestone:
        return Runestone(
            Runestone.RUNESTONE_TYPE_DATA[base][0],
            Runestone.RUNESTONE_TYPE_DATA[base][1],
            [],
        )

    # gives the runestone a nickname (which is the default str)
    def give_nickname(self):
        self.nickname = input(f"enter a nickname for your {self.info} for ease of use ")

    # adds a runes to blank sides of the runestone
    def add_runes(self, runes: list[typing.Callable]):
        for rune in runes:
            if len(self.runes) < self.sides:
                self.runes.append(rune(self))

            else:
                print("your rune is full!")

    # 'rolls' the runestone
    def throw(self, world_state: WorldState):

        print("you toss the runestone high into the air...")

        # picks a random side...
        choice = random.randint(0, self.sides - 1)
        if choice >= len(self.runes):
            print("it comes up blank")
        else:
            face = self.runes[choice]

            print(
                f"it lands on the glyph {face.glyph},\nThe rune {face.name}\nThe rune begins to glow with {COLOURS[face.colour.upper()]}{face.colour}{COLOURS['RESET']} power..."
            )

            # and activates it
            face.activate(world_state)

    # this might be bad form, but Rich Texts cand be used as just strings, so it should be all right
    def __str__(self) -> str | Text:
        return (
            self.nickname or self.info
        )  # defaults to nickname, else gives the longform version


# custom list, just for runestones, which can do a detailed explanation of them
class RunestoneBag(list[Runestone]):
    def explain(self) -> Text | str:

        if self:
            explanation = Text("")
            for i, runestone in enumerate(self, 1):
                explanation.append(
                    Text.assemble(
                        f" {i}. {runestone.nickname + ':' if runestone.nickname else ''} A",
                        runestone.info,
                    )
                )

            return explanation

        else:
            return "empty"  # Just a fall through in case there are no runes


# practicly identical to the runestone bag, but por spells
class SpellBook(list):
    def explain(self) -> str:
        explanation = ""

        for i, spell in enumerate(self, 1):
            explanation += f"{i}. {spell.name}: A {spell.colour if spell.colour else 'colourless'} spell, costing {COLOURS['PURPLE']}{spell.arcana_cost} ARCANA{COLOURS['RESET']}. {spell.info}"

        return explanation


# a class for enemies, of which all other enemies will be subclassed
class Enemy:
    def __init__(self, name, max_hp, attack_modifier, sequence_step: int = 0):
        self.name = name
        self.max_hp = max_hp
        self.current_hp = self.max_hp
        self.attack_modifier = attack_modifier  # modifier for the base damage of an attack (to customize the base attack sequences)
        self.sequence_step = sequence_step  # this indicates where in it's attack pattern the enemy is (will become clearer below)

    # property to be over-ridden, shows what the enemy will do next
    @property
    def action_foresight(self) -> str:
        return "doing nothing"

    # base attack, which damages the player based off a base damage stat, and the modifier
    def attack(self, base_attack: int, world_state: WorldState):
        damage = base_attack + self.attack_modifier
        print(
            f"The mighty {self.name} attacks for {COLOURS['RED']}{damage} damage{COLOURS['RESET']}"
        )
        world_state.player.current_hp -= damage

    # base method to be overriden
    def take_turn(self, world_state):
        pass


# subclass for chicken
class Chicken(Enemy):
    def __init__(self):
        super().__init__("chicken", 10, 5)

    # this is the chicken's attack pattern description, based off where it is in the pattern
    @property
    def action_foresight(self) -> str:
        match self.sequence_step:
            case 0:
                return f"planning to attack for {5 + self.attack_modifier} damage"

            case 1:
                return "planning to heal for 5"

            case 2:
                return f"planning to attack for {10 + self.attack_modifier} damage"

        return "doing nothing"

    # the chicken does a different action based off where it is in its action sequence
    def take_turn(self, world_state: WorldState):
        match self.sequence_step:
            case 0:
                self.attack(5, world_state)
                self.sequence_step = 1

            case 1:
                print("The mighty chicken heals 5 hp")
                self.current_hp += 5
                self.sequence_step = 2

            case 2:
                self.attack(10, world_state)
                self.sequence_step = 0


# The player character
class Player:
    def __init__(
        self,
        runestone_bag: RunestoneBag = RunestoneBag(),
        spells: SpellBook = SpellBook(),
        runestone_capacity: int = 1,
        arcana: int = 0,
        max_hp: int = 10,
    ) -> None:
        self.runestone_bag = runestone_bag  # holds runestones
        self.spells = spells  # holds spells
        self.runestone_capacity = (
            runestone_capacity  # how many runes the player can throw in a turn
        )
        self.arcana = arcana  # for casting spells
        self.current_attack = 0  # accumulated damage to do to the enemy
        self.max_hp = max_hp
        self.current_hp = self.max_hp


# holds the key information needed for most things tp operate
class WorldState:
    def __init__(self, player: Player, current_enemy: Enemy):
        self.player = player
        self.current_enemy = current_enemy
