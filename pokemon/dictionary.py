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
            print(f"hit!\n"
                  f"{target.name} took {self.damage} damage")
            return self.damage
        else:
            print("Oh no! you missed!")
            return None


class Pokemon:
    def __init__(self, name: str, types: list, hp_mod: int, moveset: list    ,level: int ):
        self.name = name
        self.types = types
        self.level = level
        self.max_hp = hp_mod * self.level
        self.hp = self.max_hp
        self.moveset = moveset


    def __str__(self):
        return self.name

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

pokemon_data = [
    ("zubat", ["flying", "dark"], 10, get_moves(moves, ["wing attack", "bite"])),
    ("snorlax", ["normal"], 70, get_moves(moves, ["headbutt", "body slam"])),
    ("pikachu", ["electric"], 20, get_moves(moves, ["thunder shock", "quick attack"])),
    ("bulbasaur", ["grass", "poison"], 30, get_moves(moves, ["vine whip", "tackle"])),
    ("squirtle", ["water"], 25, get_moves(moves, ["water gun", "tackle"])),
    ("charmander", ["fire"], 20, get_moves(moves, ["ember", "tackle"]))
]



