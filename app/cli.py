import argparse

import utils


def cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("link", help="Spotify song link to download")

    # base arguments
    parser.add_argument(
        "-d",
        "--dir",
        # default="./yASD-dl",
        help="Save directory(is created if doesn't exist)",
    )

    # audio-related arguments
    # todo

    # returns an argparse.Namespace object that stores our argument variables
    return parser.parse_args()


def controller():
    """
    Controls the flow of the program execution.
    """
    args = cli_args()

    if not args.dir:
        print("You have not defined a save directory.")
        print("Make a directory in the current folder?")
        user_choice = utils.choice(
            "Enter 'y' or 'n'(if 'n' then define directory in the next prompt): "
        )

        if not user_choice:
            save_dir = input("Save directory(is created if doesn't exist): ")
            # now, check whether the directory exists already or not
            # if not, create the directory
            utils.directory_maker(save_dir)

        else:
            utils.directory_maker(utils.default_save_dir)
