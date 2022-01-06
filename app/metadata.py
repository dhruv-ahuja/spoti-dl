import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC

from spotify import SpotifySong
from utils import download_album_art


def add_metadata(file_name: str, song: SpotifySong):
    """
    Adds textual metadata to a song given it's path.
    File name must contain file extension as well.
    """

    if "?" in file_name:
        file_name = file_name.replace("?", "#")

    try:
        meta = EasyID3(file_name)

    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(file_name, easy=True)
        meta.add_tags()

    meta["title"] = song.name
    meta["artist"] = "/".join(song.artists)
    meta["album"] = song.album_name
    meta["tracknumber"] = str(song.track_number)
    meta["discnumber"] = str(song.disc_number)

    meta.save(v2_version=3)


def add_cover(file_path: str, album_art_path: str):
    """
    Adds album art to a song given its local directory path and album art URL.
    """

    if "?" in file_path:
        file_path = file_path.replace("?", "#")

    meta = ID3(file_path)

    # here we write the downloaded album art image to our downloaded song.
    with open(album_art_path, "rb") as album_art:
        meta["APIC"] = APIC(
            encoding=3, mime="image/jpeg", type=3, data=album_art.read()
        )

    # setting the v2_version to 3 is the key; nothing will work without it!
    meta.save(v2_version=3)


def metadata_controller(file_name: str, song: SpotifySong, dir: str):
    """
    Handles the metadata writing process flow.
    """

    print("\nWriting metadata...")
    add_metadata(file_name, song)

    album_art_path = download_album_art(
        path=dir, link=song.cover_url, title=song.album_name
    )

    add_cover(file_name, album_art_path)

    print("\nFinished writing metadata!")


if __name__ == "__main__":
    add_cover(file_path="./yASD-dl/Rauw Alejandro, Tainy - ¿Cuándo Fue#")
