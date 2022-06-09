from dataclasses import dataclass

from yt_dlp import YoutubeDL
import yt_dlp

from spotidl.spotify import SpotifySong
from spotidl.utils import make_song_title, check_file


@dataclass
class YoutubeSong:
    """
    Umbrella for the song data extracted from Youtube.
    """

    id: str
    title: str
    video_url: str


def get_config(user_params: dict, song: SpotifySong) -> dict:
    """
    Prepares the parameters that need to be passed onto the YoutubeDL object.
    """

    downloader_params = {
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": user_params["codec"],
                "preferredquality": user_params["quality"],
            }
        ],
        "outtmpl": f"{make_song_title(song.artists, song.name, ', ')}.%(ext)s",
        # "outtmpl": "%(artist)s-%(title)s.ext",
        "quiet": user_params["quiet"],
        "format": "bestaudio/best",
        "dynamic_mpd": False,
        "noplaylist": True,
        "prefer_ffmpeg": True,
    }

    return downloader_params


def get_downloader(params: dict):
    """
    Initiates the YoutubeDL class with the configured parameters.
    """

    return YoutubeDL(params=params)


def fetch_source(ydl: YoutubeDL, song: SpotifySong) -> YoutubeSong:
    """
    Fetch appropriate source for the song from Youtube using the given details.
    """

    try:
        # adding "audio" to avoid 'official music videos' and similar types
        song_title = make_song_title(song.artists, song.name, ", ") + " audio"

        search: dict = ydl.extract_info(f"ytsearch:{song_title}", download=False)

        # extracting the first entry from the nested dict
        yt_info = search["entries"][0]
        audio_source_title = yt_info["title"]

        # we are unable to find the song and are probably grabbing a different
        # audio source altogether if the artist name doesn't match or doesn't
        # exist in the audio source title
        if (
            song.name not in audio_source_title
            or song.artists[0] not in audio_source_title
        ):
            print("Couldn't find the apt audio source with that name, retrying...")

            # retrying the search but with album name added
            song_title = (
                make_song_title(song.artists, song.name, ", ")
                + f" {song.album_name} audio"
            )

            search: dict = ydl.extract_info(f"ytsearch:{song_title}", download=False)

            yt_info = search["entries"][0]
            audio_source_title = yt_info["title"]
            # now, if we are still getting the wrong result,
            # we should avoid the download
            return

    except yt_dlp.DownloadError as ex:
        print("Error when trying to get audio source from YT: ", ex)
        return

    else:
        yt_song = YoutubeSong(
            id=yt_info["id"],
            title=audio_source_title,
            video_url=yt_info["webpage_url"],
        )

        return yt_song


def download_song(ydl: YoutubeDL, link: str, count: int = 0) -> bool:
    """
    Downloads the song given its source link and the YouTube downloader object.
    """

    while count < 3:
        try:
            # attempts to download the song using the best matched
            # youtube source link
            count += 1
            ydl.download(link)

        except yt_dlp.DownloadError as ex:
            if count >= 3:
                print("\nDownload failed: ", ex)
                return False

            print("\nDownload failed! Retrying...")
            # call the function again but increase the count figure
            download_song(ydl, link, count=count + 1)

        else:
            return True


def controller(user_params: dict, song: SpotifySong, file_name: str) -> bool:
    """
    Handles the flow of the download process for the given song.
    Initiates the configuration as per the user-defined parameters and chains
    the rest of functions together.
    """

    # check if song has already been downloaded before at some point;
    # only proceed with download if it doesn't
    if check_file(file_name):
        print(f"\n{file_name} already exists! Skipping download...\n")
        # False will ensure that we don't attempt to re-write metadata again
        return False

    # user parameters are used in the downloader parameters dictionary
    # the downloader_params dict is then passed onto the YoutubeDL object
    # when generating its instance.
    downloader_params = get_config(user_params, song)
    ydl = get_downloader(downloader_params)

    print(f"Starting '{song}' song download...\n")
    yt_song = fetch_source(ydl, song)

    if not yt_song:
        print("Couldn't find audio source for the song, skipping...\n")
        return False

    if not download_song(ydl, yt_song.video_url):
        # we already print the download failed statement when encountering
        # the exception in the function itself, so just return False here
        return False

    print(f"\nDownload for song '{song}' completed. Enjoy!")
    return True
