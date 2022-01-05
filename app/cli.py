import argparse
import os

import utils as u
import spotify as s
import youtube as y
import config as c
import exceptions as e


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
        default=u.default_save_dir,
        help="Save directory(is created if doesn't exist)",
    )

    # audio-related arguments
    # quiet is stored to be True, means we don't have to enter anything
    # after calling "-q/--quiet", it defaults to True if called else False
    parser.add_argument(
        "-q",
        "--quiet",
        # default=False,
        action="store_true",
        help="Makes the downloader non-verbose/quiet",
    )

    parser.add_argument(
        "-c",
        "--codec",
        default="mp3",
        help=f"Audio format to download file as. List of available formats: {c.audio_formats}",
    )

    parser.add_argument(
        "-b",
        "--bitrate",
        default="320",
        help=f"Audio quality of the file. List of available qualities: {c.audio_bitrates}",
    )

    # returns an argparse.Namespace object that stores our argument variables
    return parser.parse_args()


def controller():
    """
    Controls the flow of the program execution.
    """

    args = cli_args()

    # check whether the provided link is authentic
    is_match = u.check_spotify_link(args.link, c.spotify_link_patterns)
    if not is_match:
        raise e.LinkError("You have entered an invalid Spotify link!")

    song = s.get_song_data(args.link)

    u.directory_maker(args.dir)
    os.chdir(args.dir)

    # grouping all youtube-dl required arguments together before passing them
    # as the controller func parameters
    user_params = {
        "codec": args.codec,
        "quality": args.bitrate,
        "quiet": args.quiet,
    }
    y.youtube_controller(user_params, song)
