import argparse
from os import chdir

from utils import directory_maker, default_save_dir, spotify_link_checker
from spotify import get_song_data
from youtube import download_song
from config import spotify_link_patterns


def cli_args():
    """
    Contains and parses all command line arguments for the application.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("link", help="Spotify song link to download")

    # important argument(s)
    parser.add_argument(
        "-d",
        "--dir",
        default=default_save_dir,
        help="Save directory(is created if doesn't exist)",
    )

    # audio-related arguments
    parser.add_argument(
        "-q",
        "--quiet",
        # default=True,
        action="store_const",
        const=True,
        help="Makes the downloader non-verbose/quiet",
    )

    # returns an argparse.Namespace object that stores our argument variables
    return parser.parse_args()


def controller():
    """
    Controls the flow of the program execution.
    """
    args = cli_args()

    # check whether the provided link is authentic
    spotify_link_checker(args.link, spotify_link_patterns)

    if args.dir:
        directory_maker(args.dir)
        chdir(args.dir)

    else:
        directory_maker(default_save_dir)
        chdir(default_save_dir)

    song_data = get_song_data(args.link)
    download_song(song_data)
