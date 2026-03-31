# imports
import random
import time

from rich import print
from rich.console import Console

# text colouring module
from rich.text import Text

# my modules
import input_processing
import runes

# this is for rich, as prints now need to go through it, which is why I'm defining it right up here
CONSOLE = Console(highlight=False)


# simple bas function for readability. sleep, then print
def slprint(string):
    time.sleep(0.25)
    CONSOLE.print(string)


# generates rewards for the player to pick from after a battle. there will be three, with one always guaranteed to be a new rune
def get_rewards(world_state: runes.WorldState, reward_list: list):

    slprint("Choose your reward. Enter 'skip' to skip the reward")

    for i, reward in enumerate(reward_list, 1):
        slprint(
            Text.assemble(
                f"{i}. ",
                reward.info
                if not isinstance(reward, int)
                else "Increase the number of runes you can throw per turn",
            )
        )

    reward_choice = input_processing.get_numbers_from_input(
        minimum=1, maximum=len(reward_list), choice_amount=1, exceptions=["skip"]
    )[0]

    if reward_choice != "skip":
        reward_choice = reward_list[int(reward_choice) - 1]

        if isinstance(reward_choice, runes.Runestone):
            slprint(Text.assemble("You chose", reward_choice.info))

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
            slprint(world_state.player.runestone_bag.explain())

        elif issubclass(type(reward_choice), runes.Rune):
            slprint(
                "Which runestone would you like to inscribe this rune onto? Enter 'skip' to skip this"
            )

            slprint(world_state.player.runestone_bag.explain())

            engrave_choice = input_processing.get_numbers_from_input(
                minimum=1,
                maximum=len(world_state.player.runestone_bag),
                choice_amount=1,
                exceptions=["skip"],
            )[0]

            if engrave_choice != "skip":
                engrave_choice = world_state.player.runestone_bag[
                    int(engrave_choice) - 1
                ]

                slprint(
                    Text.assemble(
                        "You engrave ",
                        Text(reward_choice.name, reward_choice.colour),
                        " onto your ",
                        engrave_choice.nickname or engrave_choice.info,
                    )
                )

                engrave_choice.add_runes([reward_choice])

            else:
                slprint("you decide not to engrave the rune")

        elif issubclass(type(reward_choice), runes.Spell):
            slprint(
                Text.assemble(
                    "You learn the spell ",
                    Text(reward_choice.name, reward_choice.colour or "purple"),
                )
            )

            world_state.player.spells.append(reward_choice)

        elif isinstance(reward_choice, int):
            slprint("You increase your runestone capacity!")
            world_state.player.runestone_capacity += 1


# battle function for fighting enemies.
def battle(world_state: runes.WorldState, enemy: runes.Enemy, rewards: list):
    world_state.current_enemy = enemy

    slprint(f"An enemy approaches: a {world_state.current_enemy.name}")
    slprint("they draw their runestones")
    slprint("so do you\n")

    battle_ongoing = True
    battle_end = ""

    world_state.player.temp_runestone_cap = 0

    # to count how many rounds
    turn = 0

    while battle_ongoing:
        turn += 1

        slprint(f"\n---turn {turn}---\n")
        time.sleep(1)

        # resets all temporary stat modifications
        world_state.player.arcana = 0
        world_state.thrown_runestones = runes.RunestoneBag([])
        world_state.thrown_runes = []
        world_state.current_enemy.temp_accuracy_mod = 0
        world_state.player.temp_arcana_income = 0

        for runestone in world_state.player.runestone_bag:
            runestone.mask = None

        slprint(f"you have [green]{world_state.player.current_hp} hp[/green] left\n")

        # prints what the enemy will do
        slprint(
            f"The {world_state.current_enemy.name} is {world_state.current_enemy.action_foresight}\n"
        )

        # selection phase for the turn. In this part, the player chooses which of their runestones they will use

        # the type declaration prevents error flags

        # loops to get confirmation
        runestone_choices = world_state.player.runestone_bag
        # choose the stones to throw, one by one (in order)
        if runestone_choices:
            end_turn = False
            for i in range(
                world_state.player.runestone_capacity
                + world_state.player.temp_runestone_cap
            ):
                slprint(
                    f"you draw your runestones from your bag... which would you like to throw {'next' if i != 0 else 'first'}? You can throw up to {world_state.player.runestone_capacity + world_state.player.temp_runestone_cap - i} more this turn. Press ? for more info,"
                    "and type 'end' to end your throw phase\n"
                )

                # lists the runes
                for i, runestone in enumerate(runestone_choices):
                    if runestone.nickname:
                        slprint(Text.assemble(f"{i + 1}. ", runestone.nickname))
                    else:
                        slprint(Text.assemble(f"{i + 1}. ", runestone.info))

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
                            slprint("You decide to end your turn")
                            throw_rune_chosen = True
                            end_turn = True

                    # otherwise, throws the rune
                    else:
                        thrown_runestone = runestone_choices[int(user_input) - 1]
                        thrown_runestone.throw(world_state)

                        time.sleep(0.5)
                        print("")

                        world_state.thrown_runestones.append(thrown_runestone)
                        runestone_choices.remove(thrown_runestone)

                        throw_rune_chosen = True

                # gets out of the for loop if end has been selected
                if end_turn:
                    break

                if (
                    world_state.current_enemy.current_hp <= 0
                    or world_state.player.current_hp <= 0
                ):  # breaks if the enemy or player has been killed
                    break

        # resets the runestone throwing mod (as it is only applied by the enemy currently). I will change these things into a special Status effect class in the future
        world_state.player.temp_runestone_cap = 0

        # spell casting phase
        if (
            world_state.current_enemy.current_hp <= 0
            or world_state.player.current_hp <= 0
        ):
            battle_ongoing = False
            world_state.current_enemy.current_hp, world_state.player.current_hp = 0, 0

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

                    if spell_choice == "?":
                        slprint(world_state.player.spells.explain)

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
                            "you do not have enough [purple]ARCANA[/purple] to cast {spell_choice.name}"
                        )
                        slprint("please choose again")

                else:
                    slprint("you decide not to cast a spell")
                    spell_cast = True

            if world_state.current_enemy.current_hp <= 0:
                battle_ongoing = False
                world_state.current_enemy.current_hp = 0
                battle_end = "win"

            else:
                # enemy turn

                slprint("\n---enemy turn---\n")
                time.sleep(1)

                world_state.current_enemy.take_turn(world_state)

                if world_state.player.current_hp <= 0:
                    world_state.player.current_hp = 0
                    battle_ongoing = False
                    battle_end = "loss"

            for runestone in world_state.thrown_runestones:
                world_state.player.runestone_bag.append(runestone)

    world_state.player.thor_wrath = 0

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


def create_encounter(world_state: runes.WorldState):

    encounter_type = random.choices(
        ["battle", "elite"]
    )[
        0
    ]  # this will be in case I want to add other types of encounters, like rests or free tresure etc

    if encounter_type == "battle" or "elite":
        enemy = random.choice(
            runes.NORMAL_ENEMIES if encounter_type == "battle" else runes.ELITE_ENEMIES
        )(attack_mod=random.randint(0, 10), hp_mod=random.randint(0, 10))

        reward_list = []
        reward_types = ["rune", "runestone", "spell", "runestone capacity"]

        # the rune
        reward_list.append(random.choice(runes.NORMAL_RUNES)(None))

        for i in range(2 if encounter_type == "battle" else 4):
            reward_type = random.choice(
                [
                    reward
                    for reward in reward_types
                    if not (
                        (reward == "rune" and world_state.player.all_runes_full)
                        or (
                            reward == "runestone capacity"
                            and "runestone capacity" in reward_list
                        )
                    )
                ]
            )

            if reward_type == "rune":
                reward_list.append(random.choice(runes.NORMAL_RUNES)(None))

            elif reward_type == "runestone":
                reward_list.append(runes.Runestone.generate_random_runestone())

            elif reward_type == "spell":
                reward_list.append(
                    random.choice(
                        [
                            spell
                            for spell in runes.NORMAL_SPELLS
                            if spell
                            not in (
                                [type(spell) for spell in world_state.player.spells]
                                or [type(spell) for spell in reward_list]
                            )
                        ]
                    )()
                )

            elif reward_type == "runestone capacity":
                reward_list.append(1)

        return runes.Battle(
            enemy, reward_list, "normal" if encounter_type == "battle" else "elite"
        )

    return runes.Encounter()


# simple function to initialise the player's gear
def make_starter_kit(world: runes.WorldState):
    starter_runestones = runes.RunestoneBag(
        [
            runes.Runestone.create_runestone("base"),
            runes.Runestone.create_runestone("coin"),
        ]
    )
    starter_runestones[0].add_runes([runes.AscRune, runes.AscRune])
    starter_runestones[1].add_runes([runes.FehuRune])

    slprint("these are your starting runestones")
    slprint(starter_runestones.explain())
    time.sleep(0.5)
    slprint("this is what the runes upon those stones do:")
    slprint(starter_runestones[0].runes[0].info)
    slprint(starter_runestones[1].runes[0].info)

    if input_processing.get_confirmation(
        "\nwould you like to name your runestones for easy reference?"
    ):
        for rune in starter_runestones:
            rune.give_nickname()

    starter_spells = runes.SpellBook([runes.ArcaneBolt()])
    world.player.runestone_bag = starter_runestones
    world.player.spells = starter_spells


if __name__ == "__main__":
    slprint(
        "                    [bold yellow]WELCOME, RUNECASTER[/bold yellow]                      \n"
        "\n"
        "In this game, you will be journeying through a [red]dangerous[/red] land,              \n"
        "                with many [red]powerfull foes[/red]                              \n"
        "          To survive, you must use your [purple]RUNESTONES[/purple],                       \n"
        "       each with their sides engraved with [purple]ARCANE RUNES[/purple]                     \n"
        "                                                                        \n"
        "To wield the [purple]magic[/purple] of these runes, you [bold]must[/bold] throw them to the sky,          \n"
        "             letting [green]luck[/green] determine your [red]fate[/red]                             \n"
        "                                                                        \n"
        "          Then, weilding the [purple]ARCANA[/purple] from you runes,                       \n"
        "you must weave it into [purple]spells of power[/purple] to bypass your [red]foes[/red]             \n"
        "                                                                        \n"
        "This game is fully [bright_white]text-based[/bright_white], and when asked for input to choose anything,     \n"
        "enter either enter y/n, or the number that came before the item (where apropriate)   \n"
        "                                                                        \n"
        "[bold red]NEVER[/bold red] enter any input when not asked for it (it can screw with the terminal)      \n"
        "                                                                        \n"
        "                                                                            \n"
        "          [bold green]May Njordnir's luck be with you[/bold green]                               \n"
        "                                                                        \n"
        "                                                                        \n"
        "                  [bold red]YOU'LL NEED IT[/bold red]                            \n"
        "                                                                        \n"
        "                                                                        \n"
        "              press enter to continue                                               \n"
    )

    input()

    player = runes.Player(runes.RunestoneBag([]), runes.SpellBook([]), 2, 0, 100)
    world = runes.WorldState(player, runes.Enemy("blank", 1, 1))
    make_starter_kit(world)

    slprint("\nthese are your spells:")
    slprint(player.spells.explain())
    time.sleep(0.5)

    slprint("\nthese are your runes:")
    slprint(player.runestone_bag.explain())
    time.sleep(0.5)

    game_running = True
    while game_running:
        encounter_choices = [create_encounter(world), create_encounter(world)]

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

        if isinstance(encounter_choice, runes.Battle):
            battle(world, encounter_choice.enemy, encounter_choice.rewards)
