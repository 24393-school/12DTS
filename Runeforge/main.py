# imports
import random
import sys
import time

# text colouring module
from rich import print
from rich.console import Console
from rich.text import Text

# my files
import input_processing
import runes

# this is for rich, as prints now need to go through it, which is why I'm defining it right up here. the highligh kwarg means that it won't bold numbers or other system stuff
CONSOLE = Console(highlight=False)


# simple base function for readability. sleep, then print
def slprint(string):
    time.sleep(0.25)
    CONSOLE.print(string)


# prints the rewards  for the player to pick from after a battle.
def get_rewards(world_state: runes.WorldState, reward_list: list):

    slprint("Choose your reward. Enter 'skip' to skip the reward")

    # loops over the list to print the info of the reward options
    for i, reward in enumerate(reward_list, 1):
        slprint(
            Text.assemble(
                f"{i}. ",
                reward.info
                if not isinstance(reward, int)
                else "Increase the number of runes you can throw per turn\n",
            )
        )

    # input for the reward
    reward_choice = input_processing.get_numbers_from_input(
        minimum=1, maximum=len(reward_list), choice_amount=1, exceptions=["skip"]
    )[0]

    if reward_choice != "skip":
        reward_choice = reward_list[int(reward_choice) - 1]

        # if they chose a runestone, print its info/nickname
        if isinstance(reward_choice, runes.Runestone):
            slprint(Text.assemble("You chose ", reward_choice.info))

            if input_processing.get_confirmation(
                "would you like to give it a nickname for ease of use?"
            ):
                reward_choice.give_nickname()

            slprint(
                Text.assemble(
                    "Great! ",
                    reward_choice.nickname or reward_choice.info,
                    " added to your bag",
                )
            )

            world_state.player.runestone_bag.append(reward_choice)

            # prints the player's bag
            slprint("these are your runes")
            slprint(world_state.player.runestone_bag.explain())

        elif issubclass(type(reward_choice), runes.Rune):
            engrave_options = runes.RunestoneBag(
                [runestone for runestone in player.runestone_bag if not runestone.full]
            )

            # asks for which runestone to put the rune onto
            slprint(
                "Which runestone would you like to inscribe this rune onto? Enter 'skip' to skip this"
            )
            slprint(engrave_options.explain(rune_info=False))

            engrave_choice = input_processing.get_numbers_from_input(
                minimum=1,
                maximum=len(engrave_options),
                choice_amount=1,
                exceptions=["skip"],
            )[0]

            if engrave_choice != "skip":
                engrave_choice = engrave_options[int(engrave_choice) - 1]

                slprint(
                    Text.assemble(
                        "You engrave ",
                        Text(reward_choice.name, reward_choice.colour),
                        " onto your ",
                        engrave_choice.nickname or engrave_choice.info,
                    )
                )

                # actually adds it
                engrave_choice.add_runes([reward_choice])

            else:
                slprint("you decide not to engrave the rune")

        # if its a spell, it just gives it to you
        elif issubclass(type(reward_choice), runes.Spell):
            slprint(
                Text.assemble(
                    "You learn the spell ",
                    Text(reward_choice.name, reward_choice.colour or "purple"),
                )
            )

            world_state.player.spells.append(reward_choice)

        # the 1 int flag just means runestone cap (i will propbably change this later)
        elif isinstance(reward_choice, int):
            slprint("You increase your runestone capacity!")
            world_state.player.runestone_capacity += 1


# battle function for fighting enemies.
def battle(world_state: runes.WorldState, enemy: runes.Enemy, rewards: list):
    world_state.current_enemy = enemy

    slprint(f"An enemy approaches: a {world_state.current_enemy.name}")
    slprint("you draw your runestones")

    # inits loop values
    battle_ongoing = True
    battle_end = ""

    # resets temp values that need reseting before combat
    world_state.player.temp_runestone_cap = 0

    # to count how many rounds
    turn = 0

    while battle_ongoing:
        turn += 1

        slprint(f"\n---turn {turn}---\n")
        time.sleep(1)

        # resets all temporary stat modifications that last for one turn
        world_state.current_enemy.temp_accuracy_mod = 0
        world_state.player.temp_arcana_income = 0

        for runestone in world_state.player.runestone_bag:
            runestone.colour_mask = None

        world_state.player.arcana = 0

        # resets what runes have been thrown
        world_state.thrown_runes = []

        # prints hp info
        slprint(f"you have [green]{world_state.player.current_hp} hp[/green] left\n")
        slprint(
            f"The {world_state.current_enemy.name} has [red]{world_state.current_enemy.current_hp} hp[/red] left\n"
        )

        # prints what the enemy will do
        slprint(
            f"The {world_state.current_enemy.name} is {world_state.current_enemy.action_foresight}\n"
        )

        # choose the stones to throw, one by one (in order)
        end_turn = False

        # loops a number of times equal to the lower of your runestone cap, or your number of runestone
        for i in range(
            min(
                world_state.player.runestone_capacity
                + world_state.player.temp_runestone_cap,
                len(world_state.player.runestone_bag),
            )
        ):
            slprint(
                f"you draw your runestones from your bag... which would you like to throw {'next' if i != 0 else 'first'}? You can throw up to {world_state.player.runestone_capacity + world_state.player.temp_runestone_cap - i} more this turn. Press ? for more info,"
                "and type 'end' to end your throw phase\n"
            )

            # lists the runes
            for i, runestone in enumerate(world_state.player.runestone_bag):
                if runestone.nickname:
                    slprint(Text.assemble(f"{i + 1}. ", runestone.nickname))
                else:
                    slprint(Text.assemble(f"{i + 1}. ", runestone.info))

            throw_rune_chosen = False

            # loops to get input about which runestone to throw
            while not throw_rune_chosen:
                user_input = input_processing.get_numbers_from_input(
                    "", 1, len(world_state.player.runestone_bag), False, 1, ["?", "end"]
                )[0]

                # explains the runestones
                if str(user_input).lower() == "?":
                    slprint(world_state.player.runestone_bag.explain())

                # ends turn early
                elif str(user_input).lower() == "end":
                    confirm = input_processing.get_confirmation()
                    if confirm:
                        slprint("You decide to end your turn")
                        throw_rune_chosen = True
                        end_turn = True

                # otherwise, throws the rune
                else:
                    thrown_runestone = world_state.player.runestone_bag[
                        int(user_input) - 1
                    ]

                    # adds it onto the thrown runestone list (for use by runes and spells etc)
                    world_state.thrown_runestones.append(thrown_runestone)
                    world_state.player.runestone_bag.remove(thrown_runestone)

                    thrown_runestone.throw(world_state)

                    time.sleep(0.5)
                    print("")

                    throw_rune_chosen = True

            # gets out of the for loop if end has been selected
            if end_turn:
                break

            # breaks if the enemy or player has been killed
            if (
                world_state.current_enemy.current_hp <= 0
                or world_state.player.current_hp <= 0
            ):
                break

        # resets the runestone throwing modifier (as it is only applied by the enemy currently). I will change these things into a special Status effect class in the future
        world_state.player.temp_runestone_cap = 0

        # if the enemy or player hasn't died, progress the fight, otherwise, end it
        if (
            world_state.current_enemy.current_hp <= 0
            or world_state.player.current_hp <= 0
        ):
            battle_ongoing = False

            battle_end = "loss" if world_state.player.current_hp <= 0 else "win"

        # spell casting phase
        else:
            slprint("\n---spell casting phase---\n")
            time.sleep(1)
            spell_choice = None  # this is to ensure it is bound
            spell_cast = True

            # this checks in case the player cannot cast any spells
            for spell in world_state.player.spells:
                if world_state.player.arcana >= spell.arcana_cost:
                    spell_cast = False

            # if they can't, it skips the next bit
            if spell_cast:
                slprint(
                    "you do not have enough [purple]ARCANA[/purple] to cast any of your spells\n"
                )

            while not spell_cast:
                spell_chosen = False

                # loops to get a spell choice
                while not spell_chosen:
                    slprint(
                        f"You have [purple]{world_state.player.arcana} ARCANA[/purple]. Choose a spell to cast. Enter ? for more detail, and type 'end' to skip"
                    )

                    # prints the spells
                    for i, spell in enumerate(world_state.player.spells):
                        slprint(
                            f"{i + 1}. [{spell.colour or 'purple'}]{spell.name}[/{spell.colour or 'purple'}], costing [purple]{spell.arcana_cost} ARCANA[/purple]. {f'Can be empowered for [purple]{spell.empower_cost} aditional ARCANA[/purple]' if spell.empower_cost else ''}"
                        )

                    # gets input
                    spell_choice = input_processing.get_numbers_from_input(
                        "",
                        1,
                        len(world_state.player.spells) + 1,
                        False,
                        1,
                        ["?", "end"],
                    )[0]

                    # eplains the spells
                    if spell_choice == "?":
                        slprint(world_state.player.spells.explain())

                    # breaks the loop if player chooses to end
                    elif spell_choice == "end":
                        spell_choice = None
                        spell_chosen = True

                    else:
                        spell_choice = world_state.player.spells[
                            int(spell_choice) - 1
                        ]  # the int is in there to prevent unneeded error flags
                        spell_chosen = True

                # casts the spell. The isinstance is there to prevent error flags
                if isinstance(spell_choice, runes.Spell):
                    if world_state.player.arcana >= spell_choice.arcana_cost:
                        slprint(
                            f"you raise your hands to the sky as [purple]ARCANA[/purple] flows around you.\nYou reach out and weave the strings into [{spell_choice.colour or 'purple'}]{spell_choice.name}[/{spell_choice.colour or 'purple'}]"
                        )
                        spell_choice.cast(world_state)
                        spell_cast = True

                    # if they don't have enough arcana, they must choose again (or choose to end)
                    else:
                        slprint(
                            f"you do not have enough [purple]ARCANA[/purple] to cast {spell_choice.name}"
                        )
                        slprint("please choose again")

                # triggered on end
                else:
                    slprint("you decide not to cast a spell")
                    spell_cast = True

            # puts the thrown runes back into the player's bag
            for runestone in world_state.thrown_runestones:
                world_state.player.runestone_bag.append(runestone)

            world_state.thrown_runestones = runes.RunestoneBag([])

            # sets the win declaration if anyone has died
            if world_state.current_enemy.current_hp <= 0:
                battle_ongoing = False
                world_state.current_enemy.current_hp = 0
                battle_end = "win"

            elif world_state.player.current_hp <= 0:
                battle_ongoing = False
                world_state.player.current_hp = 0
                battle_end = "loss"

            else:
                # enemy turn

                slprint("\n---enemy turn---\n")
                time.sleep(1)

                world_state.current_enemy.take_turn(world_state)

                if world_state.player.current_hp <= 0:
                    world_state.player.current_hp = 0
                    battle_ongoing = False
                    battle_end = "loss"

    # resets the thor wrath buff at the end of the fight
    world_state.player.thor_wrath = 0

    # resets ay lingering thrown runes to the baf
    for runestone in world_state.thrown_runestones:
        world_state.player.runestone_bag.append(runestone)

    # and any lingering masks on runes
    for runestone in world_state.player.runestone_bag:
        runestone.colour_mask = None

    # returns values on battle end bass on win or loss
    if battle_end == "loss":
        slprint(
            "[bold red]you have been slain...[/bold red] \n"
            "Your journey is over... better luck next time"
        )
        return "loss"

    elif battle_end == "win":
        slprint("[bold green]You are victorious![/bold green]")
        slprint("Now, it is time for you to choose a [bold gold1]reward[/bold gold1]")
        get_rewards(world_state, rewards)

        return "win"


# randomly generates an encounter. will probably move this to being a method of Encounter at some point
def create_encounter(
    world_state: runes.WorldState,
    set_encounter: str | None = None,  # this is if we want a guaranteed encounter type
):

    # if we we'rent guaranteed one, make it random. For now, there are only battles and elite battles, but more could be added, like rests or free tresure etc
    if not set_encounter:
        encounter_type = random.choices(["battle", "elite"])[0]

    else:
        encounter_type = set_encounter

    if encounter_type == "battle" or "elite":
        enemy = random.choice(
            runes.NORMAL_ENEMIES if encounter_type == "battle" else runes.ELITE_ENEMIES
        )(
            attack_mod=random.randint(0, 10), hp_mod=random.randint(0, 10)
        )  # chooses either an enemy or elite enemy from the lists (there are not many currently, but more can be added)

        reward_list = []
        REWARD_TYPES = [
            "rune",
            "runestone",
            "spell",
            "runestone capacity",
        ]  # all of the different reward types

        # there will always be one rune, unless all of the player's runestones are full
        if not world_state.player.all_runes_full:
            reward_list.append(random.choice(runes.NORMAL_RUNES)(None))

        # creates more random rewards to choose from, based on encounter difficulty
        for i in range(
            (2 if encounter_type == "battle" else 4)
            + (
                1 if world_state.player.all_runes_full else 0
            )  # this is for if we didn't generate a rune at the start, so we need to swap it for another random reward
        ):
            # this list comprehension gets the types of rewards which can actually benefit the player. So no duplicate spells, or runes when full etc
            # it has to be regenrated each time as it depends on the state of the reward list (which in turn depends on the rewards that this help generates), so it needs to check it again each time
            available_rewards = [
                rt
                for rt in REWARD_TYPES
                if not (
                    (
                        rt == "rune" and world_state.player.all_runes_full
                    )  # won't generate runes if the player has no space
                    or (
                        rt == "runestone capacity" and 1 in reward_list
                    )  # won't generate runes rune cap if it already has
                    or (
                        rt == "spell"
                        and set(runes.NORMAL_SPELLS)
                        <= set(
                            [
                                type(spell)
                                for spell in world_state.player.spells
                                + reward_list  # won't generate spells if the player has them all (or the remaining ones are already in the list)
                            ]
                        )
                    )
                )
            ]

            # makes the random choice
            reward_type = random.choice(available_rewards)

            # if its a rune, choose a random rune
            if reward_type == "rune":
                reward_list.append(
                    random.choice(
                        [
                            rune
                            for rune in runes.NORMAL_RUNES
                            if rune not in [type(r) for r in reward_list]
                        ]  # this list will contain runes that are not in the reward list
                    )(None)  # and creates an instance of the rune
                )

            elif reward_type == "runestone":
                reward_list.append(
                    runes.Runestone.generate_random_runestone()
                )  # makes a random runestone

            elif reward_type == "spell":
                reward_list.append(
                    random.choice(
                        [
                            spell
                            for spell in runes.NORMAL_SPELLS
                            if spell
                            not in (
                                [
                                    type(spell)
                                    for spell in world_state.player.spells + reward_list
                                ]
                            )
                        ]  # this list will contain spells that the player does not have, and is not in the reward list
                    )()  # creates an instance of it
                )

            elif reward_type == "runestone capacity":
                reward_list.append(
                    1
                )  # this '1' flag just means a runestone cap upgrade. I will probably change it later

        return runes.Battle(
            enemy, reward_list, "normal" if encounter_type == "battle" else "elite"
        )  # returns a battle

    # fall through, just makes a blank encounter
    return runes.Encounter()


# simple function to initialise the player's gear
def make_starter_kit(world: runes.WorldState):
    starter_runestones = runes.RunestoneBag(
        [
            runes.Runestone.create_runestone("base"),
            runes.Runestone.create_runestone("coin"),
        ]
    )

    # initailize the aded runes of the player's starting runestones
    starter_runestones[0].add_runes([runes.AscRune, runes.AscRune])
    starter_runestones[1].add_runes([runes.FehuRune])

    slprint("these are your starting runestones")
    slprint(starter_runestones.explain())

    if input_processing.get_confirmation(
        "\nwould you like to name them for easy reference?"
    ):
        for rune in starter_runestones:
            rune.give_nickname()

    starter_spells = runes.SpellBook([runes.ArcaneBolt()])
    world.player.runestone_bag = starter_runestones
    world.player.spells = starter_spells


if __name__ == "__main__":
    CONSOLE.print(open("Actual Intro text.txt").read(), justify="center")

    # this input just starts the game, so I don't care what is put in
    input()

    # init player and world
    player = runes.Player(runes.RunestoneBag([]), runes.SpellBook([]), 2, 0, 100)
    world = runes.WorldState(player, runes.Enemy("blank", 1, 1))
    make_starter_kit(world)

    slprint("\nthese are your spells:")
    slprint(player.spells.explain())
    time.sleep(0.5)

    slprint("\nthese are your runes:")
    slprint(player.runestone_bag.explain())
    time.sleep(0.5)

    win_count = 0

    # main loop
    game_running = True
    while game_running:
        # creates one elit eencounter, and one normal encounter to choose from
        encounter_choices = [
            create_encounter(world, "battle"),
            create_encounter(world, "elite"),
        ]

        # gets input for which encounter to do
        slprint("choose an encounter:")
        for i, encounter in enumerate(encounter_choices, 1):
            slprint(f"{i}. {encounter.info}")
        encounter_choice = encounter_choices[
            int(
                input_processing.get_numbers_from_input(
                    minimum=1, maximum=2, choice_amount=1
                )[0]
            )
            - 1
        ]

        # this starts a battle if the encounter is a battle
        if isinstance(encounter_choice, runes.Battle):
            combat_result = battle(
                world, encounter_choice.enemy, encounter_choice.rewards
            )

            if combat_result == "win":
                win_count += 1

            # outro if the player dies
            if combat_result == "loss":
                slprint("these were your runestones")
                world.player.runestone_bag.explain()
                slprint("these were your spells")
                world.player.spells.explain()
                slprint(f"You killed [red]{win_count} enemies[/red]")
                slprint("[red]SEE")
                time.sleep(0.5)
                slprint("[red]YOU")
                time.sleep(0.5)
                slprint("[red]NEXT")
                time.sleep(0.5)
                slprint("[red]TIME")
                time.sleep(0.5)
                sys.exit()
