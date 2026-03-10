from __future__ import annotations

import random
from operator import attrgetter


def calculate_damage(
    level, crit, power, attack, defense, speed, bonus, type_effectiveness
):

    crit_chance = (speed / 2) / random.randint(0, 255)

    if crit_chance > 255 / 256:
        crit_chance = 255 / 256
    if random.random() < crit_chance:
        crit = 2
    else:
        crit = 1

    damage = (
        ((((((2 * level * crit) / 5) + 2) * power * (attack / defense)) / 50) + 2)
        * bonus
        * type_effectiveness
        * random
    )

    return damage


# class for types, for pokemon and moves. Can find effectiveness against other types. WIP
class Type:
    def __init__(
        self, name: str, super_effective: list, not_effective: list, no_effect: list
    ):
        self.name = name
        self.super_effective = super_effective
        self.not_effective = not_effective
        self.no_effect = no_effect

    def __eq__(self, other):
        if self.name == other.name:
            return True
        return False

    def __str__(self):
        return self.name

    # this finds the move's effectiveness against a target of given types
    def get_effectiveness(self, other_types: list):
        effectiveness = 1
        for type in other_types:
            if type.name in self.super_effective:
                effectiveness *= 2
            elif type.name in self.not_effective:
                effectiveness *= 0.5
            elif type.name in self.no_effect:
                effectiveness *= 0

        if effectiveness > 1:
            print("it's super effective!")
        elif 0 < effectiveness < 1:
            print("it's not very effective...")

        elif effectiveness == 0:
            print("it has no effect...")

        return effectiveness


# a class for moves, currently only supports attack moves with no special effects, but has a type. form is for sp vs phys attacks
class Move:
    def __init__(
        self, name: str, damage: int, accuracy: int, type: Type, form: str = "phys"
    ):
        self.name = name
        self.damage = damage
        self.accuracy = accuracy
        self.type = type
        self.form = form

    def __str__(self):
        return self.name

    # checks for accuracy, and if hits, applies damage to the target. Need to add type effectiveness logic
    def use(self, user: Pokemon, target: Pokemon):
        print(f"{user.name} used {self.name}")
        if random.random() <= self.accuracy:
            modified_damage = self.damage * self.type.get_effectiveness(target.types)
            target.hp -= modified_damage
            print(f"hit!\n{target.name} took {modified_damage} damage")

        else:
            print("Oh no! you missed!")


# a class for any pokemon, with a name, level, and basic hp multiplier. Also has moveset, types and hp. Need to add attack, defence, and speed stats, and possibly even correct scaling logic based on level for stats
class Pokemon:
    def get_stats(self):
        self.max_hp = (
            abs(((self.hp_base + self.hp_mod) * 2) * self.level) / 100 + self.level + 10
        )
        self.stat = abs(((self.hp_base + self.hp_mod) * 2) * self.level) / 100 + 5

    def __init__(
        self,
        name: str,
        types: list[Type],
        hp_mod: int,
        hp_base: int,
        moveset: list,
        level: int = 1,
    ):
        self.hp_mod = hp_mod
        self.hp_base = hp_base
        self.name = name
        self.types = types
        self.level = level
        self.max_hp = hp_base + hp_mod * self.level
        self.hp = self.max_hp
        self.moveset = moveset

    def __repr__(self):
        return f"Pokemon({self.name}, {self.types}, {self.max_hp}, {self.hp}, {self.moveset}, {self.level})"

    def __str__(self):
        return self.name


# base item class to be overriden, has a use ability that targets a pokemon. Not much else yet
class Item:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def use(self, target: Pokemon):  # gonna be over-ridden by subclasses
        raise NotImplementedError


# class for healing items, heals a pokemons hp by it's strength. Might add some other stuff later (special effects etc)
class Healing_Item(Item):
    def __init__(self, name, power):
        self.name = name
        self.power = power

    def use(self, target: Pokemon):
        target.hp += self.power
        print(f"{target.name} recovered {self.power} hp!\n It now has {target.hp} hp")


# dataset for all types, unfinished
TYPES = {
    "normal": Type("normal", [], ["rock", "steel"], ["ghost"]),
    "fire": Type(
        "fire",
        ["grass", "ice", "bug", "steel"],
        ["fire", "water", "rock", "dragon"],
        [],
    ),
    "water": Type(
        "water", ["fire", "ground", "rock"], ["water", "grass", "dragon"], []
    ),
    "grass": Type(
        "grass",
        ["water", "ground", "rock"],
        ["fire", "grass", "poison", "flying", "bug", "dragon", "steel"],
        [],
    ),
    "electric": Type(
        "electric", ["water", "flying"], ["grass", "electric", "dragon"], ["ground"]
    ),
    "ice": Type(
        "ice",
        ["grass", "ground", "flying", "dragon"],
        ["fire", "water", "ice", "steel"],
        [],
    ),
    "fighting": Type(
        "fighting",
        ["normal", "ice", "rock", "dark", "steel"],
        ["poison", "flying", "psychic", "bug", "fairy"],
        [],
    ),
    "poison": Type(
        "poison", ["grass", "fairy"], ["poison", "ground", "rock", "ghost"], ["steel"]
    ),
    "ground": Type(
        "ground",
        ["fire", "electric", "poison", "rock", "steel"],
        ["grass", "bug"],
        ["ground"],
    ),
    "flying": Type(
        "flying", ["grass", "fighting", "bug"], ["electric", "rock", "steel"], []
    ),
    "pyschic": Type("psychic", ["fighting", "poison"], ["psychic", "steel"], ["dark"]),
    "bug": Type(
        "bug",
        ["grass", "psychic", "dark"],
        ["fire", "fighting", "poison", "flying", "ghost", "steel", "fairy"],
        [],
    ),
    "rock": Type(
        "rock", ["fire", "ice", "flying", "bug"], ["fighting", "ground", "steel"], []
    ),
    "ghost": Type("ghost", ["ghost", "psychic"], ["dark"], ["normal"]),
    "dragon": Type("dragon", ["dragon"], ["steel"], ["fairy"]),
    "dark": Type("dark", ["psychic", "ghost"], ["dark", "fairy"], []),
    "steel": Type(
        "steel", ["ice", "rock", "fairy"], ["fire", "water", "grass", "steel"], []
    ),
    "fairy": Type(
        "fairy", ["fighting", "dragon", "dark"], ["fire", "poison", "steel"], []
    ),
}

# dataset for moves. will add more when they are needed
MOVES = {
    "wing attack": Move("wing attack", 60, 1, TYPES["flying"]),
    "bite": Move("bite", 60, 1, TYPES["normal"]),
    "headbutt": Move("headbutt", 70, 1, TYPES["normal"]),
    "body slam": Move("body slam", 85, 1, TYPES["normal"]),
    "thunder shock": Move("thunder shock", 40, 1, TYPES["electric"]),
    "quick attack": Move("quick attack", 40, 1, TYPES["normal"]),
    "vine whip": Move("vine whip", 45, 1, TYPES["grass"]),
    "tackle": Move("tackle", 40, 1, TYPES["normal"]),
    "water gun": Move("water gun", 40, 1, TYPES["water"]),
    "scratch": Move("scratch", 40, 1, TYPES["normal"]),
    "ember": Move("ember", 40, 1, TYPES["fire"]),
}

# dataset for pokemon. Need to add a lot more
pokemon_data = {
    "zubat": (
        "zubat",
        [TYPES["flying"], TYPES["dark"]],
        10,
        50,
        [MOVES["wing attack"], MOVES["bite"]],
    ),
    "snorlax": (
        "snorlax",
        [TYPES["normal"]],
        70,
        150,
        [MOVES["headbutt"], MOVES["body slam"]],
    ),
    "pikachu": (
        "pikachu",
        [TYPES["electric"]],
        20,
        70,
        [MOVES["thunder shock"], MOVES["quick attack"]],
    ),
    "bulbasaur": (
        "bulbasaur",
        [TYPES["grass"], TYPES["poison"]],
        30,
        80,
        [MOVES["vine whip"], MOVES["tackle"]],
    ),
    "squirtle": (
        "squirtle",
        [TYPES["water"]],
        25,
        75,
        [MOVES["water gun"], MOVES["tackle"]],
    ),
    "charmander": (
        "charmander",
        [TYPES["fire"]],
        20,
        70,
        [MOVES["ember"], MOVES["tackle"]],
    ),
}

# dataset for healing items. Will add more later
healing_item_data = [("potion", 20)]


def create_pokemon(name):
    return Pokemon(*pokemon_data[name])
