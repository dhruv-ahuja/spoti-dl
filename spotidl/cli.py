import argparse
import os

import dotenv

from spotidl import utils, spotify, downloader, config, exceptions, metadata
from . import __version__
from spotidl_rs import process_downloads


# loading .env vars
dotenv.load_dotenv()


def fetch_cli_args() -> argparse.Namespace:
    """
    Fetch all command-line arguments defined for the application.
    """

    parser = argparse.ArgumentParser(
        prog="spotidl",
        description="spotidl: download songs, albums and playlists using Spotify links",
    )
    parser.add_argument("link", help="Spotify song link to download")

    parser.add_argument(
        "-d",
        "--dir",
        default=utils.default_save_dir,
        help="Save directory(is created if doesn't exist)",
    )

    # quiet is a 'stored' argument, defaults to True if passed else False
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Makes the downloader non-verbose/quiet",
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

    # returns the app version defined in the poetry.toml file
    # this 'action' value helps fetch the latest version automatically; helpful for tests
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
        help="Displays the current app version",
    )

    return parser.parse_args()


def prerun_checks(args: argparse.Namespace):
    """
    Performs all pre-run checks to ensure that the app is configured properly and the input is valid.
    """

    if not utils.check_ffmpeg_installed():
        raise exceptions.FFmpegNotInstalledError()

    env_vars = utils.load_env_vars()
    utils.check_env_vars(env_vars)


async def controller():
    """
    Executes the main application flow by preparing the spotify client and extracting its active token.
    Calls and awaits the rust entrypoint function, passing the token and other input values required for the
    full download flow.
    """

    args = fetch_cli_args()
    prerun_checks(args)

    client = spotify.get_spotify_client()
    token = spotify.get_spotify_token(client)

    await process_downloads(token, args.link, args.dir, args.codec, args.bitrate)


def song_download_controller(link: str, user_params: dict):
    """
    Handles the control flow for the process to download an individual song.
    """

    # gets the SpotifySong dataclass object to be used for everything else in the func
    song = spotify.get_song_data(link)

    # create the file name to be used when writing metadata
    file_name = f"{utils.make_song_title(song.artists, song.name, ', ')}.\
{user_params['codec']}"

    # use the youtube controller to download the song
    # we also send the filename here since the download controller checks
    # to ensure that the song hasn't been downloaded before.
    is_downloaded = downloader.controller(user_params, song, file_name)

    if is_downloaded:
        # write metadata to the downloaded file
        metadata.controller(file_name, song, codec=user_params["codec"], directory=user_params["dir"])


def album_download_controller(link: str, user_params: dict):
    """
    Handles the control flow for the process to download a complete album.
    """

    # get album information
    album_name, songs = spotify.get_album_data(link)
    save_dir = "./" + album_name

    # make a directory to store the album
    utils.directory_maker(save_dir)
    os.chdir(save_dir)

    print(f"Starting '{album_name}' album download...\n")

    for song in songs:
        file_name = f"{utils.make_song_title(song.artists, song.name, ', ')}.\
{user_params['codec']}"

        is_downloaded = downloader.controller(user_params, song, file_name)

        if is_downloaded:
            # write metadata to the downloaded file
            metadata.controller(file_name, song, codec=user_params["codec"])

    print(f"\nDownload for album '{album_name}' completed. Enjoy!")


def playlist_download_controller(link: str, user_params: dict):
    """
    Handles the control flow for the process to download a complete playlist.
    """

    # get playlist information
    playlist_name, songs = spotify.get_playlist_data(link)
    save_dir = "./" + playlist_name

    # make a directory to store the playlist
    utils.directory_maker(save_dir)
    os.chdir(save_dir)

    print(f"Starting '{playlist_name}' playlist download...\n")

    for song in songs:
        file_name = f"{utils.make_song_title(song.artists, song.name, delim=', ')}.\
{user_params['codec']}"

        is_downloaded = downloader.controller(user_params, song, file_name)

        if is_downloaded:
            # write metadata to the downloaded file
            metadata.controller(file_name, song, codec=user_params["codec"])

    print(f"\nDownload for playlist '{playlist_name}' completed. Enjoy!")
