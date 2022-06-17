import mutagen
import mutagen.easyid3
import mutagen.id3
import mutagen.flac

from spotidl.spotify import SpotifySong
from spotidl.utils import download_album_art


def add_metadata_mp3(file_name: str, song: SpotifySong, album_art_path: str):
    """
    Adds metadata to a MP3 file given it's path.
    File name must contain file extension as well.
    """

    # writing textual metadata to the file
    try:
        meta = mutagen.easyid3.EasyID3(file_name)

    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(file_name, easy=True)
        meta.add_tags()

    meta["title"] = song.name
    #  ID3v2.3 spec: the delimiter is a "/" for multiple entries.
    meta["artist"] = "/".join(song.artists)
    meta["album"] = song.album_name
    meta["tracknumber"] = str(song.track_number)
    meta["discnumber"] = str(song.disc_number)

    meta.save(v2_version=3)

    # here we write the downloaded album art image to our downloaded song.
    if album_art_path:
        meta = mutagen.id3.ID3(file_name)

        with open(album_art_path, "rb") as pic:
            meta["APIC"] = mutagen.id3.APIC(
                # type 3 is for the front cover of a song
                encoding=3,
                mime="image/jpeg",
                type=3,
                data=pic.read(),
            )

        # setting the v2 version to 3 is key- nothing will work without it
        meta.save(v2_version=3)


def add_metadata_flac(file_name: str, song: SpotifySong, album_art_path: str):
    """
    Adds metadata to a FLAC file given it's path.
    File name must contain file extension as well.
    """

    meta = mutagen.flac.FLAC(file_name)

    try:
        meta.add_tags()

    except mutagen.flac.FLACVorbisError:
        # if this error occurs, the vorbis comment block already exists
        meta.delete()

    meta["TITLE"] = song.name
    meta["ARTIST"] = "/".join(song.artists)
    meta["ALBUM"] = song.album_name
    meta["TRACKNUMBER"] = str(song.track_number)
    meta["DISCNUMBER"] = str(song.disc_number)

    # now, to write the album art to the file
    if album_art_path:
        pic = mutagen.flac.Picture()

        with open(album_art_path, "rb") as img:
            pic.data = img.read()

        pic.type = mutagen.id3.PictureType.COVER_FRONT
        pic.mime = "image/jpeg"
        pic.width = pic.height = 500

        meta.add_picture(pic)

    meta.save()


# setting default directory to be the current folder(represented as ".")
def controller(file_name: str, song: SpotifySong, codec: str, directory: str = "."):
    """
    Handles the metadata writing process flow.
    """

    album_art_path = download_album_art(
        path=directory, link=song.cover_url, title=song.album_name
    )

    if not album_art_path:
        print("Album art couldn't be retrieved.")

    print("\nWriting metadata...")

    if codec == "flac":
        add_metadata_flac(file_name, song, album_art_path)

    elif codec == "mp3":
        add_metadata_mp3(file_name, song, album_art_path)

    print("\nFinished writing metadata!\n")
