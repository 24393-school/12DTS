# imports
import random
import sys
import time
from profile import run

import input_processing
import runes

COLOURS = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "PURPLE": "\033[95m",
    "RESET": "\033[0m",
}


# function for choosing some runes to use from a list
def choose_runes(world_state: runes.WorldState):
    print(
        f"Choose up to {world_state.player.runestone_capacity} runestones from your bag. Enter ? for more detail:"
        # ? here gives the full description
    )
    for runestone, i in zip(
        world_state.player.runestone_bag, range(len(world_state.player.runestone_bag))
    ):
        if runestone.nickname:
            print(f"{i + 1}. {runestone.nickname}")
        else:
            print(f"{i + 1}. {runestone}")

    user_input = input_processing.get_numbers_from_input(
        "",
        1,
        len(world_state.player.runestone_bag),
        False,
        world_state.player.runestone_capacity,
        ["?"],
    )

    if user_input == "?":
        print(world_state.player.runestone_bag.explain())

    else:
        runestone_choices = [
            world_state.player.runestone_bag[int(i) - 1] for i in user_input
        ]
        print("you have chosen:")
        for rune in runestone_choices:
            print(rune)

        return runestone_choices


# battle function for fighting enemies. takes enemy and player data.
def battle(world_state: runes.WorldState):
    print(f"An enemy approaches: a mighty {world_state.current_enemy.name}")
    time.sleep(0.5)
    print("they draw their runestones")
    time.sleep(0.5)
    print("so do you")
    time.sleep(0.5)

    # selection phase for the turn. In this part, the player chooses which of their runestones they will use

    runestone_choices: list[runes.Runestone] | None = choose_runes(world_state)

    while True:
        runestone_confirmation = input_processing.get_confirmation()

        if runestone_confirmation:
            print("runestones selected")
            break

        else:
            print("All right. Choose again")
            runestone_choices = choose_runes(world_state)

    # choose the stones to throw (in order)
    if runestone_choices:
        for i in range(len(runestone_choices)):
            print(
                f"you draw your runestones from your bag... which would you like to throw {'next' if i != 0 else 'first'}? Press ? for more info,"
                "and type 'end' to end your throw phase"
            )

            for i, runestone in enumerate(runestone_choices):
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
                    print(world_state.player.runestone_bag.explain())

                # ends turn early
                elif user_input == "end":
                    confirm = input_processing.get_confirmation()
                    if confirm:
                        break

                else:
                    thrown_rune = runestone_choices[int(user_input) - 1]
                    thrown_rune.throw(world_state)
                    throw_rune_choice = False
                    runestone_choices.pop(runestone_choices.index(thrown_rune))
                    world_state.current_enemy.current_hp -= player.current_attack

    # spell casting phase
    spell_choice = None  # this is to ensure it is bound
    spell_chosen = False
    while not spell_chosen:
        print(
            f"You have {COLOURS['PURPLE']}{player.arcana} ARCANA{COLOURS['RESET']}. Choose a spell to cast. Enter ? for more detail, and type 'end' to skip"
        )

        for i, spell in enumerate(player.spells):
            print(
                f"{i + 1}. {spell.name}, costing {COLOURS['PURPLE']}{spell.arcana_cost}{COLOURS['RESET']}"
            )

        spell_choice = input_processing.get_numbers_from_input(
            "", 1, len(player.spells) + 1, False, 1, ["?", "end"]
        )[0]

        if spell_choice == "?":
            print(player.spells.explain)

        elif spell_choice == "end":
            spell_choice = None
            spell_chosen = True

        else:
            spell_choice = player.spells[
                int(spell_choice) - 1
            ]  # the int is in there to prevent unneeded error flags
            spell_chosen = True

    if isinstance(spell_choice, runes.Spell):
        print(
            f"you raise your hands to the sky as {COLOURS['PURPLE']}ARCANA{COLOURS['RESET']} flows around you. \n You cast {spell_choice.name}"
        )
        spell_choice.cast(world_state)

    else:
        print("you decide not to cast a spell")


def make_starter_kit(world: runes.WorldState):
    starter_runestones = runes.RunestoneBag(
        [
            runes.Runestone.create_runestone("base"),
            runes.Runestone.create_runestone("coin"),
        ]
    )
    starter_runestones[0].add_runes([runes.IsazRune, runes.IsazRune])
    starter_runestones[1].add_runes([runes.SowuloRune])

    print("these are your staring runestones")
    print(starter_runestones.explain())
    time.sleep(0.5)

    if input_processing.get_confirmation(
        "would you like to name your runes for easy reference?"
    ):
        for rune in starter_runestones:
            rune.give_nickname()

    starter_spells = runes.SpellBook([runes.ArcaneBolt()])
    world.player.runestone_bag = starter_runestones
    world.player.spells = starter_spells


if __name__ == "__main__":
    player = runes.Player(runes.RunestoneBag([]), runes.SpellBook([]), 2, 0)
    world = runes.WorldState(player, runes.Enemy("chicken", 10))
    make_starter_kit(world)

    ## print(starter_runestones[0])

    print("these are your spells")
    print(player.spells.explain())
    time.sleep(0.5)

    print("these are your runes")
    print(player.runestone_bag.explain())
    time.sleep(0.5)

    battle(world)
