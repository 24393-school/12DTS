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

class Pokemon:
    def __init__(self, name: str, types: list, level: int, max_hp: int, moves: list = []):
        self.name = name
        self.types = types
        self.level = level
        self.max_hp = max_hp * self.level
        self.hp = self.max_hp
        self.moves = moves


    def __str__(self):
        return self.name

def get_moves(all_moves: list, wanted_moves: list):
    moves = []

    for move in wanted_moves:
        moves.append(next((m for m in all_moves if m.name == "wing attack"), None))

    return moves

moves = [
    Move("wing attack", 60, 1, "flying"),
    Move("bite", 60, 1, "normal"),
    Move("headbutt", 70, 1, "normal"),
    Move("body slam", 85, 1, "normal"),
    Move("thunder shock", 40, 1, "lightning"),
    Move("quick attack", 40, 1, "normal")
]

pokemon = [
    Pokemon("zubat", ["flying", "dark"], random.randint(1, 3), random.randint(10, 30), get_moves(moves, ["wing attack", "bite"])),
    Pokemon("snorlax", ["normal"], random.randint(1,3), random.randint(20, 50), get_moves(moves, ["headbutt", "body slam"])),
    Pokemon("pikachu", ["electric"], random.randint(1, 3), random.randint(20, 40), get_moves(moves, ["thunder shock", "quick attack"]))
]

