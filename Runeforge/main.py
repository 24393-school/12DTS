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

console = Console(highlight=False)


# simple bas function for readability. sleep, then print
def slprint(string):
    time.sleep(0.5)
    console.print(string)


# function for choosing some runes to use from a list
def choose_runes(world_state: runes.WorldState):
    runes_chosen = False
    while not runes_chosen:
        slprint(
            f"Choose up to {world_state.player.runestone_capacity} runestones from your bag. Enter ? for more detail:\n"
            # ? here gives the full description
        )
        for runestone, i in zip(
            world_state.player.runestone_bag,
            range(len(world_state.player.runestone_bag)),
        ):
            if runestone.nickname:
                console.print(Text.assemble(f"{i + 1}. ", runestone.nickname))
            else:
                console.print(Text.assemble(f"{i + 1}. ", runestone.info))

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
            slprint("you have chosen:\n")
            for rune in runestone_choices:
                slprint(Text.assemble(rune.nickname or rune.info))

            return runestone_choices


# generates rewards for the player to pick from after a battle. there will be three, with one always guaranteed to be a new rune
def get_rewards(world_state: runes.WorldState, reward_list: list):

    slprint("Choose your reward. Enter 'skip' to skip the reward")

    for i, reward in enumerate(reward_list, 1):
        slprint(Text.assemble(f"{i}. ", reward.info))

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
            print(world_state.player.runestone_bag.explain())

        elif issubclass(type(reward_choice), runes.Rune):
            print(
                "Which runestone would you like to inscribe this rune onto? Enter 'skip' to skip this"
            )

            print(world_state.player.runestone_bag.explain())

            engrave_choice = input_processing.get_numbers_from_input(
                minimum=1,
                maximum=len(world_state.player.runestone_bag),
                choice_amount=1,
                exceptions=["skip"],
            )[0]

            if engrave_choice != "skip":
                engrave_choice = player.runestone_bag[int(engrave_choice) - 1]

                print(
                    Text.assemble(
                        "You engrave ",
                        Text(reward_choice.name, reward_choice.colour),
                        " onto your",
                        engrave_choice.nickname or engrave_choice.info,
                    )
                )

                engrave_choice.add_runes([reward_choice])

            else:
                print("you decide not to engrave the rune")

        elif issubclass(type(reward_choice), runes.Spell):
            print(
                Text.assemble(
                    "You learn the spell ",
                    Text(reward_choice.name, reward_choice.colour or "purple"),
                )
            )

            player.spells.append(reward_choice)


# battle function for fighting enemies.
def battle(world_state: runes.WorldState, enemy: runes.Enemy, rewards: list):
    world_state.current_enemy = enemy

    slprint(f"An enemy approaches: a mighty {world_state.current_enemy.name}")
    slprint("they draw their runestones")
    slprint("so do you\n")

    battle_ongoing = True
    battle_end = ""

    # to count how many rounds
    turn = 0

    while battle_ongoing:
        turn += 1

        slprint(f"\n---turn {turn}---\n")
        world_state.player.arcana = 0
        world_state.thrown_runes = runes.RunestoneBag([])
        for runestone in player.runestone_bag:
            runestone.mask = None

        slprint(f"you have [green]{world_state.player.current_hp} hp[/green] left\n")

        # prints what the enemy will do
        slprint(
            f"The mighty {world_state.current_enemy.name} is {world_state.current_enemy.action_foresight}\n"
        )

        # selection phase for the turn. In this part, the player chooses which of their runestones they will use

        runestone_choices: list[runes.Runestone] | None = choose_runes(
            world_state
        )  # the type declaration prevents error flags

        # loops to get confirmation
        while True:
            runestone_confirmation = input_processing.get_confirmation()

            if runestone_confirmation:
                slprint("runestones selected\n")
                break

            else:
                slprint("All right. Choose again\n")
                runestone_choices = choose_runes(world_state)

        # choose the stones to throw, one by one (in order)
        if runestone_choices:
            end_turn = False
            for i in range(len(runestone_choices)):
                slprint(
                    f"you draw your runestones from your bag... which would you like to throw {'next' if i != 0 else 'first'}? Press ? for more info,"
                    "and type 'end' to end your throw phase\n"
                )

                # lists the runes
                for i, runestone in enumerate(runestone_choices):
                    if runestone.nickname:
                        slprint(Text.assemble(f"{i + 1}.", runestone.nickname))
                    else:
                        slprint(Text.assemble(f"{i + 1}.", runestone.info))

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
                        thrown_rune = runestone_choices[int(user_input) - 1]
                        thrown_rune.throw(world_state)

                        world_state.thrown_runes.append(thrown_rune)
                        runestone_choices.remove(thrown_rune)

                        throw_rune_chosen = True

                # gets out of the for loop if end has been selected
                if end_turn:
                    break

        # spell casting phase
        if world_state.current_enemy.current_hp <= 0:
            battle_ongoing = False
            world_state.current_enemy.current_hp = 0

        else:
            slprint("\n---spell casting phase---\n")
            spell_choice = None  # this is to ensure it is bound
            spell_cast = True

            # this checks in case the player cannot cast any spells
            for spell in world_state.player.spells:
                if player.arcana >= spell.arcana_cost:
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
                    for i, spell in enumerate(player.spells):
                        slprint(
                            f"{i + 1}. {spell.name}, costing [purple]{spell.arcana_cost} ARCANA[/purple]"
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
                            f"you raise your hands to the sky as [purple]ARCANA[/purple] flows around you. \n You cast {spell_choice.name}"
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

                world_state.current_enemy.take_turn(world_state)

                if world_state.player.current_hp <= 0:
                    player.current_hp = 0
                    battle_ongoing = False
                    battle_end = "loss"

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
        ["battle"]
    )[
        0
    ]  # this will be in case I want to add other types of encounters, like rests or free tresure etc

    if encounter_type == "battle":
        enemy = random.choice(runes.NORMAL_ENEMIES)(
            attack_mod=random.randint(0, 10), hp_mod=random.randint(0, 10)
        )

        reward_list = []

        # the rune
        reward_list.append(random.choice(runes.ALL_RUNES)(None))

        for i in range(2):
            reward_type = random.choice(["rune", "runestone", "spell"])

            if reward_type == "rune":
                reward_list.append(random.choice(runes.ALL_RUNES)(None))

            elif reward_type == "runestone":
                reward_list.append(runes.Runestone.generate_random_runestone())

            elif reward_type == "spell":
                reward_list.append(
                    random.choice(
                        [
                            spell
                            for spell in runes.ALL_SPELLS
                            if spell
                            not in (
                                [type(spell) for spell in world_state.player.spells]
                                or [type(spell) for spell in reward_list]
                            )
                        ]
                    )()
                )

        return runes.Battle(enemy, reward_list)

    return runes.Encounter()


# simple function to initialise the player's gear
def make_starter_kit(world: runes.WorldState):
    starter_runestones = runes.RunestoneBag(
        [
            runes.Runestone.create_runestone("base"),
            runes.Runestone.create_runestone("coin"),
            runes.Runestone.create_runestone("coin"),
        ]
    )
    starter_runestones[0].add_runes([runes.IsazRune, runes.IsazRune])
    starter_runestones[1].add_runes([runes.SowuloRune])
    starter_runestones[2].add_runes([runes.IsazRune])

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
        encounter = create_encounter(world)

        if isinstance(encounter, runes.Battle):
            battle(world, encounter.enemy, encounter.rewards)
