import os
from re import search

from exceptions import LinkError


default_save_dir = os.getcwd() + "/yASD-dl"


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
        os.makedirs(path, exist_ok=True)

    except OSError as e:
        print("Error when attempting to make directory: ", e)

    else:
        return True


def check_dir(path: str) -> bool:
    return os.path.isdir(path)


def check_file(path: str) -> bool:
    return os.path.isfile(path)


def directory_maker(path: str):
    """
    Checks for the existence of a directory given the path
    and makes one if it doesn't exist.
    """

    if not check_dir(path):
        # if there's an error making the directory,
        # the app will return False automatically
        if make_dir(path):
            print("Successfully created save directory.")

    else:
        print("Directory exists, using it as save space.")


if __name__ == "__main__":
    mk = directory_maker("./app/yASD-dl")
    print(mk)


def check_spotify_link(link: str, patterns_list: list):
    """
    Handles all checks needed to vet user-entered Spotify links.
    """
    if not link:
        raise LinkError("You have entered an empty link!")

    # patterns_list contains a list of regex patterns for Spotify URLs
    for pattern in patterns_list:
        if not search(pattern=pattern, string=link):
            raise LinkError("You have entered an invalid Spotify link!")
