# function that takes asks for input of numbers seperated by commas, and returns a list of the numbers
def get_numbers_from_input(
    prompt: str = "",
    minimum: int | None = None,
    maximum: int | None = None,
    dupes: bool = True,
    choice_amount: int | None = None,
    exceptions: list[str] | None = None,
):
    while True:
        try:
            user_input = input(prompt)
            if exceptions:
                if user_input.lower() in exceptions:
                    return [user_input.lower()]

            numbers = user_input.split(",")

            numbers = [int(n) for n in numbers if n.isdigit()]

            if choice_amount and len(numbers) > choice_amount:
                raise ValueError("too many numbers")

            if minimum or maximum:
                for n in numbers:
                    if (n < minimum if minimum else False) or (
                        n > maximum if maximum else False
                    ):
                        raise ValueError("out of range")

            if not dupes:
                for n in numbers:
                    if numbers.count(n) > 1:
                        raise ValueError("you entered the same thing twice")

            if not numbers:
                raise ValueError("you didn't select anything")

            # seperates the numbers between the commas (going to make this more versatile later)
            # for i in range(len(user_input)):
            #     if user_input[i] == "," or i == len(user_input) - 1:
            #         if i == len(user_input) - 1:
            #             number = int((user_input[last_comma + 1 :]))
            #         else:
            #             number = int((user_input[last_comma + 1 : i]))

            #         if choice_amount:
            #             if len(numbers) + 1 > choice_amount:
            #                 print("you entered too many numbers")
            #                 raise ValueError("you entered too many numbers")

            #         # checks that it is within the range provided (could be made more efficient)
            #         if minimum:
            #             if not minimum <= number:
            #                 print("out of range!")
            #                 raise ValueError

            #         if maximum:
            #             if not number <= maximum:
            #                 print("out of range!")
            #                 raise ValueError

            #         # checks for duplicate numbers, if that is enabled
            #         if not dupes:
            #             for n in numbers:
            #                 if n == number:
            #                     print("you entered two of the same number")
            #                     raise ValueError

            #         numbers.append(number)
            #         last_comma = i

        except ValueError:
            print("that is not valid input, try again")

        else:
            return numbers


def get_confirmation(prompt: str = "is this your choice?"):
    while True:
        confirmation = input(f"{prompt} - y/n ")

        if confirmation.lower() in ("y", "yes", "1"):
            return True

        elif confirmation.lower() in ("n", "no", "2"):
            return False

        else:
            print("that is not a yes or a no!")
