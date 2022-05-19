import argparse
import os
import pkg_resources

import dotenv


from spotidl import utils, spotify, downloader, config, exceptions, metadata


# loading .env vars
dotenv.load_dotenv()


def cli_args() -> argparse.Namespace:
    """
    Contains and parses all command line arguments for the application.
    """

    parser = argparse.ArgumentParser(
        prog="spotidl",
        description="spotidl: download songs, albums and playlists using Spotify links",
    )
    parser.add_argument("link", help="Spotify song link to download")

    # important argument(s)
    parser.add_argument(
        "-d",
        "--dir",
        default=utils.default_save_dir,
        help="Save directory(is created if doesn't exist)",
    )

    # audio-related arguments
    # quiet is a 'stored' argument, means we don't have to enter anything
    # after calling "-q/--quiet", it defaults to True if called else False
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

    # misc. arguments
    # tells the app version by reading it from the poetry toml file
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=pkg_resources.get_distribution("spoti-dl").version,
        help="Displays the current app version",
    )

    return parser.parse_args()


def prerun_checks(args: argparse.Namespace):
    """
    Performs all the necessary pre-run checks.
    """

    # we can't download and convert songs using the yt-dlp library w/o ffmpeg
    if not utils.check_ffmpeg_installed():
        raise exceptions.FFmpegNotInstalledError()

    #  perform necessary cli-argument validity checks
    if not utils.check_cli_args(args.codec, args.bitrate, args.link):
        raise exceptions.LinkError()

    # checks to see whether required environment variables have been added
    # or not
    utils.check_env_vars()


def controller():
    """
    Controls the flow of the program execution.
    """

    args = cli_args()
    prerun_checks(args)

    # i believe getting the link type should be separated from just checking
    # the validity of the link and the audio-related args like codec and bitrate
    # that are covered in the prerun_checks func
    link_type = utils.get_link_type(args.link)

    if not link_type in config.spotify_link_types:
        raise exceptions.LinkError("Invalid Spotify link type entered!")

    # make the specified dir. if it doesn't exist and open it to store files
    utils.directory_maker(args.dir)
    os.chdir(args.dir)

    # grouping all youtube-dl required arguments together before passing them
    # as the controller func parameters
    user_params = {
        "codec": args.codec,
        "quality": args.bitrate,
        "quiet": args.quiet,
        "dir": args.dir,
    }

    # replacing match-case with if else for comaptibility's sake
    if link_type == "track":
        song_download_controller(args.link, user_params)

    elif link_type == "album":
        album_download_controller(args.link, user_params)

    elif link_type == "playlist":
        playlist_download_controller(args.link, user_params)


def song_download_controller(link: str, user_params: dict):
    """
    Handles the control flow for the process to download an individual song.
    """

    # gets the SpotifySong dataclass object to be used for everything else in the func
    song = spotify.get_song_data(link)

    # create the file name to be used when writing metadata
    file_name = f"{utils.make_song_title(song.artists, song.name, ', ')}.\
{user_params['codec']}"

    print(f"Starting '{song.name}' song download...\n")
    # use the youtube controller to download the song
    # we also send the filename here since the download controller checks
    # to ensure that the song hasn't been downloaded before.
    downloader.controller(user_params, song, file_name)

    # write metadata to the downloaded file
    metadata.controller(
        file_name, song, codec=user_params["codec"], directory=user_params["dir"]
    )

    print(f"\nDownload for song '{song.name}' completed. Enjoy!")


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

    print(f"Starting '{album_name}' song download...\n")

    for song in songs:
        file_name = f"{utils.make_song_title(song.artists, song.name, ', ')}.\
{user_params['codec']}"

        downloader.controller(user_params, song, file_name)

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

    print(f"Starting '{playlist_name}' song download...\n")

    for song in songs:
        file_name = f"{utils.make_song_title(song.artists, song.name, delim=', ')}.\
{user_params['codec']}"

        downloader.controller(user_params, song, file_name)

        # write metadata to the downloaded file
        metadata.controller(file_name, song, codec=user_params["codec"])

    print(f"\nDownload for playlist '{playlist_name}' completed. Enjoy!")
