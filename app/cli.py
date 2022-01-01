import argparse
from os import chdir

from utils import directory_maker, default_save_dir
from spotify import get_song_data
from youtube import download_song


def cli_args():
    """
    Contains and parses all command line arguments for the application.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("link", help="Spotify song link to download")

    # base arguments
    parser.add_argument(
        "-d",
        "--dir",
        default=default_save_dir,
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

    if args.dir:
        directory_maker(args.dir)
        chdir(args.dir)

    else:
        directory_maker(default_save_dir)
        chdir(default_save_dir)

    song_data = get_song_data(args.link)
    download_song(song_data)
