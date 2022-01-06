import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

from spotify import SpotifySong


def add_metadata(path: str, song: SpotifySong):
    """
    Adds metadata to a song given it's path.
    Path must contain file extension as well.
    """
    try:
        print("Adding metadata...")
        meta = EasyID3(path)

    except ID3NoHeaderError:
        meta = mutagen.File(path, easy=True)
        meta.add_tags()

    meta["title"] = song.name
    meta["artist"] = "/".join(song.artists)
    meta["album"] = song.album_name
    meta["tracknumber"] = str(song.track_number)
    meta["discnumber"] = str(song.disc_number)

    meta.save(v1=2, v2_version=3)
    print("Successfully wrote metadata!")


if __name__ == "__main__":
    path = "./yASD-dl/DjRUM-Sparrows.mp3"
    add_metadata(path)
