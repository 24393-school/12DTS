# imports
from __future__ import annotations

import random
import time
import typing

# text colour library
from rich.console import Console
from rich.text import Text

# my file
import input_processing

# set for rich to use
CONSOLE = Console(highlight=False)

# Table to use on list comprehension strings to clean them. Unused currently, but may be needed in the future, so its staying
STRING_FORMATTING_TABLE = str.maketrans("", "", "[]'")


def slprint(string: str | Text):
    time.sleep(0.25)
    CONSOLE.print(string)


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

    # returns a detailed string of the spell's information
    @property
    def info(self):
        return Text.assemble(
            Text(f"{self.name}: ", f"{self.colour or 'purple'}"),
            "A ",
            Text(f"{self.colour or 'colourless'} ", f"{self.colour or 'purple'}"),
            "spell that costs ",
            Text(f"{self.arcana_cost} ARCANA", "purple"),
            ". ",
            self.tooltip,
            ", and will be " if self.empower_cost else "",
            Text("empowered ", "bold purple") if self.empower_cost else "",
            "for " if self.empower_cost else "",
            Text(f"{self.empower_cost} additional ARCANA ", "purple")
            if self.empower_cost
            else "",
            "to ",
            self.empower_desc if self.empower_cost and self.empower_desc else "",
            "\n",
        )

    # this method will be overriden by subclasses, but it checks if you empower the spell
    def cast(self, world_state: WorldState):
        empowered = False
        world_state.player.arcana -= self.arcana_cost
        if self.empower_cost and world_state.player.arcana >= self.empower_cost:
            world_state.player.arcana -= self.empower_cost
            slprint("[bold purple blink]EMPOWERED[/bold purple blink]")
            empowered = True
        return empowered


# each spell will be its own subclass. Origeonally I had a callable class variable, but now i've changed it to subclasses


# most basic spell. uses arcana and hurts an enemy
class ArcaneBolt(Spell):
    def __init__(self):
        super().__init__(
            "Arcane Bolt",
            5,
            10,
            None,
            Text.assemble("Deals ", Text("arcane ", "purple"), "damage to your enemy"),
            " gain increased damage",
        )

    def cast(self, world_state: WorldState):
        empowered = super().cast(world_state)
        slprint(
            f"you channel your [purple]ARCANA[/purple] into a {'[bold purple]mighty [/bold purple]' if empowered else ''}bolt of energy, and loose it at the enemy"
        )
        damage = random.randint(5, 10) + (
            5 if empowered else 0
        )  # randomises damage, and boosts it if its empowered
        world_state.current_enemy.injure(damage, world_state)

        return empowered


# A spell which heals the player
class HealSpell(Spell):
    def __init__(self):
        super().__init__(
            "Will of Frey",
            10,
            10,
            "green",
            Text.assemble(
                Text("Heals", "green"), " you, for ", Text("10-20 hp", "green")
            ),
            Text.assemble("gain increased ", Text("healing", "green"), " by 15 hp"),
        )

    def cast(self, world_state: WorldState):
        empowered = super().cast(world_state)

        slprint(
            f"You channel your [purple]ARCANA[/purple] into a chant of [green]Frey[/green]. Plants bloom around you, and your wounds {'[bold green]reseale themselves[/bold green]' if empowered else 'begin to close'}, filling you with {'[bold green]vigor[/bold green]' if empowered else 'hope'}"
        )

        heal_power = random.randint(10, 20) + (
            15 if empowered else 0
        )  # randomises healing

        slprint(f"You [green]heal {heal_power} hp[/green]")

        world_state.player.current_hp = min(
            world_state.player.current_hp + heal_power, world_state.player.max_hp
        )  # Caps hp at max

        slprint(f"You now have [green]{world_state.player.current_hp} hp[/green] left")

        return empowered


# spell that deals damage, plus extra if you have rolled blue runes
class LightningSpell(Spell):
    def __init__(self):
        super().__init__(
            "Wrath of Thor",
            30,
            35,
            "blue",
            Text.assemble(
                "Smites enemies with ",
                Text("lighting", "blue"),
                ". Gains bonus damage for each ",
                Text("blue", "blue"),
                " rune that you have thrown this round",
            ),
            Text.assemble(
                "grant your ",
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
            f"[blue]Lightning rends[/blue] the sky above,{f' drawing power from your [blue]{blue_rune_count} blue[/blue] {"runes" if blue_rune_count > 1 else "rune"}' if blue_rune_count else ''} {'[bold blue]smiting[/bold blue]' if empowered else 'striking'} your enemy {'as might pulses through you, [bold blue]energizing[/bold blue] your blue runes with [bold blue]crackling electricity[/bold blue]' if empowered else ''}"
        )

        damage = random.randint(20, 30) + random.randint(
            blue_rune_count * 5, blue_rune_count * 7
        )  # randomises the damage, with extra for each blue rune

        world_state.current_enemy.injure(damage, world_state)

        if empowered:
            world_state.player.thor_wrath += (
                10  # this buff makes the player's blue runes hurt the enemy
            )

        return empowered


# class for enhancements for rune. Going to give bonuses or abilities etc. WIP. unused currently.
class Enhancement:
    def __init__(self, name: str, tooltip: str, effect: typing.Callable):
        self.name = name
        self.tooltip = tooltip
        self.effect = effect


# these are what is on the side of a runestone each has a name, glyph, and tooltip
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
        # enhancement: Enhancement | None = None
    ):
        self.parent = parent

        self.name = name
        self.glyph = glyph
        self.truecolour = colour
        self.tooltip = tooltip
        self.meaning = meaning

        ## self.enhancement: Enhancement = enhancement      This will be where enhancements go (once I add them)

    # this colour property checks if the runestone that this rune is on has a colour mask on, and uses that if it does
    @property
    def colour(self):
        if self.parent:
            return self.parent.colour_mask or self.truecolour

        else:
            return self.truecolour

    # simmilar to Spell.info, this gives a detailed description of the rune's effects
    @property
    def info(self):
        return Text.assemble(
            Text(f"{self.name}", f"{self.colour}"),
            ": ",
            Text(self.meaning, self.colour),
            ". A ",
            Text(self.colour, self.colour),
            " rune that ",
            self.tooltip,
            "\n",
        )

    # this is the base method to be overriden completely by subclasses
    def activate(self, world_state: WorldState):
        pass

    def __str__(self):
        return self.name


# simmilar situation to spells, here. I origeonally had them as having a variable for effect, but they ended up needing a parameter which was essentially 'self', so I am now doing them as subclasses


# Ice rune. first oone implemented, it changes the colour of your other runestones for the round, and gives you arcana
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
            runestone.colour_mask = "blue"  # this is the part that temporarily changes the runestone's colour


# rune that heals the player, and gives arcana
class SowuloRune(Rune):
    def __init__(self, parent: Runestone):
        super().__init__(
            parent,
            "Sōwulō",
            "ᛊ",
            "yellow",
            Text.assemble(
                "grants ", Text("ARCANA", "purple"), " and ", Text("healing")
            ),
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


# rune that gives a choice of arcana or healing
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
                Text("healing", "green"),
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


# rune that does a random effect from a list. read the print text to know what they all do
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
                        "[orchid]Charming song[/orchid] echoes through your ears... Your enemy's [red]attack[/red] has been reduced by 2"
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
                        f"A spout of [orange]liquid fire[/orange] leaps from the runestone towards the enemy {world_state.current_enemy.name}, engulfing it in [orange]flame[/orange]..."
                    )

                    world_state.current_enemy.injure(15, world_state)

                case chance if 0.4 < chance <= 0.5:
                    slprint(
                        "[bright_white]dazzling[/bright_white] light scatters forth from your runestone... Enemy Accuracy reduced this round"
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


# the most simple rune, that just gives 5 arcana
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
            "[medium_purple1]Mystic energy[/medium_purple1] flows around you, forming into the shape of an [medium_purple1]Ash Tree[/medium_purple1]... Gain [purple]5 ARCANA[/purple]"
        )
        world_state.player.arcana += 5


# a rune which gives 5 arcana per rune in your bag, and thrown green rune
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
            f"[gold3]Golden light[/gold3] blossoms around you, and [purple]ARCANA[/purple] leaps from the runestones that you have left in your bag to your fingertips...  Gain [purple]{arcana_gain} ARCANA[/purple]"
        )
        world_state.player.arcana += arcana_gain


# this will be the "die" that the runes are on. it will be thrown to get a rune, which is then triggered
class Runestone:
    def __init__(self, material: str, sides: int, runes: list[Rune]):
        self.material = material
        self.sides = sides
        self.runes = runes

        self.colour_mask: str | None = None
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
                    f"{'' if self.runes.index(rune) == len(self.runes) else ', and ' if self.runes.index(rune) == len(self.runes) - 2 and len(self.runes) == self.sides else ', '}",
                )
                for rune in self.runes
            ],
            f"{f'{"and" if self.runes else ""} {self.sides - len(self.runes)} blank {"side" if self.sides - len(self.runes) == 1 else "sides"}' if self.sides - len(self.runes) else ''}",
            "\n",
        )

    @classmethod  # creates a blank runestone of a certain type
    def create_runestone(cls, base) -> Runestone:
        return Runestone(
            Runestone.RUNESTONE_TYPE_DATA[base][0],
            Runestone.RUNESTONE_TYPE_DATA[base][1],
            runes=[],
        )

    # creates a randomly generated runestone with random runes.
    @classmethod
    def generate_random_runestone(cls) -> Runestone:

        new_runestone = cls.create_runestone(
            random.choice(["base", "coin", "knucklebone"])
        )

        rune_count = int(
            random.normalvariate(new_runestone.sides / 2, new_runestone.sides / 6)
        )  # normal distribution to get the number of sides that the runestone will have

        new_runes = random.choices(NORMAL_RUNES, k=rune_count)

        new_runestone.add_runes(new_runes)

        return new_runestone

    # gives the runestone a nickname (which is the default str)
    def give_nickname(self):

        slprint(
            Text.assemble("enter a nickname for your ", self.info, "for ease of use")
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
                    slprint(
                        "your rune is full!"
                    )  # will not add a rune if all of your runes are full

            else:
                if len(self.runes) < self.sides:
                    self.runes.append(rune(self))

                else:
                    slprint("your rune is full!")

    # 'rolls' the runestone
    def throw(self, world_state: WorldState):

        slprint("you toss the runestone high into the air...")
        time.sleep(0.5)

        # gives any 'imbued' arcana to the player
        if world_state.player.arcana_income + world_state.player.temp_arcana_income:
            slprint(
                f"the lingering [purple]ARCANA[/purple] within your runestone suffuses you... Gain [purple]{world_state.player.arcana_income + world_state.player.temp_arcana_income} ARCANA[/purple]"
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
                    "The blessing of [bold blue]Thor[/bold blue] imbues the rune with power, as [blue]lightning[/blue] arcs from it towards the enemy..."
                )
                world_state.current_enemy.injure(
                    world_state.player.thor_wrath, world_state
                )

            # and activates it
            world_state.thrown_runes.append(face)

            face.activate(world_state)

    # strings it
    def __str__(self) -> str:
        return self.nickname or str(
            self.info
        )  # defaults to nickname, else gives the longform version


# custom list, just for runestones, which can do a detailed explanation of them
class RunestoneBag(list[Runestone]):
    # returns a detailed explanation of the runestones and runes on the runestones
    def explain(self, rune_info: bool = True) -> Text | str:
        explanation = "empty"
        runes: list[Rune] = []

        if self:
            explanation = Text("")
            runestone = None
            for i, runestone in enumerate(self, 1):
                explanation.append(
                    Text.assemble(
                        f" {i}. {runestone.nickname + ':' if runestone.nickname else ''} A ",
                        runestone.info,
                    )
                )
                if runestone and rune_info:
                    runestone_runes = [rune for rune in runestone.runes]

                    for rune in runestone_runes:
                        if rune.name not in [rune.name for rune in runes]:
                            runes.append(rune)

            # this bit will give the rune description
            if rune_info:
                explanation.append("These are the abilities of your runes\n\n")
                for rune in runes:
                    explanation.append(rune.info)
                    explanation.append("\n")

        return explanation


# practicly identical to the runestone bag, but for spells
class SpellBook(list[Spell]):
    def explain(self) -> Text:
        explanation = Text("")

        for i, spell in enumerate(self, 1):
            explanation.append(Text.assemble(f"{i}. ", spell.info, "\n"))

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
            if not world_state.player.current_hp <= 0:
                slprint(
                    f"you now have [red]{world_state.player.current_hp} hp[/red] left"
                )

        else:
            slprint("[cornflower_blue]miss![/cornflower_blue]")

    # base method to be overriden
    def take_turn(self, world_state):
        pass

    # this is called by other thing sto deal damage to the enemy
    def injure(self, damage, world_state: WorldState):

        if world_state.player.weakened:
            slprint(
                "you're [yellow4]weakened[/yellow4]! [yellow4]damage reduced[/yellow4]"
            )
            damage = int(damage * 0.75)

        slprint(f"[red]{damage} damage![/red]")

        self.current_hp = max(0, self.current_hp - damage)

        if self.current_hp > 0:
            slprint(f"the {self.name} has [red]{self.current_hp} hp left[/red]")

        else:
            slprint(f"you deafeat the {self.name}")


# subclass for chicken enemy
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


# an elite enemy, which is stronger than the chicken
class Turkey(Enemy):
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
                return f"planning to [red]attack[/red] for [red]{4 + self.attack_modifier} damage[/red], [bold red]three times[/bold red]"

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
                    f"it now has [green]{self.current_hp} hp[/green], and you've been [yellow4]distacted! Throw one less rune next turn[/yellow4]"
                )
                world_state.player.temp_runestone_cap -= 1
                self.sequence_step = 0

            case 2:
                slprint(
                    "The Colossal Turkey charges, and lets loose a [red]flurry[/red] of pecks at you"
                )
                for i in range(3):
                    self.attack(4, world_state)
                self.sequence_step = 0


# the boss enemy
class Goose(Enemy):
    def __init__(self, attack_mod=0, hp_mod=0):
        super().__init__("Gargantuan Goose", 55 + hp_mod, attack_mod)
        self.arcana = 0

    @property
    def action_foresight(self) -> str:
        match self.sequence_step:
            case 0:
                return f"planning to attack for [red]{15 + self.attack_modifier} damage[/red]"

            case 1:
                return (
                    "planning to throw one [medium_purple1]runestone[/medium_purple1]"
                )

            case 2:
                return "planning to [purple]cast ARCANE PECK[/purple]"

            case 3:
                return "planning to [purple]cast MIGHTY GUST[/purple]"

            case _:
                return "doing nothing"

    def take_turn(self, world_state: WorldState):
        match self.sequence_step:
            # basic attack
            case 0:
                slprint(
                    "the goose rushes towards you, and lets losse a [red]mighty peck[/red]"
                )
                self.attack(12, world_state)
                self.sequence_step = 1

            # does a random rune. In the future, I might add a subclass of runes for enemy runes that can be used
            case 1:
                slprint(
                    "The goose honks, and with its [purple]arcane[/purple] power a runestone is thrown into the air..."
                )
                time.sleep(0.5)
                rune_face = random.randint(0, 2)

                match rune_face:
                    # the equivilant of the heal/arcana choice rune
                    case 0:
                        slprint("the runestone lands on [green]ᚹ[/green]")
                        slprint("the rune [green]Wynn[/green]")
                        slprint("the rune glows with [green]green[/green] power...")
                        slprint("Vines burst from the earth in front of the goose")

                        if self.current_hp <= self.max_hp / 3:
                            slprint(
                                "the vines bloom with [green]invigorating melons[/green], which the goose eats"
                            )
                            slprint(
                                "the goose eats the apples, [green]healing 20 hp[/green]"
                            )
                            self.current_hp = min(self.current_hp + 20, self.max_hp)
                            slprint(
                                f"it now has [green]{self.current_hp} hp[/green] left"
                            )

                        else:
                            slprint(
                                "the vines blooom with [purple]invigorating lemons[/purple]"
                            )
                            slprint("the goose gains [purple]20 ARCANA[/purple]")
                            self.arcana += 20

                    # a heal and arcana rune
                    case 1:
                        slprint("the runestone lands on [yellow]ᛊ[/yellow]")
                        slprint("the rune [yellow]Sōwulō[/yellow]")
                        slprint("the rune glows with [yellow]yellow[/yellow] power...")
                        slprint(
                            f"heavenly light blesses the {self.name}... it gains [purple]5 ARCANA[/purple], and [green]heals 10 hp[/green]"
                        )
                        self.arcana += 5
                        self.current_hp = min(self.current_hp + 10, self.max_hp)
                        slprint(f"it now has [green]{self.current_hp} hp[/green] left")

                    # just gain arcana
                    case 2:
                        slprint("the runestone lands on [purple]ᚫ[/purple]")
                        slprint("the rune [purple]Æsc[/purple]")
                        slprint("the rune glows with [purple]yellow[/purple] power...")
                        slprint(
                            f"arcane power suffuses the {self.name}... it gains [purple]5 ARCANA[/purple]"
                        )
                        self.arcana += 5

                # chooses a move to go next, depending on the arcana cost
                if self.arcana >= 10:
                    self.sequence_step = 3

                elif 10 > self.sequence_step >= 5:
                    self.sequence_step = 2

                else:
                    self.sequence_step = random.randint(0, 1)

            # increases it attack bonus for 5 arcana
            case 2:
                slprint(
                    f"the {self.name} honks its arcana into an [purple]enchantment[/purple] upon it's beak... its [red]attack has increased by 3[/red]"
                )
                self.attack_modifier += 3
                self.arcana = 0
                self.sequence_step = 0

            # does a strong attack that weakens the player
            case 3:
                slprint(
                    f"the {self.name} honks its arcana into a mighty gust, which it flaps towards you, slamming into you with [red]immense force[/red]"
                )
                self.attack(30, world_state)
                slprint(
                    "you are [yellow4]destabilized[/yellow4]... you deal [yellow4]25% less damage next turn[/yellow4]"
                )
                world_state.player.weakened = True
                self.arcana = 0
                self.sequence_step = random.randint(0, 1)


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
        self.temp_arcana_income = 0  # temporary stat modifications
        self.temp_runestone_cap = 0
        self.thor_wrath = 0  # this is specificly for the wrath of thor spell
        self.weakened = (
            False  # this is a negative status effect that reduces the player's damage
        )

    # checks if all of the player's runes are full
    @property
    def all_runes_full(self):
        return (
            True
            if len([True for runestone in self.runestone_bag if runestone.full])
            == len(self.runestone_bag)
            else False
        )


# base class for any encounters, of which others will be subclassed into others. currently does basicly nothing, but will perahps do more when I add more kinds of encounters
class Encounter:
    def __init__(self) -> None:
        pass

    # this is overriden by subclasses
    @property
    def info(self) -> str:
        return "\n"


# class containing information fo any battle
class Battle(Encounter):
    def __init__(self, enemy: Enemy, rewards: list, difficulty: str) -> None:
        super().__init__()

        self.enemy = enemy
        self.rewards = rewards
        self.difficulty = difficulty

    @property
    def info(self) -> str:
        return f"{'An elite battle' if self.difficulty == 'elite' else 'A boss battle' if self.difficulty == 'boss' else 'A battle'} against a {self.enemy.name}"


# holds the key information needed for most things tp operate
class WorldState:
    def __init__(self, player: Player, current_enemy: Enemy):
        self.player = player
        self.current_enemy = current_enemy
        self.thrown_runestones: RunestoneBag = RunestoneBag([])
        self.thrown_runes: list[Rune] = []
        self.player.thor_wrath = 0


# lists of all of the types of things

NORMAL_RUNES = [IsazRune, SowuloRune, WynnRune, PeorthRune]
STARTER_RUNES = [AscRune, FehuRune]

NORMAL_ENEMIES = [Chicken]
ELITE_ENEMIES = [Turkey]

NORMAL_SPELLS = [HealSpell, LightningSpell]
STARTER_SPELLS = [ArcaneBolt]
