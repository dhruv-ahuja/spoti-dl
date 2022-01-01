import os


default_save_dir = "./yASD-dl"


def choice(msg: str) -> bool:
    """
    Offer the user a choice, infinite loop till they make a decision.
    """
    user_choice = ""
    choice_list = ("y", "n")
    while user_choice not in choice_list:
        user_choice = input(msg + ": ")

    return True if user_choice[0].lower() == "y" else False


def make_dir(path: str) -> bool:
    try:
        os.makedirs(path)

    except OSError as e:
        print("Error when trying to make directory: ", e)

    else:
        return True


def check_dir(path: str) -> bool:
    return os.path.isdir(path)


def check_file(path: str) -> bool:
    return os.path.isfile(path)


def directory_maker(path: str) -> bool:
    if not check_dir(path):
        # we don't need an else statement for the make_dir function
        # since we already have implemented error handling
        if not make_dir(path):
            print("Directory already exists!")
            return False

        print("Successfully created save directory!")
        return True
