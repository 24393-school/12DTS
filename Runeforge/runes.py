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
    time.sleep(0.25)
    console.print(string)


# going to use your arcana to modify une effects, just here so I don't forget
# spell class, to use at end of turn. Each has a name and a cost, with an optional colour and/or info
class Spell:
    def __init__(
        self,
        name,
        arcana_cost: int,
        empower_cost: int | None = None,
        colour: str | None = None,
        tooltip: str | Text | None = None,
        empower_desc: str | Text | None = None,
    ):
        self.name = name
        self.arcana_cost = arcana_cost
        self.colour = colour
        self.empower_cost = empower_cost
        self.tooltip = tooltip or ""
        self.empower_desc = empower_desc

    @property
    def info(self):
        return Text.assemble(
            Text(f"{self.name}: ", f"{self.colour or 'purple'}"),
            "A ",
            Text(f"{self.colour or 'colourless'} ", f"{self.colour or 'purple'}"),
            "spell that ",
            self.tooltip,
            ", and can be empowered for " if self.empower_cost else "",
            Text(f"{self.empower_cost} additional ARCANA ", "purple")
            if self.empower_cost
            else "",
            "to ",
            self.empower_desc if self.empower_cost and self.empower_desc else "",
        )

    def cast(self, world_state: WorldState):
        empowered = False
        world_state.player.arcana -= self.arcana_cost
        if self.empower_cost and world_state.player.arcana >= self.empower_cost:
            world_state.player.arcana -= self.empower_cost
            slprint("[bold purple blink]EMPOWERED[/bold purple blink]")
            empowered = True
        return empowered


# each spell will be its own subclass. Origeonally I had a callable class variable, but now i've changed it to subclasses


# most basic spell. uses arcana and hits an enemy
class ArcaneBolt(Spell):
    def __init__(self):
        super().__init__(
            "Arcane Bolt",
            5,
            10,
            None,
            Text.assemble("deals ", Text("arcane ", "purple"), "damage to your enemy"),
            "gain increased damage",
        )

    def cast(self, world_state: WorldState):
        empowered = super().cast(world_state)
        slprint(
            f"you channel your [purple]ARCANA[/purple] into a {'[bold purple]mighty[/bold purple]' if empowered else ''} bolt of energy, and loose it at the enemy"
        )
        damage = random.randint(5, 10) + (5 if empowered else 0)
        world_state.current_enemy.injure(damage)

        return empowered


class HealSpell(Spell):
    def __init__(self):
        super().__init__(
            "Will of Frey",
            10,
            10,
            "green",
            Text.assemble(Text("Heals", "green"), " you"),
            Text.assemble("gain increased", Text("healing", "green")),
        )

    def cast(self, world_state: WorldState):
        empowered = super().cast(world_state)

        slprint(
            f"You channel your [purple]ARCANA[purple] into a chant of [green]Frey[/green]. Plants bloom around you, and your wounds {'[bold green]reseale themselves[/bold green]' if empowered else 'begin to close'}, filling you with {'[bold green]vigor[/bold green]' if empowered else 'hope'}"
        )

        heal_power = random.randint(10, 20) + 15 if empowered else 0

        slprint(f"You [green]heal {heal_power} hp[/green]")

        world_state.player.current_hp = min(
            world_state.player.current_hp + heal_power, world_state.player.max_hp
        )

        slprint(f"You now have [green]{world_state.player.current_hp} hp[/green] left")

        return empowered


class LightningSpell(Spell):
    def __init__(self):
        super().__init__(
            "Wrath of Thor",
            40,
            30,
            "blue",
            Text.assemble(
                "smites enemies with ",
                Text("lighting", "blue"),
                ". Gains bonus damage for each ",
                Text("blue", "blue"),
                " rune that you have thrown this round",
            ),
            Text.assemble(
                "grant your",
                Text("blue", "blue"),
                " runestones bonus damage for the rest of this fight",
            ),
        )

    def cast(self, world_state: WorldState):
        empowered = super().cast(world_state)

        blue_rune_count = 0

        for rune in world_state.thrown_runes:
            if rune.colour == "blue":
                blue_rune_count += 1

        slprint(
            f"You whip your [purple]ARCANA[/purple] into an immense shout, calling {'[bold blue]storms[/bold blue]' if empowered else 'thunder'} from above"
        )
        slprint(
            f"[blue]Lightning rends[/blue] the sky above, {f'drawing power from your [blue]{blue_rune_count} blue[/blue] runes' if blue_rune_count else ''} {'[bold blue]smiting[/bold blue]' if empowered else 'striking'} your enemy {'as might pulses through you, [bold blue]energizing[/bold blue] your blue runes with [bold blue]crackling electricity[/bold blue]' if empowered else ''}"
        )

        damage = random.randint(10, 20) + random.randint(
            blue_rune_count * 5, blue_rune_count * 7
        )

        world_state.current_enemy.injure(damage)

        return empowered


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
        parent: Runestone
        | None,  # this is the runestone they are on (so they can interact with it)
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
            Text.assemble(
                "Grants a choice of either ",
                Text("ARCANA", "purple"),
                ", or ",
                Text("hp", "green"),
            ),
            "The Bounty",
        )

    def activate(self, world_state: WorldState):
        slprint(
            "the ground cracks, and [green]vines[/green] burst from the earth... Would you like:\n"
        )
        slprint("1. [green]Healing fruit[/green] ([green]Heal 20 hp[/green])\n")
        slprint("2. [purple]Arcane fruit[/purple] ([purple]20 ARCANA[/purple])")
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

        def roll(max_rand: float = 1):
            while True:
                chance = random.random()
                if chance <= max_rand:
                    break

            slprint("[red]Chaotic[/red] energy darts around you...")

            match chance:
                case chance if chance <= 0.1:
                    slprint(
                        "Charming song echoes through your ears... Your enemy's [red]attack[/red] has been reduced by 2"
                    )
                    world_state.current_enemy.attack_modifier -= 2

                case chance if 0.1 < chance <= 0.3:
                    slprint(
                        "A painfull bolt of [purple]ARCANA[/purple] jolts through your veins... [red]Lose 5 hp[/red], but gain [purple]15 ARCANA[/purple]"
                    )

                    world_state.player.current_hp = max(
                        0, world_state.player.current_hp - 5
                    )

                    if world_state.player.current_hp > 0:
                        slprint(
                            f"You now have [red]{world_state.player.current_hp} hp[/red] left"
                        )

                    else:
                        slprint("You've killed yourself!")

                    world_state.player.arcana += 15

                case chance if 0.3 < chance <= 0.4:
                    slprint(
                        f"A spout of [orange]liquid fire[orange] leaps from the runestone towards the enemy {world_state.current_enemy.name}, engulfing it in [orange]flame[/orange]... [red]15 damage[/red]"
                    )

                    world_state.current_enemy.injure(15)

                case chance if 0.4 < chance <= 0.5:
                    slprint(
                        "[bright_white]dazzling[/bright_white] light scatters forth from your runestone... Enemy Accuracy reduced"
                    )
                    world_state.current_enemy.temp_accuracy_mod -= 0.5

                case chance if 0.5 <= chance <= 0.7:
                    slprint(
                        "A [bright_yellow]thunderous bolt[/bright_yellow] splits the sky above you, and [purple]ARCANA[/purple] imbues your remaining runestones... Your other runestones will each grant [purple]5 ARCANA[/purple] when thrown this round"
                    )
                    world_state.player.temp_arcana_income += 5

                case chance if 0.7 < chance <= 0.9:
                    slprint(
                        "an [medium_purple1]erie whistle[/medium_purple1] floats around you, and your feel your willpower leaving you... [red]lose[/red] [purple]10 ARCANA[/purple]"
                    )
                    world_state.player.arcana = max(0, world_state.player.arcana - 10)

                case chance if 0.9 < chance <= 0.95:
                    slprint(
                        "[bold red]darn... nat 1[/bold red]... lose all of your [purple]ARCANA[/purple], and [red]destroy[/red] this rune"
                    )
                    world_state.player.arcana = 0
                    if self.parent:
                        self.parent.runes.remove(self)
                        self.parent = None

                case chance if 0.95 < chance <= 1:
                    slprint(
                        "[bold green]Woo! nat 20![/bold green]... [pruple]Gain 30 ARCANA[/purple], then roll this rune twice more, for only good effects"
                    )
                    world_state.player.arcana += 30
                    for i in range(2):
                        roll(0.7)

                case _:
                    slprint("nothing happens")

        roll()


class AscRune(Rune):
    def __init__(self, parent: Runestone | None):
        super().__init__(
            parent,
            "Æsc",
            "ᚫ",
            "purple",
            Text.assemble("grants ", Text("ARCANA", "purple")),
            "The Tree",
        )

    def activate(self, world_state: WorldState):
        slprint(
            "[medium_purple1]Mystic energy[/medium_purple1] flows around you, forming into the shape of an [medium_purple1]Ash Tree[/medium_purple1]... Gain 5 [purple]ARCANA[/purple]"
        )
        world_state.player.arcana += 5


class FehuRune(Rune):
    def __init__(self, parent: Runestone):
        super().__init__(
            parent,
            "Fehu",
            "ᚠ",
            "green",
            Text.assemble(
                "grants ",
                Text("ARCANA ", "purple"),
                "for every runestone you have left in your bag, and every thrown ",
                Text("green", "green"),
                " rune (including this one)",
            ),
            "The Hoard",
        )

    def activate(self, world_state: WorldState):
        arcana_gain = (
            len(world_state.player.runestone_bag)
            + len([rune for rune in world_state.thrown_runes if rune.colour == "green"])
        ) * 5

        slprint(
            f"[gold3]Golden light[/gold3] blossoms around you, and [purple]ARCANA[/purple] leaps from the runestones that you have thrown to your fingertips...  Gain [purple]{arcana_gain} ARCANA[/purple]"
        )
        world_state.player.arcana += arcana_gain


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
    def full(self):
        return True if len(self.runes) == self.sides else False

    @property
    def info(
        self,
    ):  # this property gives the longhand information about the runes on the runestone. The nasty list comprehension ternery is for nice formmating, so I won't go into the full detail of it

        return Text.assemble(
            f"{self.sides}-sided {self.material} runestone, {'with the runes' if self.runes else 'with'} ",
            *[
                Text.assemble(
                    Text(rune.name, f"{rune.colour}"),
                    f"{',' if self.runes.index(rune) == len(self.runes) - 1 else ', '}",
                )
                for rune in self.runes
            ],
            f"{f' and {self.sides - len(self.runes)} blank {"side" if self.sides - len(self.runes) == 1 else "sides"}' if self.sides - len(self.runes) else ''}",
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

        new_runes = random.choices(NORMAL_RUNES, k=rune_count)

        new_runestone.add_runes(new_runes)

        return new_runestone

    # gives the runestone a nickname (which is the default str)
    def give_nickname(self):

        slprint(
            Text.assemble("enter a nickname for your", self.info, "for ease of use")
        )
        self.nickname = input()

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

        if world_state.player.arcana_income + world_state.player.temp_arcana_income:
            slprint(
                f"the lingering ARCANA within your runestone suffuses you... Gain [purple]{world_state.player.arcana_income + world_state.player.temp_arcana_income} ARCANA[/purple]"
            )
            world_state.player.arcana += (
                world_state.player.arcana_income + world_state.player.temp_arcana_income
            )

        # picks a random side...
        choice = random.randint(0, self.sides - 1)
        if choice >= len(self.runes):
            slprint("it comes up blank")
        else:
            face = self.runes[choice]

            slprint(
                f"it lands on the glyph [{face.colour}]{face.glyph}[/{face.colour}],\nThe rune [{face.colour}]{face.name}[/{face.colour}]\nThe rune begins to glow with [{face.colour}]{face.colour}[/{face.colour}] power..."
            )

            # if the player has any thor blessing, uses it
            if world_state.player.thor_wrath and face.colour == "blue":
                slprint(
                    f"The blessing of [bold blue]Thor[/bold blue] imbues the rune with power, as [blue]lightning[/blue] arcs from it towards the enemy..."
                )
                world_state.current_enemy.injure(world_state.player.thor_wrath)

            # and activates it
            face.activate(world_state)
            world_state.thrown_runes.append(face)

    # str
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
                        f" {i}. {runestone.nickname + ':' if runestone.nickname else ''} A ",
                        runestone.info,
                    )
                )

            return explanation

        else:
            return "empty"  # Just a fall through in case there are no runes


# practicly identical to the runestone bag, but por spells
class SpellBook(list[Spell]):
    def explain(self) -> Text:
        explanation = Text("")

        for i, spell in enumerate(self, 1):
            explanation.append(Text.assemble(f"{i}. ", spell.info))

        return explanation


# a class for enemies, of which all other enemies will be subclassed
class Enemy:
    def __init__(self, name, max_hp, attack_modifier, sequence_step: int = 0):
        self.name = name
        self.max_hp = max_hp
        self.current_hp = self.max_hp
        self.attack_modifier = attack_modifier  # modifier for the base damage of an attack (to customize the base attack sequences)
        self.sequence_step = sequence_step  # this indicates where in it's attack pattern the enemy is (will become clearer below)
        self.accuracy: float = 1
        self.temp_accuracy_mod: float = 0

    # property to be over-ridden, shows what the enemy will do next
    @property
    def action_foresight(self) -> str:
        return "doing nothing"

    # base attack, which damages the player based off a base damage stat, and the modifier
    def attack(self, base_attack: int, world_state: WorldState):
        damage = max(base_attack + self.attack_modifier, 1)
        slprint(f"[red]{damage} damage! [/red]")

        if random.random() <= self.accuracy + self.temp_accuracy_mod:
            world_state.player.current_hp -= damage
            if world_state.player.current_hp <= 0:
                slprint("you are slain...")

            else:
                slprint(
                    f"you now have [red]{world_state.player.current_hp} hp[/red] left"
                )

        else:
            slprint("[cornflower_blue]miss![/cornflower_blue]")

    # base method to be overriden
    def take_turn(self, world_state):
        pass

    def injure(self, damage):

        slprint(f"[red]{damage} damage![/red]")

        self.current_hp = max(0, self.current_hp - damage)

        if self.current_hp > 0:
            slprint(f"the {self.name} has [red]{self.current_hp} hp left[/red]")

        else:
            slprint(f"you deafeat the {self.name}")


# subclass for chicken
class Chicken(Enemy):
    def __init__(self, attack_mod=5, hp_mod=0):
        super().__init__("mighty chicken", 10 + hp_mod, attack_mod)

    # this is the chicken's attack pattern description, based off where it is in the pattern (applies to all enemies)
    @property
    def action_foresight(self) -> str:
        match self.sequence_step:
            case 0:
                return f"planning to [red]attack[/red] for [red]{5 + self.attack_modifier} damage[/red]"

            case 1:
                return f"planning to [red]attack[/red] for [red]{10 + self.attack_modifier} damage[/red]"

        return "doing nothing"

    # the chicken does a different action based off where it is in its action sequence (also applies to all enemies)
    def take_turn(self, world_state: WorldState):
        match self.sequence_step:
            case 0:
                slprint("The chicken claws!")
                self.attack(5, world_state)
                self.sequence_step = 1

            case 1:
                slprint("The mighty chicken pecks, with unnatural force!")
                self.attack(10, world_state)
                self.sequence_step = 0


class ColossalTurkey(Enemy):
    def __init__(self, attack_mod=0, hp_mod=0) -> None:
        super().__init__("Colossal Turkey", 30 + hp_mod, attack_mod)

    @property
    def action_foresight(self) -> str:
        match self.sequence_step:
            case 0:
                return f"planning to [red]attack[/red] for [red]{12 + self.attack_modifier} damage[/red]"

            case 1:
                return "planning to [green]heal[/green] for [green]10 hp[/green], and apply a [yellow4]negative status effect[/yellow4]"

            case 2:
                return f"planning to [red]attack[/red] for [red]{4 + self.attack_modifier} damage[/red], three times"

        return "doing nothing"

    def take_turn(self, world_state: WorldState):
        match self.sequence_step:
            case 0:
                slprint("The Colossal Turkey scrapes at you")
                self.attack(12, world_state)
                self.sequence_step = 1 if self.current_hp <= self.max_hp - 15 else 2

            case 1:
                slprint(
                    "The Colossal Turkey gobbles, [yellow4]distracting[/yellow4] you, and [green]regaining energy[/green]"
                )
                self.current_hp = min(self.current_hp + 10, self.max_hp)
                slprint(
                    f"it now has [green]{self.current_hp} hp[/green], and you've been [yellow4]distacted[/yellow4]! Throw one less rune next turn"
                )
                world_state.player.temp_runestone_cap -= 1
                self.sequence_step = 0

            case 2:
                slprint(
                    "The Colossal Turkey charges, and lets loose a flurry of pecks at you"
                )
                for i in range(3):
                    self.attack(4, world_state)
                self.sequence_step = 1


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
        self.max_hp = max_hp
        self.current_hp = self.max_hp
        self.arcana_income = 0
        self.temp_arcana_income = 0
        self.temp_runestone_cap = 0
        self.thor_wrath = 0  # this is specificly for the wrath of thor spell

    @property
    def all_runes_full(self):
        return (
            True
            if len([True for runestone in self.runestone_bag if runestone.full])
            == len(self.runestone_bag)
            else False
        )


class Encounter:
    def __init__(self) -> None:
        pass

    @property
    def info(self) -> str:
        return ""


class Battle(Encounter):
    def __init__(self, enemy: Enemy, rewards: list, difficulty: str) -> None:
        super().__init__()

        self.enemy = enemy
        self.rewards = rewards
        self.difficulty = difficulty

    @property
    def info(self) -> str:
        return f"{'An elite battle' if self.difficulty == 'elite' else 'A battle'} against a {self.enemy.name}"


# holds the key information needed for most things tp operate
class WorldState:
    def __init__(self, player: Player, current_enemy: Enemy):
        self.player = player
        self.current_enemy = current_enemy
        self.thrown_runestones: RunestoneBag = RunestoneBag([])
        self.thrown_runes: list[Rune] = []


# lists of all of the types of things

NORMAL_RUNES = [IsazRune, SowuloRune, WynnRune, PeorthRune]
STARTER_RUNES = [AscRune, FehuRune]

NORMAL_ENEMIES = [Chicken]
ELITE_ENEMIES = [ColossalTurkey]

NORMAL_SPELLS = [HealSpell, LightningSpell]
STARTER_SPELLS = [ArcaneBolt]
