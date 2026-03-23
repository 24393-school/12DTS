# imports
import random
import sys
import time

import runes
import input_processing


class Colour:
    RED = "\033[91m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


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
            print(f"{i + 1}. {runestone}")

    user_input = input_processing.get_numbers_from_input(
        "", 1, len(world_state.player.runestone_bag), False, world_state.player.runestone_capacity, "?"
    )

    if user_input == "?":
        runes.runestone_explain(world_state.player.runestone_bag)

    else:
        runestone_choices = [world_state.player.runestone_bag[i - 1] for i in user_input]
        print("you have chosen:")
        for rune in runestone_choices:
            print(rune)

        return runestone_choices


# battle function for fighting enemies. takes enemy and player data.
def battle(world_state: runes.WorldState, enemy: runes.Enemy):
    print(f"An enemy approaches: a mighty {enemy.name}")
    time.sleep(0.5)
    print("they draw their runestones")
    time.sleep(0.5)
    print("so do you")
    time.sleep(0.5)

    # selection phase for the turn. In this part, the player chooses which of their runestones they will use

    runestone_choices = choose_runes(world_state)

    while True:
        runestone_confirmation = input_processing.get_confirmation()

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
            user_input = input_processing.get_numbers_from_input(
                "", 1, len(runestone_choices), False, 1, ["?", "end"]
            )[0]

            # explains
            if user_input == "?":
                runes.runestone_explain(world_state.player.runestone_bag)

            # ends turn early
            elif user_input == "end":
                confirm = input_processing.get_confirmation()
                if confirm:
                    break

            else:
                thrown_rune = runestone_choices[user_input - 1]
                thrown_rune.throw(
                    world_state
                )
                throw_rune_choice = False
                runestone_choices.pop(runestone_choices.index(thrown_rune))
                enemy.current_hp -= player.current_attack

    # spell casting phase
    spell_chosen = False
    while not spell_chosen:
        print(
            f"You have {Colour.BLUE}{player.arcana} ARCANA{Colour.RESET}. Choose a spell to cast. Enter ? for more detail, and type 'end' to skip")

        for spell, i in zip(player.spells, range(len(player.spells))):
            print(f"{i + 1}. {spell.name}")

        spell_choice = input_processing.get_numbers_from_input("", 1, len(player.spells) + 1, False, 1,
                                                               ["?", "end"])[0]

        if spell_choice == "?":
            runes.spell_explain(player.spells)

        elif spell_choice == "end":
            spell_choice = None
            spell_chosen = True

        else:

            spell_choice = player.spells[spell_choice - 1]
            spell_chosen = True

    if spell_choice:
        print(f"you raise your hands to the sky as {Colour.BLUE}ARCANA{Colour.RESET} flows around you. \n You cast {spell_choice.name}")

    else:
        print("you decide not to cast a spell")


def make_starter_kit(world: runes.WorldState):
    starter_runestones = [runes.Runestone.create_runestone("base"),
                          runes.Runestone.create_runestone("coin")]
    starter_runestones[0].add_runes(["isaz", "isaz"])
    starter_runestones[1].add_runes(["sōwulō"])

    print("these are your staring runestones")
    runes.runestone_explain(starter_runestones)
    time.sleep(0.5)

    if input_processing.get_confirmation('would you like to name your runes for easy reference?'):
        for rune in starter_runestones:
            rune.give_nickname()

    starter_spells = [runes.Spell.create_spell("arcane bolt")]
    world.player.runestone_bag = starter_runestones
    world.player.spells = starter_spells


if __name__ == "__main__":
    player = runes.Player([], [], 2, 0)
    world = runes.WorldState(player, None)
    make_starter_kit(world)

    ## print(starter_runestones[0])

    print("these are your spells")
    runes.spell_explain(player.spells)
    time.sleep(0.5)

    print("these are your runes")
    runes.runestone_explain(player.runestone_bag)
    time.sleep(0.5)

    battle(world, runes.Enemy("chicken", 10))
