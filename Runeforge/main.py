# imports
import random
import sys
import time

import runes
import some_functions_copy


# function for choosing some runes to use from a list
def choose_runes(world_state: runes.WorldState):
    print(
        f"Choose up to {world_state.player.runestone_capacity} runestones from your bag. Enter ? for more detail:"
        # ? here gives the full description
    )
    for runestone, i in zip(world_state.player.runestone_bag, range(len(world_state.player.runestone_bag))):
        if runestone.nickname:
            print(f"{i + 1}. {runestone.nickname}")
        else:
            print(f"r{i + 1}. {runestone}")

    user_input = some_functions_copy.get_numbers_from_input(
        "", 1, len(world_state.player.runestone_bag), False, world_state.player.runestone_capacity, "?"
    )

    if user_input == "?":
        runes.runestone_explain(world_state.player.runestone_bag)

    else:
        runestone_choices = [world_state.player.runestone_bag[i - 1] for i in user_input]
        print("you have chosen:")
        for rune in runestone_choices:
            print(rune.nickname)

        return runestone_choices


# battle function for fighting enemies. takes enemy and player data. Will Class player and enemy later
def battle(world_state: runes.WorldState, enemy: runes.Enemy):
    print(f"An enemy approaches: a mighty {enemy.name}")
    print("they draw their runestones")
    print("so do you")

    # selection phase for the turn. In this part, the player chooses which of their runestones they will use

    runestone_choices = choose_runes(world_state)

    while True:
        runestone_confirmation = some_functions_copy.get_confirmation()

        if runestone_confirmation:
            print("runestones selected")
            break

        else:
            print("All right. Choose again")
            runestone_choices = choose_runes(world_state)

    # choose the stones to throw (in order)
    for i in range(len(runestone_choices)):
        if i != 0:
            print(
                "you draw your runestones from your bag... which would you like to throw next? Press ? for more info,"
                "and type 'end' to end your throw phase"
            )

        else:
            print(
                "you draw your runestones from your bag... which would you like to throw first? Press ? for more info, "
                "and type 'end' to end your throw phase"
            )

        for runestone, i in zip(runestone_choices, range(len(runestone_choices))):
            if runestone.nickname:
                print(f"{i + 1}. {runestone.nickname}")
            else:
                print(f"{i + 1}. {runestone}")

        throw_rune_choice = True
        while throw_rune_choice:
            user_input = some_functions_copy.get_numbers_from_input(
                "", 1, len(runestone_choices), False, 1, ["?", "end"]
            )[0]

            # explains
            if user_input == "?":
                runes.runestone_explain(world_state.player.runestone_bag)

            # ends turn early
            elif user_input == "end":
                confirm = some_functions_copy.get_confirmation()
                if confirm:
                    break

            else:
                thrown_rune = runestone_choices[user_input - 1]
                arcana, player_attack = thrown_rune.throw(
                    world_state
                )
                throw_rune_choice = False
                runestone_choices.pop(runestone_choices.index(thrown_rune))
                enemy.current_hp -= player_attack
                player_attack = 0

            #     next will be the spell casting phase, which consumes arcana, and then the enemy turn


if __name__ == "__main__":
    starter_runestones = [runes.Runestone.create_runestone("base"),
                          runes.Runestone.create_runestone("coin")]

    starter_runestones[0].add_runes("isaz")
    print(starter_runestones[0])

    player = runes.Player([], [], 2, 0)
    world = runes.WorldState(player, None)

    battle(world, runes.Enemy("chicken", 10))
