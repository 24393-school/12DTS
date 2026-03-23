# imports
import random
import sys
import time

import runes
import input_processing


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
                arcana, player_attack = thrown_rune.throw(
                    world_state
                )
                throw_rune_choice = False
                runestone_choices.pop(runestone_choices.index(thrown_rune))
                enemy.current_hp -= player_attack

        # spell casting phase
        spell_chosen = False
        while not spell_chosen:
            print(f"You have {arcana} ARCANA. Choose a spell to cast. Enter ? for more detail, and type 'end' to skip")

            for spell, i in zip(player.spells, range(len(player.spells))):
                print(f"{i + 1}. {spell.name}")

            spell_choice = input_processing.get_numbers_from_input("", 1, len(player.spells + 1), False, 1,
                                                                   ["?", "end"])

            if spell_choice == "?":
                runes.spell_explain(player.spells)

            elif spell_choice == "end":
                spell_choice = None
                spell_chosen = True

            else:

                spell_choice = player.spells[spell_choice-1]
                spell_chosen = True

        if spell_choice:
            print(f"you raise your hands to the sky as ARCANA flows around you. \n You cast {spell_choice.name}")

        else:
            print("you decide not to cast a spell")


if __name__ == "__main__":
    starter_runestones = [runes.Runestone.create_runestone("base"),
                          runes.Runestone.create_runestone("coin")]

    starter_runestones[0].add_runes("isaz")
    ## print(starter_runestones[0])

    player = runes.Player(starter_runestones, [runes.Spell.create_spell("arcane bolt")], 2, 0)

    runes.spell_explain(player.spells)
    runes.runestone_explain(player.runestone_bag)

    world = runes.WorldState(player, None)

    battle(world, runes.Enemy("chicken", 10))
