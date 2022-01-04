import argparse
from os import chdir


from utils import directory_maker, default_save_dir, check_spotify_link
from spotify import get_song_data
from youtube import Downloader
from config import spotify_link_patterns, audio_formats, audio_bitrates


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
    # quiet is stored to be True, means we don't have to enter anything
    # after calling "-q/--quiet", it defaults to True if called else False
    parser.add_argument(
        "-q",
        "--quiet",
        default=False,
        action="store_true",
        help="Makes the downloader non-verbose/quiet",
    )

    parser.add_argument(
        "-c",
        "--codec",
        default="mp3",
        help=f"Audio format to download file as. List of available formats: {audio_formats}",
    )

    parser.add_argument(
        "-b",
        "--bitrate",
        default="192",
        help=f"Audio quality of the file. List of available qualities: {audio_bitrates}",
    )

    # returns an argparse.Namespace object that stores our argument variables
    return parser.parse_args()


def controller():
    """
    Controls the flow of the program execution.
    """

    args = cli_args()
    dl = Downloader()

    # check whether the provided link is authentic
    check_spotify_link(args.link, spotify_link_patterns)

    if args.dir:
        directory_maker(args.dir)
        chdir(args.dir)

    else:
        directory_maker(default_save_dir)
        chdir(default_save_dir)

    song_data = get_song_data(args.link)
    download_song(song_data)
