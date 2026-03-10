# function that takes asks for input of numbers seperated by commas, and returns a list of the numbers
def get_numbers_from_input(
    prompt="",
    minimum: int = None,
    maximum: int = None,
    dupes: bool = True,
    choice_amount: int = None,
    exception: str = None,
):
    while True:
        try:
            user_input = input(prompt)
            if user_input == exception:
                return True

            last_comma = -1
            numbers = []

            # seperates the numbers between the commas (going to make this more versatile later)
            for i in range(len(user_input)):
                if user_input[i] == "," or i == len(user_input) - 1:
                    if i == len(user_input) - 1:
                        number = int((user_input[last_comma + 1 :]))
                    else:
                        number = int((user_input[last_comma + 1 : i]))

                    if choice_amount:
                        if len(numbers) + 1 > choice_amount:
                            print("you entered too many numbers")
                            raise ValueError

                    # checks that it is within the range provided (could be made more efficient)
                    if minimum:
                        if not minimum <= number:
                            raise ValueError

                    if maximum:
                        if not number <= maximum:
                            raise ValueError

                    # checks for duplicate numbers, if that is enabled
                    if not dupes:
                        for n in numbers:
                            if n == number:
                                print("you entered two of the same number")
                                raise ValueError

                    numbers.append(number)
                    last_comma = i

        except ValueError:
            print("that is not valid input, try again")

        else:
            return numbers
