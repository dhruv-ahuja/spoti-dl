from dataclasses import dataclass
from youtube_dl import YoutubeDL
from spotify import Song

# options = {
#     "format": "bestaudio/best",
#     "postprocessors": [
#         {
#             "key": "FFmpegExtractAudio",
#             "preferredcodec": "mp3",
#             # "preferredquality": "320",
#         }
#     ],
#     "outtmpl": "%(title)s.%(ext)s",
#     "quiet": False,
#     "noplaylist": True,
# }

yt = YoutubeDL()


@dataclass
class YoutubeSong:
    id: int
    title: str
    video_url: str


def download_song(song: Song):
    """
    Download the song using the given details.
    """
    # using Song dataclasses' __repr__ function to construct the song name
    song_title = str(song)

    yt_info = yt.extract_info(f"ytsearch:{song_title}", download=False)["entries"][0]
    # stripping link of https
    link = "".join(yt_info["webpage_url"])
    yt_song = YoutubeSong(
        id=yt_info["id"],
        title=yt_info["title"],
        video_url=yt_info["webpage_url"],
    )
    # print(yt_song)
    try:
        print(yt_song.video_url)
        dl = yt.download([yt_song.video_url], codec="mp3", bitrate="320", quiet=False)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    download_song(song=Song("He Don't Love Me", ["Winona Oak"], ""))
