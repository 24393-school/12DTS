import random
import time

import runes
import some_functions_copy


# battle function for fighting enemies
def battle(
    user_runestones: list[runes.Runestone],
    enemy_runestones: list[runes.Runestone],
    enemy_name: str,
):
    print(f"An enemy approaches: a mighty {enemy_name}")
    print("they draw their runestones")
    print("so do you")

    arcana = 0

    while True:
        print("Choose up to five runestones from your bag. Enter ? for more detail:")
        for runestone, i in zip(user_runestones, range(len(user_runestones))):
            if runestone.nickname:
                print(f"{i + 1}. {runestone.nickname}")
            else:
                print(f"r{i + 1}. {runestone}")

            user_input = some_functions_copy.get_numbers_from_input(
                "", 1, len(user_runestones) + 1, False, 5, "?"
            )


if __name__ == "__main__":
    pass
