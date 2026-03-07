from __future__ import annotations
import random
from operator import attrgetter


class Move:
    def __init__(self, name: str, damage: int, accuracy: int, type):
        self.name = name
        self.damage = damage
        self.accuracy = accuracy
        self.type = type

    def __str__(self):
        return self.name

    def use(self, user: Pokemon, target: Pokemon):
        print(f"{user.name} used {self.name}")
        if random.random() <= self.accuracy:
            target.hp -= self.damage
            print(f"hit!\n{target.name} took {self.damage} damage")

        else:
            print("Oh no! you missed!")
            return None


# a class for any pokemon, with a name, level, and basic hp multiplier. Also has moveset, types and hp. Need to add attack, defence, and speed stats, and possibly even correct scaling logic based on level for stats
class Pokemon:
    def __init__(
        self, name: str, types: list, hp_mod: int, moveset: list, level: int = 1
    ):
        self.name = name
        self.types = types
        self.level = level
        self.max_hp = hp_mod * self.level
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
        super().use()
        target.hp += self.power
        print(f"{target.name} recovered {self.power} hp")
        return Pokemon


def get_moves(all_moves: list, wanted_moves: list):
    moves = []

    for move in wanted_moves:
        moves.append(next((m for m in all_moves if m.name == move), None))

    return moves


moves = [
    Move("wing attack", 60, 1, "flying"),
    Move("bite", 60, 1, "normal"),
    Move("headbutt", 70, 1, "normal"),
    Move("body slam", 85, 1, "normal"),
    Move("thunder shock", 40, 1, "lightning"),
    Move("quick attack", 40, 1, "normal"),
    Move("vine whip", 45, 1, "grass"),
    Move("tackle", 40, 1, "normal"),
    Move("water gun", 40, 1, "water"),
    Move("scratch", 40, 1, "normal"),
    Move("ember", 40, 1, "fire")
]

# dataset for moves. will add more when they are needed
moves = {
    "wing attack": Move("wing attack", 60, 1, "flying"),
    "bite": Move("bite", 60, 1, "normal"),
    "headbutt": Move("headbutt", 70, 1, "normal"),
    "body slam": Move("body slam", 85, 1, "normal"),
    "thunder shock": Move("thunder shock", 40, 1, "lightning"),
    "quick attack": Move("quick attack", 40, 1, "normal"),
    "vine whip": Move("vine whip", 45, 1, "grass"),
    "tackle": Move("tackle", 40, 1, "normal"),
    "water gun": Move("water gun", 40, 1, "water"),
    "scratch": Move("scratch", 40, 1, "normal"),
    "ember": Move("ember", 40, 1, "fire"),
}

# dataset for pokemon. Need to add a lot more
pokemon_data = {
    "zubat": ("zubat", ["flying", "dark"], 10, [moves["wing attack"], moves["bite"]]),
    "snorlax": ("snorlax", ["normal"], 70, [moves["headbutt"], moves["body slam"]]),
    "pikachu": ("pikachu", ["electric"], 20, [moves["thunder shock"], moves["quick attack"]]),
    "bulbasaur": ("bulbasaur", ["grass", "poison"], 30, [moves["vine whip"], moves["tackle"]]),
    "squirtle": ("squirtle", ["water"], 25, [moves["water gun"], moves["tackle"]]),
    "charmander": ("charmander", ["fire"], 20, [moves["ember"], moves["tackle"]]),
}

# dataset for healing items. Will add more later
healing_item_data = [("potion", 20)]


def create_pokemon(name):
    return Pokemon(*pokemon_data[name])
