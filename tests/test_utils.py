import pytest
from dotenv.main import load_dotenv

import os
import platform
import subprocess

import spotidl.utils as package
import spotidl.config as config

load_dotenv()


def test_check_env_vars():
    # here, if the check_env_vars function runs without any problems
    # , then that means that all env vars have a value
    assert package.check_env_vars() is None


@pytest.fixture()
def make_test_dir(tmp_path):
    d = tmp_path / "test"
    d.mkdir()

    return d


@pytest.fixture()
def make_test_file(make_test_dir):
    d = make_test_dir
    f = d / "test.txt"
    f.write_text("testing")
    return f


def test_make_dir(make_test_dir):
    # make_dir returns True if dir exists or it creates a dir successfully
    assert package.make_dir(make_test_dir)
    assert package.make_dir(make_test_dir)


def test_check_dir(make_test_dir):
    assert package.check_dir(make_test_dir)


def test_check_file(make_test_file):
    assert package.check_file(make_test_file)


def test_directory_maker(capsys, tmp_path):
    dir_path = tmp_path / "test"
    package.directory_maker(dir_path)

    # capsys.readouterr() captures print statements and has to be used just
    # after the function call
    captured = capsys.readouterr()
    expected_output = "Successfully created 'test' directory.\n"

    assert captured.out == expected_output


@pytest.fixture()
def get_song_link():
    return "https://open.spotify.com/track/4kgNvCA8bcbeMozbGHDULB?\
si=35aba232e6c344ef"


@pytest.fixture()
def get_album_link():
    return "https://open.spotify.com/album/74EvGqq3t8JFRwscYjUI13?\
si=_W4OW5HsT96EPfjO6IwJBg"


@pytest.fixture()
def get_playlist_link():
    return "https://open.spotify.com/playlist/5Uf0UoZMAsKBSMe3QNBFBz?\
si=5465fbd51d5640d8"


def test_check_spotify_link(get_song_link):
    # we will need to pass on the regex patterns list ourselves
    assert not package.check_spotify_link(
        link="", patterns_list=config.spotify_link_patterns
    )

    assert package.check_spotify_link(
        link=get_song_link,
        patterns_list=config.spotify_link_patterns,
    )


def test_make_song_title():
    artists = ["one", "two"]
    name = "song"
    delim = ", "
    expected_output = "one, two - song"

    assert package.make_song_title(artists, name, delim) == expected_output


def test_download_album_art(make_test_dir):
    album_art_url = "https://i.scdn.co/image/ab67616d0000b273c91030650cb3fdf8c\
75394f0"
    title = "test"
    path = str(make_test_dir)

    # album art images are stored in the "/album-art" folder
    expected_output = path + "/album-art/test.jpeg"

    assert (
        package.download_album_art(path=path, link=album_art_url, title=title)
        == expected_output
    )

    assert os.path.isfile(expected_output)


def test_check_cli_args(capsys, get_song_link):
    link = get_song_link

    # first testing with correct input
    assert package.check_cli_args("flac", "best", link)

    expected_output = "Invalid codec entered! Using default value.\n"
    package.check_cli_args("wrong_input", "320", link)
    captured = capsys.readouterr()

    assert captured.out == expected_output

    expected_output = "Invalid bitrate entered! Using default value.\n"
    package.check_cli_args("mp3", "wrong_input", link)
    captured = capsys.readouterr()

    assert captured.out == expected_output


def test_get_link_type(get_song_link, get_album_link, get_playlist_link):
    assert package.get_link_type(get_song_link) == "track"

    assert package.get_link_type(get_album_link) == "album"

    assert package.get_link_type(get_playlist_link) == "playlist"


def test_correct_name():
    query = "/\\<>"

    assert package.correct_name(query) == "####"


def test_get_playlist_id(get_playlist_link):
    assert package.get_playlist_id(get_playlist_link) == "5Uf0UoZMAsKBSMe3QNBFBz"


def test_check_ffmpeg_installed():
    # we will have to check this here ourselves to be able to assert
    # since ffmpeg is a package which may or may not be on the user's system
    os_platform = platform.system()
    check = package.check_ffmpeg_installed()

    try:
        if os_platform == "Windows":
            subprocess.check_output(["where", "ffmpeg"])

        subprocess.check_output(["which", "ffmpeg"])

    except Exception:
        assert not check

    assert check
