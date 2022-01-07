import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.id3 import ID3, APIC

import mutagen.flac
from spotify import SpotifySong
from utils import download_album_art


def add_metadata(file_name: str, song: SpotifySong, album_art_path: str):
    """
    Adds metadata to a file given it's path.
    File name must contain file extension as well.
    """

    # fix for invalid character in file name on windows
    if "?" in file_name:
        file_name = file_name.replace("?", "#")

    # writing textual metadata to the file
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

    # here we write the downloaded album art image to our downloaded song.
    meta = ID3(file_name)

    with open(album_art_path, "rb") as album_art:
        meta["APIC"] = APIC(
            # type 3 is for the front cover of a song
            encoding=3,
            mime="image/jpeg",
            type=3,
            data=album_art.read(),
        )

    # setting the v2 version to 3 is key- nothing will work without it
    meta.save(v1=2, v2_version=3)


def add_metadata_flac(file_name: str, song: SpotifySong):
    """
    Adds textual metadata to a FLAC file given it's path.
    File name must contain file extension as well.
    """

    meta = FLAC(file_name)

    try:
        meta.add_tags()

    except mutagen.flac.FLACVorbisError:
        # if this error occurs, it means that the vorbis comment block already
        # exists and we actually just need to start writing metadata
        meta.delete()

    meta["title"] = song.name
    meta["artist"] = "/".join(song.artists)
    meta["album"] = song.album_name
    meta["tracknumber"] = str(song.track_number)
    meta["discnumber"] = str(song.disc_number)

    # now, to write the album art to the file
    meta.add_picture()

    meta.save()


def metadata_controller(file_name: str, song: SpotifySong, dir: str, codec: str):
    """
    Handles the metadata writing process flow.
    """

    print("\nWriting metadata...")

    album_art_path = download_album_art(
        path=dir, link=song.cover_url, title=song.album_name
    )

    if codec == "flac" or codec == "vorbis":
        add_metadata_flac(file_name, song)

    else:
        add_metadata(file_name, song, album_art_path)

    print("\nFinished writing metadata!")


# if __name__ == "__main__":
# add_cover(file_path="./yASD-dl/Rauw Alejandro, Tainy - ¿Cuándo Fue#")
