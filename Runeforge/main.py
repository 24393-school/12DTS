# imports
import random
import sys
import time

import runes
import some_functions_copy


# For use later to hold the player's stuff
class Player:
    def __init__(self, runestone_bag: list = [runes.Runestone]) -> None:
        self.runestone_bag = runestone_bag


# function for choosing some runes to use from a list
def choose_runes(user_runestones, user_runestone_capacity):
    print(
        f"Choose up to {user_runestone_capacity} runestones from your bag. Enter ? for more detail:"
        # ? here gives the full description
    )
    for runestone, i in zip(user_runestones, range(len(user_runestones))):
        if runestone.nickname:
            print(f"{i + 1}. {runestone.nickname}")
        else:
            print(f"r{i + 1}. {runestone}")

    user_input = some_functions_copy.get_numbers_from_input(
        "", 1, len(user_runestones), False, user_runestone_capacity, "?"
    )

    if user_input == "?":
        runes.runestone_explain(user_runestones)

    else:
        runestone_choices = [user_runestones[i - 1] for i in user_input]
        print("you have chosen:")
        for rune in runestone_choices:
            print(rune.nickname)

        return runestone_choices


# battle function for fighting enemies. takes enemy and player data. Will Class player and enemy later
def battle(
    user_runestones: list[runes.Runestone],
    user_runestone_capacity: int,
    enemy_runestones: list[runes.Runestone],
    enemy_name: str,
):
    print(f"An enemy approaches: a mighty {enemy_name}")
    print("they draw their runestones")
    print("so do you")

    # selection phase for the turn. In this part, the player chooses which of their runestones they will use
    arcana = 0
    runestone_choices = choose_runes(user_runestones, user_runestone_capacity)

    while True:
        runestone_confirmation = input("is this your choice? - y/n ")

        if runestone_confirmation == ("y" or "yes"):
            print("runestones selected")
            break

        elif runestone_confirmation == ("n" or "no"):
            print("All right. Choose again")
            runestone_choices = choose_runes(user_runestones, user_runestone_capacity)

        else:
            print("that is not a yes or a no!")

    print(
        "you draw your runestones from your bag... which would you like to throw first?"
    )

    for runestone, i in zip(runestone_choices, range(len(runestone_choices))):
        if runestone.nickname:
            print(f"{i + 1}. {runestone.nickname}")
        else:
            print(f"{i + 1}. {runestone}")

    while True:
        user_input = some_functions_copy.get_numbers_from_input(
            "", 1, len(runestone_choices), False, 1, "?"
        )[0]

        if user_input == "?":
            runes.runestone_explain(user_runestones)
        else:
            thrown_rune = runestone_choices[user_input - 1]
            thrown_rune.throw(0)
            break


if __name__ == "__main__":
    battle(
        [
            runes.Runestone(
                "metal",
                3,
                [runes.Rune.create_rune("isaz"), runes.Rune.create_rune("isaz")],
            ),
            runes.Runestone.create_runestone(
                "base",
                [runes.Rune.create_rune("sōwulō"), runes.Rune.create_rune("sōwulō")],
            ),
        ],
        2,
        [],
        "chicken",
    )
