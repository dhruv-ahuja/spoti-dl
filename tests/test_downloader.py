import os


from yt_dlp import YoutubeDL
import pytest


import spotidl.downloader as package
from tests.test_spotify import generate_new_song as spotify_song


@pytest.fixture()
def generate_config():
    """
    Generates the config needed to test the YoutubeDL object.
    """

    downloader_params = {
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }
        ],
        "outtmpl": "Juliette - Le sort de Circé.%(ext)s",
        "quiet": True,
        "format": "bestaudio/best",
        "dynamic_mpd": False,
        "noplaylist": True,
        "prefer_ffmpeg": True,
    }

    yield downloader_params
    del downloader_params


def test_get_config(spotify_song, generate_config):
    """
    Tests to ensure that the config for the YoutubeDL object is generated
    correctly.
    """

    song = spotify_song
    user_params = {"quiet": True, "codec": "mp3", "quality": "320"}

    expected_output = generate_config

    assert package.get_config(user_params=user_params, song=song) == expected_output


def test_get_downloader(generate_config):
    """
    Tests the creation of the download object.
    """

    params = generate_config

    assert isinstance(package.get_downloader(params), YoutubeDL)


@pytest.fixture()
def generate_downloader(generate_config):
    """
    Generates the YoutubeDL object to be used for further testing.
    """

    # we have hard coded one particular song name in the config just for
    # testing; we keep the name dynamic in the actual app
    return YoutubeDL(generate_config)


@pytest.fixture()
def generate_yt_song():
    """
    Generates a valid YoutubeSong object to be used for testing.
    """

    song_id = "pkB9fm08IDM"
    song_title = "Le sort de Circé"
    audio_source_url = "https://www.youtube.com/watch?v=pkB9fm08IDM"

    song = package.YoutubeSong(song_id, song_title, audio_source_url)

    yield song
    del song


def test_fetch_source(generate_downloader, generate_yt_song, spotify_song):
    # need these objects for the actual function that we're testing
    song = spotify_song
    ytd = generate_downloader

    expected_output = generate_yt_song

    assert package.fetch_source(ytd, song) == expected_output


@pytest.fixture()
def make_test_dir(tmp_path):
    """
    Creates a mock test directory.
    """

    directory = tmp_path / "test"
    directory.mkdir()

    # yielding the directory and then regaining control when function execution
    # ends will enable to us to remove it from the memory
    yield directory
    del directory


@pytest.fixture()
def make_test_song(make_test_dir):
    """
    Creates a mock song file.
    """

    def make_song(codec: str = "mp3"):
        song_file = make_test_dir / f"artist - unknown.{codec}"
        song_file.write_text("testing")

        return song_file

    yield make_song
    del make_song


def test_download_song(make_test_song):
    """
    Mocks the behaviour of the download_song function.
    """

    # mocking the behaviour of the downloader function
    downloaded_song = make_test_song()

    assert os.path.isfile(downloaded_song)
