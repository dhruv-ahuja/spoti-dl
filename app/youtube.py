from dataclasses import dataclass

from spotify import SpotifySong
from yt_dlp import YoutubeDL
from utils import make_song_title


@dataclass
class YoutubeSong:
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
        song_title = make_song_title(song.artists, song.name, ", ") + " audio"
        search = yt.extract_info(f"ytsearch:{song_title}", download=False)
        yt_info = search["entries"][0]

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

    print("\nStarting download..")

    try:
        # attempts to download the song using the best matched
        # youtube source link
        yt.download(link)

    except:
        print("\nDownload failed!")

    else:
        print(f"\nSuccessfully finished downloading!")


def youtube_controller(user_params: dict, song: SpotifySong):
    """
    Handles the flow of the download process for the given song.
    Initiates the configuration as per the user-defined parameters and chains
    the rest of functions together.
    """

    # user parameters are used in the downloader parameters dictionary
    # the downloader_params dict is then passed onto the YoutubeDL object
    # when generating its instance.
    downloader_params = get_config(user_params, song)
    yt = get_downloader(downloader_params)

    yt_song = fetch_source(yt, song)
    download_song(yt, yt_song.video_url)


if __name__ == "__main__":

    song = SpotifySong(
        name="He Don't Love Me",
        artists=["Winona Oak"],
        cover_url="",
        album_name="",
        disc_number=10,
        track_number=20,
    )

    user_params = {"codec": "mp3", "quality": "320", "quiet": True}

    youtube_controller(user_params, song)
