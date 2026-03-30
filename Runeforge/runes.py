# imports
from __future__ import annotations

import random
import time
import typing

# text colour library
from rich.console import Console
from rich.text import Text

import input_processing

console = Console(highlight=False)

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


def slprint(string: str | Text):
    time.sleep(0.5)
    console.print(string)


# going to use your arcana to modify une effects, just here so I don't forget
# spell class, to use at end of turn. Each has a name and a cost, with an optional colour and/or info
class Spell:
    def __init__(
        self,
        name,
        arcana_cost: int,
        colour: str | None = None,
        tooltip: str | None = None,
    ):
        self.name = name
        self.arcana_cost = arcana_cost
        self.colour = colour

        self.tooltip = tooltip or ""

    @property
    def info(self):
        return Text.assemble(
            # f"[{self.colour if self.colour else 'purple'}]{self.name}[/{self.colour if self.colour else 'purple'}]. A [{self.colour or 'purple'}]{self.colour or 'colourless'}[/{self.colour or 'purple'}] spell that {self.tooltip}\n"
            Text(f"{self.name} ", f"{self.colour or 'purple'}"),
            "A ",
            Text(f"{self.colour or 'colourless'} ", f"{self.colour or 'purple'}"),
            f"spell that {self.tooltip}",
        )

    def cast(self, world_state: WorldState):
        world_state.player.arcana -= self.arcana_cost


# each spell will be its own subclass. Origeonally I had a callable class variable, but now i've changed it to subclasses


# most basic spell. uses arcana and hits an enemy
class ArcaneBolt(Spell):
    def __init__(self):
        super().__init__(
            "Arcane Bolt", 5, None, "deals [purple]arcane[/purple] damage to your enemy"
        )

    def cast(self, world_state: WorldState):
        super().cast(world_state)
        slprint(
            "you channel your [purple]ARCANA[/purple] into a bolt of energy, and loose it at the enemy"
        )
        damage = random.randint(5, 10)
        slprint(f"[red]{damage} damage [/red]")
        world_state.current_enemy.current_hp -= damage
        if world_state.current_enemy.current_hp <= 0:
            slprint(
                f"you [red]defeat[/red] the mighty {world_state.current_enemy.name}"
            )

        else:
            slprint(
                f"the mighty {world_state.current_enemy.name} has [red]{world_state.current_enemy.current_hp} hp left[/red]"
            )


class HealSpell(Spell):
    def __init__(self):
        super().__init__("Heal", 5, "green", "heals")


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
        tooltip: str | Text,  # a brief description
        meaning: str,  # flavour
    ):
        self.parent = parent

        self.name = name
        self.glyph = glyph
        self.truecolour = colour
        self.tooltip = tooltip
        self.meaning = meaning

        ## self.enhancement: Enhancement = enhancement      This will be where enhancements go (once i ad them)

    @property
    def colour(self):
        if self.parent:
            return self.parent.mask or self.truecolour

        else:
            return self.truecolour

    @property
    def info(self):
        return Text.assemble(
            # f"[{self.colour}]{self.name}[/{self.colour}]. A [{self.colour}]{self.colour}[/{self.colour}] rune that {self.tooltip}\n"
            Text(f"{self.name}", f"{self.colour}"),
            ": ",
            Text(self.meaning, self.colour),
            ". A ",
            Text(self.colour, self.colour),
            " rune that ",
            self.tooltip,
        )

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
            parent,
            "Isaz",
            "ᛁ",
            "blue",
            Text.assemble(
                "grants ",
                Text("ARCANA", "purple"),
                " and turns your runes ",
                Text("blue", "blue"),
                " this round\n",
            ),
            "The Rime",
        )

    def activate(self, world_state: WorldState):
        slprint(
            "[blue]Ice[/blue] forms over all of your runestones, and snow begins to fly in the air...  [purple] +10 ARCANA [/purple], and all other "
            "runes will be considered [blue]blue[/blue] this round"
        )
        world_state.player.arcana += 10
        for runestone in world_state.player.runestone_bag:
            runestone.mask = "blue"  # this is the part that temporarily changes the runestone's colour


# sun rune. no effect currently
class SowuloRune(Rune):
    def __init__(self, parent: Runestone):
        super().__init__(
            parent,
            "Sōwulō",
            "ᛊ",
            "yellow",
            Text.assemble("grants ", Text("ARCANA", "purple"), " and heals you"),
            "The Soul",
        )

    def activate(self, world_state: WorldState):
        slprint(
            "[yellow]Radiant light[/yellow] shines from the heavens, and your [yellow]SOUL[/yellow] glows bright with warmth... [green]Heal 10 hp[/green], and gain [purple]5 ARCANA[/purple]"
        )
        world_state.player.current_hp += 10

        world_state.player.current_hp = min(
            world_state.player.current_hp, world_state.player.max_hp
        )

        slprint(f"you now have [green]{world_state.player.current_hp} hp[/green] left")
        world_state.player.arcana += 5


class WynnRune(Rune):
    def __init__(self, parent: Runestone):
        super().__init__(
            parent,
            "Wynn",
            "ᚹ",
            "green",
            "Grants a choice of either ARCANA, or hp",
            "The Bounty",
        )

    def activate(self, world_state: WorldState):
        slprint(
            "the ground cracks, and [green]vines[/green] burst from the earth... Would you like:\n"
        )
        slprint("1. Healing fruit (Heal 20 hp)\n")
        slprint("2. [purple]Arcane[/purple] fruit")
        choice = input_processing.get_numbers_from_input(
            minimum=1, maximum=2, choice_amount=1
        )[0]

        match choice:
            case 1:
                slprint(
                    "The vines bloom with [green]invigorating apples[/green]...  [green]Heal 20 hp[/green]"
                )
                world_state.player.current_hp += 20
                if world_state.player.current_hp > world_state.player.max_hp:
                    world_state.player.current_hp = world_state.player.max_hp

                slprint(
                    f"you now have [green]{world_state.player.current_hp} hp[/green] left"
                )

            case 2:
                slprint(
                    "The vines bloom with [purple]energizing plums[/purple]...  Gain [purple]20 ARCANA[/purple]"
                )
                world_state.player.arcana += 20


class PeorthRune(Rune):
    def __init__(self, parent):
        super().__init__(
            parent, "Peorth", "ᛈ", "red", "grants a random effect", "The Gamble"
        )

    def activate(self, world_state: WorldState):
        chance = random.random()

        match chance:
            case chance if chance <= 0.1:
                print(
                    "Charming song echoes through your ears... Your enemy's [red]attack[/red] has been reduced by 2"
                )
                world_state.current_enemy.attack_modifier -= 2

            case chance if 0.1 < chance <= 0.3:
                print(
                    "A painfull bolt of [purple]ARCANA[/purple] jolts through your veins... [red]Lose 5 hp[/red], but gain [purple]15 ARCANA[/purple]"
                )

            case chance if 0.3 < chance <= 0.4:
                print(
                    f"A spout of [orange]liquid fire[orange] leaps from the runestone towards the enemy {world_state.current_enemy.name}, engulfing it in [orange]flame[/orange]... [red]15 damage[/red]"
                )

                if world_state.current_enemy.current_hp <= 0:
                    print(
                        f"You [red]defeat[/red] the enemy {world_state.current_enemy.name}"
                    )

                else:
                    print(
                        f"the enemy {world_state.current_enemy.name} has [red]{world_state.current_enemy.current_hp} hp[/red] left"
                    )

            case chance if 0.4 < chance <= 0.5:
                print("Whoops! All Ones")


# this will be the "die" that the runes are on. it will be 'thrown' to get a rune, which is then triggeres
class Runestone:
    def __init__(self, material: str, sides: int, runes: list[Rune]):
        self.material = material
        self.sides = sides
        self.runes = runes

        self.mask: str | None = None
        self.nickname = None

    RUNESTONE_TYPE_DATA = {
        "base": ("stone", 3),
        "coin": ("metal", 2),
        "knucklebone": ("bone", 4),
    }  # a dict of the base rune templates

    @property
    def info(
        self,
    ):  # this property gives the longhand information about the runes on the runestone. The nasty list comprehension ternery is for nice formmating, so I won't go into the full detail of it

        return Text.assemble(
            f" {self.sides}-sided {self.material} runestone, with the runes ",
            *[
                Text.assemble(
                    Text(rune.name, f"{rune.colour}"),
                    f"{'' if self.runes.index(rune) == len(self.runes) - 1 else ', and ' if self.runes.index(rune) == len(self.runes) - 2 else ', '}",
                )
                for rune in self.runes
            ],
            "\n",
        )

    @classmethod  # creates a blank runestone of a certain type
    def create_runestone(cls, base) -> Runestone:
        return Runestone(
            Runestone.RUNESTONE_TYPE_DATA[base][0],
            Runestone.RUNESTONE_TYPE_DATA[base][1],
            [],
        )

    # creates a randomly generated runestone with random runes.
    @classmethod
    def generate_random_runestone(cls) -> Runestone:

        new_runestone = cls.create_runestone(
            random.choice(["base", "coin", "knucklebone"])
        )

        rune_count = int(
            random.normalvariate(new_runestone.sides / 2, new_runestone.sides / 6)
        )

        new_runes = random.choices(ALL_RUNES, k=rune_count)

        new_runestone.add_runes(new_runes)

        return new_runestone

    # gives the runestone a nickname (which is the default str)
    def give_nickname(self):
        self.nickname = input(f"enter a nickname for your {self.info} for ease of use ")

    # adds a runes to blank sides of the runestone, either taking the TYPE of rune it is eg. IsazRune, SowuloRune, or an instance of a rune subclass, eg x = IsazRune()
    def add_runes(self, runes: list[Rune] | list[typing.Callable]):
        for rune in runes:
            if isinstance(rune, Rune):
                if len(self.runes) < self.sides:
                    self.runes.append(rune)
                    rune.parent = self

                else:
                    slprint("your rune is full!")

            else:
                if len(self.runes) < self.sides:
                    self.runes.append(rune(self))

                else:
                    slprint("your rune is full!")

    # 'rolls' the runestone
    def throw(self, world_state: WorldState):

        slprint("you toss the runestone high into the air...")

        # picks a random side...
        choice = random.randint(0, self.sides - 1)
        if choice >= len(self.runes):
            slprint("it comes up blank")
        else:
            face = self.runes[choice]

            slprint(
                f"it lands on the glyph [{face.colour}]{face.glyph}[/{face.colour}],\nThe rune {face.name}\nThe rune begins to glow with [{face.colour}]{face.colour}[/{face.colour}] power..."
            )

            # and activates it
            face.activate(world_state)

    # this might be bad form, but Rich Texts cand be used as just strings, so it should be all right
    def __str__(self) -> str:
        return self.nickname or str(
            self.info
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
            explanation += f"{i}. {spell.info}"

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
        damage = max(base_attack + self.attack_modifier, 1)
        slprint(f"The mighty {self.name} attacks for [red]{damage} damage [/red]")
        world_state.player.current_hp -= damage
        if world_state.player.current_hp <= 0:
            slprint("you are slain...")

        else:
            slprint(f"you now have [red]{world_state.player.current_hp} hp[/red] left")

    # base method to be overriden
    def take_turn(self, world_state):
        pass


# subclass for chicken
class Chicken(Enemy):
    def __init__(self, attack_mod=5, hp_mod=0):
        super().__init__("chicken", 10 + hp_mod, attack_mod)

    # this is the chicken's attack pattern description, based off where it is in the pattern
    @property
    def action_foresight(self) -> str:
        match self.sequence_step:
            case 0:
                return f"planning to [red]attack[/red] for [red]{5 + self.attack_modifier} damage[/red]"

            case 1:
                return "planning to [green]heal[/green] for [green]5 hp[/green]"

            case 2:
                return f"planning to [red]attack[/red] for [red]{10 + self.attack_modifier} damage[/red]"

        return "doing nothing"

    # the chicken does a different action based off where it is in its action sequence
    def take_turn(self, world_state: WorldState):
        match self.sequence_step:
            case 0:
                self.attack(5, world_state)
                self.sequence_step = 1 if self.current_hp < self.max_hp else 2

            case 1:
                slprint("The mighty chicken [green]heals 5 hp[/green]")
                self.current_hp += 5
                self.current_hp = min(self.current_hp, self.max_hp)
                slprint(f"It now has [red]{self.current_hp} hp[/red] left")
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


class Encounter:
    def __init__(self) -> None:
        pass


class Battle(Encounter):
    def __init__(self, enemy: Enemy, rewards: list) -> None:
        super().__init__()

        self.enemy = enemy
        self.rewards = rewards


# holds the key information needed for most things tp operate
class WorldState:
    def __init__(self, player: Player, current_enemy: Enemy):
        self.player = player
        self.current_enemy = current_enemy
        self.thrown_runes: RunestoneBag = RunestoneBag([])


# lists of all of the types of things

ALL_RUNES = [IsazRune, SowuloRune, WynnRune]

NORMAL_ENEMIES = [Chicken]

ALL_SPELLS = [ArcaneBolt, HealSpell]
