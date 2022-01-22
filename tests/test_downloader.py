from yt_dlp import YoutubeDL
import pytest

import os

import spotidl.downloader as package
from tests.test_spotify import generate_new_song


@pytest.fixture()
def generate_config():
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
    }

    return downloader_params


def test_get_config(generate_new_song, generate_config):
    song = generate_new_song
    user_params = {"quiet": True, "codec": "mp3", "quality": "320"}

    expected_output = generate_config

    assert package.get_config(user_params=user_params, song=song) == expected_output


def test_get_downloader(generate_config):
    params = generate_config

    assert isinstance(package.get_downloader(params), YoutubeDL)


@pytest.fixture()
def generate_downloader(generate_config):
    # we have hard coded one particular name in the config just for testing,
    # we keep the name dynamic in the actual app
    return YoutubeDL(generate_config)


@pytest.fixture()
def generate_yt_song(generate_downloader):
    yt = generate_downloader

    def make_yt_song(song_title: str):
        search = yt.extract_info(f"ytsearch: {song_title}", download=False)
        yt_info = search["entries"][0]

        yt_song = package.YoutubeSong(
            id=yt_info["id"],
            title=yt_info["title"],
            video_url=yt_info["webpage_url"],
        )

        return yt_song

    return make_yt_song


def test_fetch_source(generate_downloader, generate_yt_song, generate_new_song):
    song = generate_new_song
    song_title = "Juliette - Le sort de Circé audio"
    yt = generate_downloader
    expected_output = generate_yt_song(song_title)

    assert package.fetch_source(yt, song) == expected_output


@pytest.fixture()
def make_test_dir(tmp_path):
    d = tmp_path / "test"
    d.mkdir()

    return d


def test_download_song(generate_downloader, generate_yt_song):
    yt = generate_downloader
    song_title = "Juliette - Le sort de Circé"
    yt_song = generate_yt_song(song_title)

    try:
        package.download_song(yt, yt_song.video_url)

    except Exception:
        assert not os.path.isfile(f"./{song_title}.mp3")

    else:

        assert os.path.isfile(f"./{song_title}.mp3")


def test_controller_mp3(generate_new_song, capsys):
    song = generate_new_song
    file_name = "Juliette - Le sort de Circé.mp3"
    user_params = {"codec": "mp3", "quality": "320", "quiet": True}

    # since we already downloaded the song in the previous test, we will first get to test the first part of the controller
    expected_output = f"\n{file_name} already exists! Skipping download...\n"

    # changing directory to the app's default downloads folder
    os.makedirs("./dl", exist_ok=True)
    os.chdir("./dl")
    package.controller(user_params, song, file_name)
    captured = capsys.readouterr()

    assert captured.out == expected_output

    # now testing the else statement part
    os.remove(f"./{file_name}")

    package.controller(user_params, song, file_name)

    assert os.path.isfile(f"./{file_name}")

    os.chdir("..")


def test_controller_flac(generate_new_song):
    song = generate_new_song
    file_name = "Juliette - Le sort de Circé.flac"
    user_params = {"codec": "flac", "quality": "320", "quiet": True}

    # changing directory to the app's default downloads folder
    os.makedirs("./dl", exist_ok=True)
    os.chdir("./dl")
    package.controller(user_params, song, file_name)

    # now testing the else statement part
    os.remove(f"./{file_name}")

    package.controller(user_params, song, file_name)

    assert os.path.isfile(f"./{file_name}")

    os.chdir("..")
