# imports
import runes
import some_functions_copy
import random, time, sys

class Enemy:
    def __init__(self, name):
        self.name = name

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
        enemy: Enemy
):
    print(f"An enemy approaches: a mighty {enemy.name}")
    print("they draw their runestones")
    print("so do you")

    # selection phase for the turn. In this part, the player chooses which of their runestones they will use
    player_arcana = 0

    runestone_choices = choose_runes(user_runestones, user_runestone_capacity)

    while True:
        runestone_confirmation = some_functions_copy.get_confirmation()

        if runestone_confirmation:
            print("runestones selected")
            break

        else:
            print("All right. Choose again")
            runestone_choices = choose_runes(user_runestones, user_runestone_capacity)

    print("you draw your runestones from your bag... which would you like to throw first? Press ? for more info, "
          "and type 'end' to end your throw phase")

    for runestone, i in zip(runestone_choices, range(len(runestone_choices))):
        if runestone.nickname:
            print(f"{i + 1}. {runestone.nickname}")
        else:
            print(f"{i + 1}. {runestone}")

    # choose the stones to throw(in order)
    for i in range(len(runestone_choices)):
        throw_rune_choice = True
        while throw_rune_choice:
            user_input = some_functions_copy.get_numbers_from_input(
                "", 1, len(runestone_choices), False, 1, ["?", "end"]
            )[0]

            # explains
            if user_input == "?":
                runes.runestone_explain(user_runestones)

            # ends turn early
            elif user_input == "end":
                confirm = some_functions_copy.get_confirmation()
                if confirm:
                    break

            else:
                thrown_rune = runestone_choices[user_input - 1]
                arcana, player_attack = thrown_rune.throw(player_arcana, enemy.name)
                throw_rune_choice = False

#     next will be the spell casting phase, which consumes arcana, and then the enemy turn


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
        Enemy("chicken"),
    )
