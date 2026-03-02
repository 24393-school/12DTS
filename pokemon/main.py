import random

import dictionary

wild_pokemon = dictionary.pokemon
def battle():
    enemy_pokemon = wild_pokemon[random.randint(0, len(wild_pokemon)-1)]

    print(f"a wild {enemy_pokemon.name} has appeared")
    if len(enemy_pokemon.types) != 1:
        print(f"it is a {enemy_pokemon.types[0]} and {enemy_pokemon.types[1]} type pokemon")
    else:
        print(f"it is a {enemy_pokemon.types[0]} type pokemon")

    print(f"it has {enemy_pokemon.hp} health points")

    while True:




if __name__ == '__main__':
    battle()

