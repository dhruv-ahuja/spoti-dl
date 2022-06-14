from typing import List

import pytest
import spotipy

import spotidl.spotify as package


exceptions = package.exceptions


@pytest.fixture()
def sp():
    return package.sp


def test_sp(sp):
    assert isinstance(sp, spotipy.Spotify)


@pytest.fixture()
def generate_song_data():
    def make_song(name: str):
        """
        Helper function that makes a SpotifySong object for the given name.
        """

        if name == "gotye-somebody that I used to know":
            song = package.SpotifySong(
                name="Somebody That I Used To Know",
                artists=["Gotye", "Kimbra"],
                album_name="Making Mirrors",
                disc_number=1,
                track_number=3,
                cover_url="https://i.scdn.co/image/ab67616d0000b2738ac5768205ad\
97df3f4f4c0e",
            )

        elif name == "santiago-colourblind":
            song = package.SpotifySong(
                name="Colourblind",
                artists=["Santiago"],
                disc_number=1,
                track_number=1,
                album_name="Colourblind",
                cover_url="https://i.scdn.co/image/ab67616d0000b273650b3094e\
d2b0b758777f081",
            )

        return song

    # we return the function so that we can re-use the fixture for different
    # inputs
    return make_song


def test_get_song_data(generate_song_data, capsys):
    expected_output = generate_song_data

    actual_output = package.get_song_data(
        "https://open.spotify.com/track/1qDrWA6lyx8cLECdZE7TV7?si=\
b1b87827cc604d0a"
    )

    assert actual_output == expected_output("gotye-somebody that I used to know")

    actual_output = package.get_song_data(
        "https://open.spotify.com/track/67tMk3x5UwaPc6ATevv9BN?si=\
3877bdc40b0d4a97"
    )

    assert actual_output == expected_output("santiago-colourblind")

    # now, to check whether the string formatting is correct
    # (when printing the SpotifySong object)
    expected_string = "Santiago - Colourblind"

    assert str(actual_output) == expected_string


@pytest.fixture()
def generate_new_song():
    song = package.SpotifySong(
        name="Le sort de Circé",
        artists=["Juliette"],
        album_name="Mutatis mutandis",
        disc_number=1,
        track_number=1,
        cover_url="https://i.scdn.co/image/ab67616d0000b273e5c8d59f7\
f75f7d2e25022a6",
    )

    return song


def test_new_song(generate_new_song):
    # get_song_data that we tested before relies on this function
    expected_output = generate_new_song

    query_song = {
        "name": "Le sort de Circé",
        "artists": [{"name": "Juliette"}],
        "album": {
            "name": "Mutatis mutandis",
            "images": [
                {
                    "url": "https://i.scdn.co/image/ab67616d0000b273e5c8d59f\
7f75f7d2e25022a6"
                }
            ],
        },
        "track_number": 1,
        "disc_number": 1,
    }

    query_album = {
        "name": "Le sort de Circé",
        "artists": [{"name": "Juliette"}],
        "album": {"name": "Mutatis mutandis"},
        "track_number": 1,
        "disc_number": 1,
    }

    album_name = "Mutatis mutandis"
    album_cover_url = "https://i.scdn.co/image/ab67616d0000b273e5c8d59f\
7f75f7d2e25022a6"

    assert package.new_song(query_song, "song") == expected_output

    assert (
        package.new_song(
            query_album, "album", album_name=album_name, album_cover_url=album_cover_url
        )
        == expected_output
    )


@pytest.fixture()
def generate_new_album_data():
    album: List[package.SpotifySong] = []

    song = package.SpotifySong(
        name="Twilight (OAKK Remix)",
        artists=["An-Ten-Nae", "Morillo", "OAKK"],
        album_name="Twilight (Oakk Remix)",
        track_number=1,
        disc_number=1,
        cover_url="https://i.scdn.co/image/ab67616d0000b273c91030650cb3fdf8c\
75394f0",
    )

    album.append(song)

    return song.album_name, album


def test_get_album_data(generate_new_album_data):
    assert (
        package.get_album_data(
            "https://open.spotify.com/album/\
5tGwVgsAWcUv9Pml0cNqQZ?si=foGyKSZgQJOR_wbpeu_sZg"
        )
        == generate_new_album_data
    )


@pytest.fixture()
def generate_new_playlist_data():
    playlist: list[package.SpotifySong] = []
    song = package.SpotifySong(
        name="Twilight (OAKK Remix)",
        artists=["An-Ten-Nae", "Morillo", "OAKK"],
        album_name="Twilight (Oakk Remix)",
        track_number=1,
        disc_number=1,
        cover_url="https://i.scdn.co/image/ab67616d0000b273c91030650cb3fdf8c\
75394f0",
    )
    playlist.append(song)

    return "app-test", playlist


def test_get_playlist_data(generate_new_playlist_data):
    assert (
        package.get_playlist_data(
            "https://open.spotify.com/playlist/\
5Uf0UoZMAsKBSMe3QNBFBz?si=a145a657f12341ac"
        )
        == generate_new_playlist_data
    )


# will raise the given exception for us
# def failer(e: Exception):
#     raise e


# now to check for the exceptions:
def test_get_song_data_fail():
    e = exceptions.NoDataReceivedError

    with pytest.raises(e):
        package.get_song_data(
            "https://open.spotify.com/album/3ngcrybWz1fUix\
AjS1ggl3?si=7bb836740b7d4963"
        )


def test_get_playlist_data_fail():
    e = exceptions.NoDataReceivedError

    with pytest.raises(e):
        package.get_playlist_data(
            "https://open.spotify.com/album/3ngcrybWz1fUix\
AjS1ggl3?si=7bb836740b7d4963"
        )
