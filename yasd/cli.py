import argparse
import os

import yasd.utils as u
# import utils as u
import yasd.spotify as s
import yasd.youtube as y
import yasd.config as c
import yasd.exceptions as e
import yasd.metadata as m


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

    #  perform necessary argument validity checks
    if not u.check_cli_args(args.codec, args.bitrate, args.link):
        raise e.LinkError("Invalid Spotify link entered!")

    # i believe getting the link type should be separated from just checking
    # the validity of the link and the audio-related args like codec and bitrate
    link_type = u.get_link_type(args.link)
    if not link_type in c.spotify_link_types:
        raise e.LinkError("Invalid Spotify link type entered!")

    # make the specified dir. if it doesn't exist and open it to store files
    u.directory_maker(args.dir)
    os.chdir(args.dir)

    # grouping all youtube-dl required arguments together before passing them
    # as the controller func parameters
    user_params = {
        "codec": args.codec,
        "quality": args.bitrate,
        "quiet": args.quiet,
        "dir": args.dir,
    }

    match link_type:
        case "track":
            song_download_controller(args.link, user_params)

        case "album":
            # album controller requires the directory since it will 
            # create a separate folder for the album
            album_download_controller(args.link, user_params)

        case "playlist":
            playlist_download_controller(args.link, user_params)


def song_download_controller(link: str, user_params: dict):
    """
    Handles the control flow for the process to download an individual song.
    """

    # gets the SpotifySong dataclass object to be used for everything else in the func
    song = s.get_song_data(link)

    # use the youtube controller to scrape audio source and download the song
    y.controller(user_params, song)

    # write metadata to the downloaded file
    file_name = (
        f"{u.make_song_title(song.artists, song.name, ', ')}.{user_params['codec']}"
    )

    m.controller(file_name, song, user_params["dir"], user_params["codec"])


def album_download_controller(link: str, user_params: dict):
    """
    Handles the control flow for the process to download a complete album.
    """

    # get album information
    album_name, songs = s.get_album_data(link)
    save_dir = "./" + album_name

    #make a directory to store the album
    u.directory_maker(save_dir)
    os.chdir(save_dir)

    for song in songs:
        y.controller(user_params, song)

        # write metadata to the downloaded file
        file_name = f"{u.make_song_title(song.artists, song.name, ', ')}.{user_params['codec']}"
        

        # since we have already entered the <album_name> directory, we don't
        # have to pass in anything except the current directory indicator 
        # we have to change directories since we are creating a dedicated folder
        # for the album unlike a song
        m.controller(file_name, song, ".", user_params["codec"])

    print(f"\nDownload for album '{album_name}' completed. Enjoy!")


def playlist_download_controller(link: str, user_params: dict):
    """
    Handles the control flow for the process to download a complete playlist.
    """

    # get playlist information
    playlist_name, songs = s.get_playlist_data(link)
    save_dir = "./" + playlist_name

    # make a directory to store the playlist
    u.directory_maker(save_dir)
    os.chdir(save_dir)

    for song in songs: 
        y.controller(user_params, song)

        # write metadata to the downloaded file
        file_name = f"{u.make_song_title(song.artists, song.name, delim=', ')}.{user_params['codec']}"

        # passing "." aka curr dir indicator since we've already moved 
        # into the <playlist_name> directory
        m.controller(file_name, song, dir=".", codec=user_params["codec"])
    
    print(f"\nDownload for playlist '{playlist_name}' completed. Enjoy!")