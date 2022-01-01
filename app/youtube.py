from dataclasses import dataclass

# from youtube_dl import YoutubeDL
from spotify import Song
from yt_dlp import YoutubeDL

# todo: convert this to be modular, add ability to customize options
options = {
    "format": "bestaudio/best",
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

    def __repr__(self):
        return f"{self.artist}: {self.title}"


def fetch_source(song: Song) -> YoutubeSong:
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

    else:
        yt_song = YoutubeSong(
            id=yt_info["id"],
            title=yt_info["title"],
            video_url=yt_info["webpage_url"],
            artist=yt_info["artist"],
            track=yt_info["track"],
        )

        return yt_song


def download_song(song: YoutubeSong, parameters: list[str]) -> bool:
    print("Starting download...")
    # print("artist: ", yt_info["artist"], yt_info["track"])
    # yt.download([yt_song.video_url])
    print(f"Successfully downloaded {song.name}")


if __name__ == "__main__":
    download_song(song=Song("Whats Poppin(feat DaBaby)", ["Jack Harlow"], ""))
    # download_song(song=Song("He Dont Love Me", ["Winona Oak"], ""))
