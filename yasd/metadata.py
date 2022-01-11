import mutagen
import mutagen.easyid3 
import mutagen.id3 
import mutagen.flac
import mutagen.mp4
import mutagen.m4a

from yasd.spotify import SpotifySong
from yasd.utils import download_album_art


def add_metadata_mp3(file_name: str, song: SpotifySong, album_art_path: str):
    """
    Adds metadata to a MP3 file given it's path.
    File name must contain file extension as well.
    """

    # fix for invalid character in file name on windows
    if "?" in file_name:
        file_name = file_name.replace("?", "#")

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

    meta["title"] = song.name
    meta["artist"] = "/".join(song.artists)
    meta["album"] = song.album_name
    meta["tracknumber"] = str(song.track_number)
    meta["discnumber"] = str(song.disc_number)

    # now, to write the album art to the file
    p = mutagen.flac.Picture()

    with open(album_art_path, "rb") as pic:
        p.data = pic.read()

    meta.add_picture(p)

    meta.save()


def add_metadata_m4a(file_name: str, song: SpotifySong, album_art_path: str):
    """
    Adds metadata to an M4A file given it's path.
    File name must contain file extension as well.
    """

    meta = mutagen.mp4.MP4(file_name)

    # refer https://stackoverflow.com/questions/56660170/\problem-using-mutagen-to-set-custom-tags-for-mp4-file

    meta["\xa9nam"] = song.name
    meta['\xa9ART'] = "/".join(song.artists)
    meta["\xa9alb"] = song.album_name

    # now, to write the album art
    with open(album_art_path, "rb") as pic:
        meta["covr"] = [mutagen.mp4.MP4Cover(pic.read(),
        imageformat=mutagen.mp4.MP4Cover.FORMAT_JPEG)]

    meta.save(file_name)



def controller(file_name: str, song: SpotifySong, dir: str, codec: str):
    """
    Handles the metadata writing process flow.
    """

    album_art_path = download_album_art(
        path=dir, link=song.cover_url, title=song.album_name
    )

    print("\nWriting metadata...")

    match codec:
        case "flac":
            add_metadata_flac(file_name, song, album_art_path)

        case "mp3":
            add_metadata_mp3(file_name, song, album_art_path)

        case "m4a":
            add_metadata_m4a(file_name, song, album_art_path)

    print("\nFinished writing metadata!")


# if __name__ == "__main__":
# add_cover(file_path="./yASD-dl/Rauw Alejandro, Tainy - ¿Cuándo Fue#")
