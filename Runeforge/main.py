import runes
import some_functions_copy


# r
# For use later to hold the player's stuff
class Player:
    def __init__(self, runestone_bag: list = [runes.Runestone]) -> None:
        self.runestone_bag = runestone_bag


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
    runestone_choices = []
    while not runestone_choices:
        print(
            f"Choose up to {user_runestone_capacity} runestones from your bag. Enter ? for more detail:"  # ? here gives the full description
        )
        for runestone, i in zip(user_runestones, range(len(user_runestones))):
            if runestone.nickname:
                print(f"{i + 1}. {runestone.nickname}")
            else:
                print(f"r{i + 1}. {runestone}")

        user_input = some_functions_copy.get_numbers_from_input(
            "", 1, len(user_runestones) + 1, False, user_runestone_capacity, "?"
        )

        if user_input == "?":
            for runestone, i in zip(user_runestones, range(len(user_runestones))):
                if runestone.nickname:
                    print(f"{i + 1}. {runestone.nickname}: A {runestone}")
                else:
                    print(f"{i + 1}. A {runestone}")

        else:
            runestone_choices = [user_runestones[i - 1] for i in user_input]
            print("you have chosen:")
            for rune in runestone_choices:
                print(rune.nickname)

            while True:
                runestone_confirmation = input("is this your choice? - y/n ")

                if runestone_confirmation == ("y" or "yes"):
                    print("runestones selected")
                    break

                elif runestone_confirmation == ("n" or "no"):
                    print("All right. Choose again")
                    runestone_choices = []
                    break

                else:
                    print("that is not a yes or a no!")

            p

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
                [runes.Rune.create_rune("isaz"), runes.Rune.create_rune("isaz")],
            ),
        ],
        2,
        [],
        "chicken",
    )
