import random
import time

import some_functions.py

import dictionary

wild_pokemon = []

for p in dictionary.pokemon_data:
    wild_pokemon.append(dictionary.create_pokemon(p))


# battle code
def battle(
    enemy_pokemon: dictionary.Pokemon, own_pokemon_roster: list, own_inventory: list
):
    # declairs the pokemon's stats
    print(f"A wild level {enemy_pokemon.level} {enemy_pokemon.name} has appeared!")
    if len(enemy_pokemon.types) != 1:
        print(
            f"It is a {enemy_pokemon.types[0]} and {enemy_pokemon.types[1]} type pokemon"
        )
    else:
        print(f"It is a {enemy_pokemon.types[0]} type pokemon")

    print(f"It has {enemy_pokemon.hp} health points")

    active_pokemon = own_pokemon_roster[0]

    print(f"you have sent out {active_pokemon.name}, with {active_pokemon.hp} hp left")

    while True:
        action = some_functions.get_numbers_from_input(
            "would you like to:\n1. fight\n2. flee\n3. item\n4. switch\n",
            1,
            4,
            False,
            1,
        )[0]

        if action == 1:  # attack
            print("your pokemon has these moves:")
            for move, i in zip(
                active_pokemon.moveset, range(len(active_pokemon.moveset))
            ):  # list off moves
                print(f"{i + 1}. {move}")
            move_choice = active_pokemon.moveset[
                some_functions.get_numbers_from_input(
                    "Which move would you like to use?\n", 1, 3, False, 1
                )[0]
                - 1
            ]  # choose moves

            move_choice.use(active_pokemon, enemy_pokemon)

            if enemy_pokemon.hp > 0:
                print(
                    f"the enemy {enemy_pokemon.name} now has {enemy_pokemon.hp} hp left!\n"
                )

            else:
                print(f"the enemy {enemy_pokemon.name} fainted!")
                enemy_pokemon.hp = 0
                return 1  # 1 will be a 'win' flag

        elif action == 2:  # running
            if random.random() > 0.3:
                print("you got away safely")
                return 2  # 2 will be a 'run' flag

            else:
                print("you couldn't escape")

        elif action == 3:  # using an item
            for item, i in zip(inventory, range(len(inventory))):
                print(f"{i + 1}. {item}")
                item_choice = inventory[
                    some_functions.get_numbers_from_input(
                        "", 1, len(inventory) + 1, False, 1
                    )[0]
                    - 1
                ]
                item_choice.use(active_pokemon)

        elif action == 4:  # switching pokemon
            possible_switches = [
                p for p in own_pokemon_roster if p.hp != 0 and p != active_pokemon
            ]
            if possible_switches:
                print("who would you like to switch in?")
                for p, i in zip(possible_switches, range(len(possible_switches))):
                    print(f"{i + 1}. {p.name}, with {p.hp} hp left")
                switch_choice = possible_switches[
                    some_functions.get_numbers_from_input(
                        "", 1, len(possible_switches) + 1, False, 1
                    )[0]
                    - 1
                ]
                print(f"great! you switched in {switch_choice.name}")
                active_pokemon = switch_choice

        # enemy tun
        time.sleep(1)
        print("enemy turn!")
        enemy_move = enemy_pokemon.moveset[
            random.randint(0, len(enemy_pokemon.moveset) - 1)
        ]

        enemy_move.use(enemy_pokemon, active_pokemon)

        if active_pokemon.hp > 0:
            print(f"{active_pokemon.name} now has {active_pokemon.hp} hp left!")

        else:
            print(f"Oh no! {active_pokemon.name} fainted!")
            active_pokemon.hp = 0

            possible_switches = [p for p in own_pokemon_roster if p.hp != 0]
            if possible_switches:
                print("who would you like to switch in?")
                for p, i in zip(possible_switches, range(len(possible_switches))):
                    print(f"{i + 1}. {p.name}, with {p.hp} hp left")
                switch_choice = possible_switches[
                    some_functions.get_numbers_from_input(
                        "", 1, len(possible_switches) + 1, False, 1
                    )[0]
                    - 1
                ]
                print(f"great! you switched in {switch_choice.name}")
                active_pokemon = switch_choice

            else:
                print("all of you pokemon have fainted! you have lost :{")
                return 0  # 0 will be a 'lose' flag


# main loop
if __name__ == "__main__":
    # gets the starter pokemon
    starter_pokemon = [
        dictionary.create_pokemon("bulbasaur"),
        dictionary.create_pokemon("squirtle"),
        dictionary.create_pokemon("charmander"),
    ]

    # choose a starter
    own_pokemon = []
    print("you may choose a starter pokemon. These are your options:")

    for i in range(len(starter_pokemon)):
        print(f"{i + 1}. {starter_pokemon[i]}")

    own_pokemon.append(
        starter_pokemon[
            some_functions.get_numbers_from_input("", 1, 3, False, 1)[0] - 1
        ]
    )

    print(f"great! you chose {own_pokemon[0]}\n")

    inventory = [dictionary.Healing_Item("potion", 20)]

    battle(
        wild_pokemon[random.randint(0, len(wild_pokemon) - 1)], own_pokemon, inventory
    )
