import argparse
import logging

import dotenv

from . import __version__, spotidl_rs
from spotidl import utils, config, spotify


dotenv.load_dotenv()


def fetch_cli_args() -> argparse.Namespace:
    """
    Fetch all command-line arguments defined for the application.
    """

    parser = argparse.ArgumentParser(
        prog="spotidl",
        description="spotidl: download songs, albums and playlists using Spotify links",
    )
    parser.add_argument("link", help="Spotify song/album/playlist link to download")
    parser.add_argument(
        "-d",
        "--dir",
        default=utils.default_save_dir,
        help="Save directory (created if doesn't exist)",
    )
    parser.add_argument(
        "-c",
        "--codec",
        default="mp3",
        help=f"Audio format to download file as. List of available formats: {config.audio_formats}",
    )
    parser.add_argument(
        "-b",
        "--bitrate",
        default="320",
        help=f"Audio quality of the file. List of available qualities: {config.audio_bitrates}",
    )
    parser.add_argument(
        "-p",
        "--parallel-downloads",
        default="5",
        help="Maximum number of parallel song downloads. Limit: 1-100. Default: 5",
    )

    # returns the app version as in the poetry.toml file
    # this 'action' value helps fetch the latest version automatically; helpful for tests
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
        help="Displays the current app version",
    )

    return parser.parse_args()


async def controller():
    """
    Executes the main application flow by preparing the spotify client and extracting its active token.
    Calls and awaits the rust entrypoint function, passing the token and other input values required for the
    full download flow.
    """

    utils.initialize_logger(config.LOG_FILE, config.LOG_MESSAGE_FORMAT, config.LOG_DATETIME_FORMAT, logging.WARN)
    args = fetch_cli_args()

    env_vars = utils.load_env_vars()
    if not utils.check_env_vars(env_vars):
        colorized_error = utils.colorize_message(config.ENV_VARS_ERROR, config.RED_COLOR_CODE)
        print(colorized_error)
        return

    if not utils.check_ffmpeg_installed():
        colorized_error = utils.colorize_message("Please install ffmpeg before continuing!", config.RED_COLOR_CODE)
        print(colorized_error)
        return

    client = spotify.get_spotify_client()
    token = spotify.get_spotify_token(client)

    await spotidl_rs.process_downloads(token, args.link, args.dir, args.codec, args.bitrate, args.parallel_downloads)
