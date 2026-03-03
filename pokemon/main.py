import random

import dictionary, some_functions

wild_pokemon = []

for d in dictionary.pokemon_data:
    wild_pokemon.append(dictionary.Pokemon(d)) #need fix


# battle code
def battle(enemy_pokemon: dictionary.Pokemon, own_pokemon: list):
    # declairs the pokemon's stats
    print(f"A wild {enemy_pokemon.name} has appeared!")
    if len(enemy_pokemon.types) != 1:
        print(f"It is a {enemy_pokemon.types[0]} and {enemy_pokemon.types[1]} type pokemon")
    else:
        print(f"It is a {enemy_pokemon.types[0]} type pokemon")

    print(f"It has {enemy_pokemon.hp} health points")

    active_pokemon = own_pokemon[0]

    print(f"you have sent out {active_pokemon.name}, with {active_pokemon.hp} hp left")

    while True:
        action = some_functions.get_numbers_from_input("would you like to:\n"
                                                       "1. fight\n"
                                                       "2. flee\n"
                                                       "3. item\n"
                                                       "4. switch\n", 1, 4, False, 1)

        if action[0] == 1:  # attack
            print("your pokemon has these moves:")
            for move, i in zip(active_pokemon.moveset, range(len(active_pokemon.moveset))):  # list off moves
                print(f"{i + 1}. {move}")
            move_choice = active_pokemon.moveset[
                some_functions.get_numbers_from_input("Which move would you like to use?\n", 1, 3, False, 1)[
                    0] - 1]  # choose moves

            attack_power = move_choice.use(active_pokemon, enemy_pokemon)  # gets the move's damage, and damage the enemy

            if attack_power:
                enemy_pokemon.hp -= attack_power

            print(f"the enemy {enemy_pokemon.name} now has {enemy_pokemon.hp} hp left!\n")

        # enemy tun
        enemy_move = enemy_pokemon.moveset[random.randint(0, len(enemy_pokemon.moveset))]

        enemy_attack = enemy_move.use(enemy_pokemon, active_pokemon)
        if enemy_attack:
            active_pokemon.hp -= enemy_attack

        print(f"{active_pokemon.name} now has {active_pokemon.hp} hp left!")



# main loop
if __name__ == '__main__':
    # gets the starter pokemon
    starter_pokemon = [dictionary.all_pokemon[3], dictionary.all_pokemon[4], dictionary.all_pokemon[5]]

    # choos a starter
    own_pokemon = []
    print("you may choose a starter pokemon. These are your options:")

    for i in range(len(starter_pokemon)):
        print(f"{i + 1}. {starter_pokemon[i]}")

    own_pokemon.append(starter_pokemon[some_functions.get_numbers_from_input("", 1, 3, False, 1)[0] - 1])

    print(f"great! you chose {own_pokemon[0]}\n")

    battle(wild_pokemon[random.randint(0, len(wild_pokemon) - 1)], own_pokemon)
