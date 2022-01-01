from dataclasses import dataclass
from youtube_dl import YoutubeDL
from spotify import Song

# todo: convert this to be modular, add ability to customize options
options = {
    "format": "bestaudio",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }
    ],
    # todo: change the output according to the song title and artist
    "outtmpl": "%(title)s.%(ext)s",
    "quiet": True,
    "noplaylist": True,
    "progress": True,
    "newline": True,
}

yt = YoutubeDL(options)


# creating a YoutubeSong dataclass just for insurance, if there's no need for it
# later, will remove it
@dataclass
class YoutubeSong:
    id: int
    title: str
    artist: str
    track: str
    video_url: str


def download_song(song: Song):
    """
    Download the song using the given details. Returns False in case of errors.
    """

    try:
        # using Song dataclasses' __repr__ function to construct the song name
        # adding "audio" to avoid music videos 😅
        song_title = str(song) + "audio"

        yt_info = yt.extract_info(f"ytsearch:{song_title}", download=False)
        yt_info = yt_info["entries"][0]
        # print(yt_info.keys())

        yt_song = YoutubeSong(
            id=yt_info["id"],
            title=yt_info["title"],
            video_url=yt_info["webpage_url"],
            artist=yt_info["artist"],
            track=yt_info["track"],
        )

        print("Starting download...")
        print(yt_info["track"], "artist: ", yt_info["artist"])
        # yt.download([yt_song.video_url])

    except Exception as e:
        print(e)

    else:
        print(f"Successfully downloaded {song.name}")


if __name__ == "__main__":
    download_song(song=Song("Whats Poppin(feat DaBaby)", ["Jack Harlow"], ""))
