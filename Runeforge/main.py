# imports
import random
import sys
import time
from profile import run

# text colouring module
from rich import print
from rich.text import Text

# my modules
import input_processing
import runes

# will be removed when I have RIch up and running
COLOURS = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "PURPLE": "\033[95m",
    "RESET": "\033[0m",
}


# sleep, then print
def slprint(string):
    time.sleep(0.5)
    print(string)


# function for choosing some runes to use from a list
def choose_runes(world_state: runes.WorldState):
    runes_chosen = False
    while not runes_chosen:
        slprint(
            f"Choose up to {world_state.player.runestone_capacity} runestones from your bag. Enter ? for more detail:"
            # ? here gives the full description
        )
        for runestone, i in zip(
            world_state.player.runestone_bag,
            range(len(world_state.player.runestone_bag)),
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

        if user_input[0] == "?":
            slprint(world_state.player.runestone_bag.explain())

        else:
            runestone_choices = [
                world_state.player.runestone_bag[int(i) - 1] for i in user_input
            ]
            slprint("you have chosen:")
            for rune in runestone_choices:
                slprint(rune)

            return runestone_choices


# battle function for fighting enemies. 
def battle(world_state: runes.WorldState):
    slprint(f"An enemy approaches: a mighty {world_state.current_enemy.name}")
    slprint("they draw their runestones")
    slprint("so do you\n")

    battle_ongoing = True

    # to count how many rounds
    turn = 0

    while battle_ongoing:
        turn += 1

        print(f"\n---turn {turn}---\n")
        
        # prints what the enemy will do
        slprint(
            f"The mighty {world_state.current_enemy.name} is {world_state.current_enemy.action_foresight}\n"
        )

        # selection phase for the turn. In this part, the player chooses which of their runestones they will use

        runestone_choices: list[runes.Runestone] | None = choose_runes(world_state)     # the type declaration prevents error flags

        # loops to get confirmation
        while True:
            runestone_confirmation = input_processing.get_confirmation()

            if runestone_confirmation:
                slprint("runestones selected")
                break

            else:
                slprint("All right. Choose again")
                runestone_choices = choose_runes(world_state)

        # choose the stones to throw (in order)
        if runestone_choices:
            end_turn = False
            for i in range(len(runestone_choices)):
                slprint(
                    f"you draw your runestones from your bag... which would you like to throw {'next' if i != 0 else 'first'}? Press ? for more info,"
                    "and type 'end' to end your throw phase"
                )
                
                # lists the runes 
                for i, runestone in enumerate(runestone_choices):
                    if runestone.nickname:
                        slprint(f"{i + 1}. {runestone.nickname}")
                    else:
                        slprint(f"{i + 1}. {runestone}")
                
                
                throw_rune_chosen = False
                
                # loops to get input about which runestone to throw
                while not throw_rune_chosen:
                    user_input = input_processing.get_numbers_from_input(
                        "", 1, len(runestone_choices), False, 1, ["?", "end"]
                    )[0]

                    # explains the runestones
                    if user_input == "?":
                        slprint(world_state.player.runestone_bag.explain())

                    # ends turn early
                    elif str(user_input).lower() == "end":
                        confirm = input_processing.get_confirmation()
                        if confirm:
                            print("You decide to end your turn")
                            throw_rune_chosen = True
                            end_turn = True
                        
                    # otherwise, throws the rune
                    else:
                        thrown_rune = runestone_choices[int(user_input) - 1]
                        thrown_rune.throw(world_state)
                        throw_rune_chosen = True
                        runestone_choices.pop(runestone_choices.index(thrown_rune))
                        world_state.current_enemy.current_hp -= (
                            world_state.player.current_attack
                        )
                
                # gets out of the for loop if end has been selected
                if end_turn:
                    break

        # spell casting phase

        slprint("\n ---spell casting phase---\n")
        spell_choice = None  # this is to ensure it is bound
        spell_cast = True

        
        # this checks in case the player cannot cast any spells
        for spell in world_state.player.spells:
            if player.arcana >= spell.arcana_cost:
                spell_cast = False
        
        # if they can't, it skips the next bit
        if spell_cast:
            slprint(
                f"you do not have enough {COLOURS['PURPLE']}ARCANA{COLOURS['RESET']} to cast any of your spells\n"
            )

        while not spell_cast:
            spell_chosen = False
            
            # loops to get a spell choice
            while not spell_chosen:
                slprint(
                    f"You have {COLOURS['PURPLE']}{player.arcana} ARCANA{COLOURS['RESET']}. Choose a spell to cast. Enter ? for more detail, and type 'end' to skip"
                )

                # prints the spells
                for i, spell in enumerate(player.spells):
                    slprint(
                        f"{i + 1}. {spell.name}, costing {COLOURS['PURPLE']}{spell.arcana_cost} ARCANA{COLOURS['RESET']}"
                    )

                # gets input
                spell_choice = input_processing.get_numbers_from_input(
                    "", 1, len(player.spells) + 1, False, 1, ["?", "end"]
                )[0]

                if spell_choice == "?":
                    slprint(player.spells.explain)

                elif spell_choice == "end":
                    spell_choice = None
                    spell_chosen = True

                else:
                    spell_choice = player.spells[
                        int(spell_choice) - 1
                    ]  # the int is in there to prevent unneeded error flags
                    spell_chosen = True

            # casts the spell. The isinstance is there to prevent error flags
            if isinstance(spell_choice, runes.Spell):
                if player.arcana >= spell_choice.arcana_cost:
                    slprint(
                        f"you raise your hands to the sky as {COLOURS['PURPLE']}ARCANA{COLOURS['RESET']} flows around you. \n You cast {spell_choice.name}"
                    )
                    spell_choice.cast(world_state)
                    spell_cast = True

                # if they don't have enough arcana, they must choose again (or choose to end)
                else:
                    slprint(
                        f"you do not have enough {COLOURS['PURPLE']}ARCANA{COLOURS['RESET']} to cast {spell_choice.name}"
                    )
                    slprint("please choose again")

            else:
                slprint("you decide not to cast a spell")
                spell_cast = True

        # enemy turn

        slprint("\n---enemy turn---\n")

        world_state.current_enemy.take_turn(world_state)

# simple function to initialise the player's gear
def make_starter_kit(world: runes.WorldState):
    starter_runestones = runes.RunestoneBag(
        [
            runes.Runestone.create_runestone("base"),
            runes.Runestone.create_runestone("coin"),
        ]
    )
    starter_runestones[0].add_runes([runes.IsazRune, runes.IsazRune])
    starter_runestones[1].add_runes([runes.SowuloRune])

    slprint("these are your staring runestones")
    slprint(starter_runestones.explain())
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
    world = runes.WorldState(player, runes.Chicken())
    make_starter_kit(world)

    ## slprint(starter_runestones[0])

    slprint("\nthese are your spells:")
    slprint(player.spells.explain())
    time.sleep(0.5)

    slprint("\nthese are your runes:")
    slprint(player.runestone_bag.explain())
    time.sleep(0.5)

    battle(world)
