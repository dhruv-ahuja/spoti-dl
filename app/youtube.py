from dataclasses import dataclass

from spotify import SpotifySong
from yt_dlp import YoutubeDL


@dataclass
class YoutubeSong:
    id: str
    title: str
    video_url: str


def get_config(user_params: dict, song_name: str, song_artists: list) -> dict:
    """
    Prepares the parameters that need to be passed onto the YoutubeDL object.
    """

    # preparing the list as a string
    artists = ""
    for entry in song_artists:
        if entry != song_artists[-1]:
            artists += entry + ", "
        else:
            artists += entry

    downloader_params = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": user_params["codec"],
                "preferredquality": user_params["quality"],
            }
        ],
        "outtmpl": f"{artists}- {song_name}.%(ext)s",
        "quiet": user_params["quiet"],
    }

    return downloader_params


def get_downloader(params: dict):
    """
    Initiates the YoutubeDL class with the configured parameters.
    """

    return YoutubeDL(params=params)


def fetch_source(yt: YoutubeDL, song: SpotifySong) -> YoutubeSong:
    """
    Fetch apt source for the song from Youtube using the given details.
    """

    try:
        # using Song dataclasses' __repr__ function to construct the song name
        # adding "audio" to avoid 'official music videos' and similar types 😅
        song_title = str(song) + " audio"

        yt_info = yt.extract_info(f"ytsearch:{song_title}", download=False)
        yt_info = yt_info["entries"][0]

    except Exception as e:
        print("Error when trying to get audio source from YT: ", e)
        return

    else:
        yt_song = YoutubeSong(
            id=yt_info["id"], title=yt_info["title"], video_url=yt_info["webpage_url"]
        )

        return yt_song


def download_song(yt: YoutubeDL, link: str):
    """
    Registers the provided parameters with the YoutubeDL object and
    downloads the song using the extracted information.
    """

    print("Starting download...\n")

    try:
        # using try-else since afaik the library itself doesn't return
        # any errors
        # attempts to download the song using the best matched
        # youtube source link
        yt.download(link)

    except:
        print("Download failed!")

    else:
        print(f"Successfully finished downloading!")


def youtube_controller(user_params: dict, song: SpotifySong):
    """
    Handles the flow of the download process for the given song.
    Initiates the configuration as per the user-defined parameters and chains
    the rest of functions together.
    """

    # user parameters are used in the downloader parameters dictionary
    # the downloader_params dict is then passed onto the YoutubeDL object
    # when generating its instance.
    downloader_params = get_config(user_params, song.name, song.artists)
    yt = get_downloader(downloader_params)

    yt_song = fetch_source(yt, song)
    download_song(yt, yt_song.video_url)


if __name__ == "__main__":

    song = SpotifySong("He Don't Love Me", ["Winona Oak"], "")

    user_params = {"codec": "mp3", "quality": "320", "quiet": True}

    youtube_controller(user_params, song)
