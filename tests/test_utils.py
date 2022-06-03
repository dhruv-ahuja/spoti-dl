import os
import platform
import subprocess

import pytest

from spotidl import config, exceptions
from spotidl import utils as package


@pytest.fixture()
def env_vars():
    """
    Generates mock environment variables to be used for testing certain helper
    functions.
    """

    def make_vars(id_: str = "foo", secret: str = "bar", uri: str = "baz") -> dict:
        mock_vars = {
            "id": id_,
            "secret": secret,
            "redirect_uri": uri,
        }

        return mock_vars

    # by returning a function, we'll have the freedom to modify the dictionary
    # according to our needs by defining the function parameters
    return make_vars


def test_valid_env_vars(env_vars):
    """
    Verifies whether the environment variable-checker function is working as
    intended, by feeding it non-empty data.
    """

    # here, if the check_env_vars function runs without any problems then that
    # means that all env vars have a value and that should be the case since
    # we're feeding it the mock env_vars dictionary by calling the fixture
    assert package.check_env_vars(env_vars()) is None

    # removing env_vars dict from the memory
    del env_vars


def test_invalid_env_vars(env_vars):
    """
    Verifies whether the environment variable-checker function raises the
    apt Exception when given empty data.
    """
    mock_env_vars = env_vars(id_="")
    err_invalid_id = "SPOTIPY_CLIENT_ID not configured!"

    with pytest.raises(exceptions.EnvVariablesError) as exc:
        package.check_env_vars(mock_env_vars)

    assert exc.value.message == err_invalid_id

    mock_env_vars = env_vars(secret="")
    err_invalid_secret = "SPOTIPY_CLIENT_SECRET not configured!"

    with pytest.raises(exceptions.EnvVariablesError) as exc:
        package.check_env_vars(mock_env_vars)

    assert exc.value.message == err_invalid_secret

    mock_env_vars = env_vars(uri="")
    err_invalid_uri = "SPOTIPY_REDIRECT_URI not configured!"

    with pytest.raises(exceptions.EnvVariablesError) as exc:
        package.check_env_vars(mock_env_vars)

    assert exc.value.message == err_invalid_uri

    # removing env_vars dict from the memory
    del env_vars


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
def make_test_file(make_test_dir):
    """
    Creates a mock test file.
    """

    directory = make_test_dir
    file_ = directory / "test.txt"
    # I believe writing some data to the file is necessary for its existence to
    # be recognized by the os library's functions.
    file_.write_text("testing")

    # yielding the file and then regaining control when function execution ends
    # will enable to us to remove it from the memory
    yield file_
    del file_


def test_make_invalid_dir(capsys):
    """
    Tests the directory maker function by raising an Exception and verifiying
    the output.
    """

    err_making_dir = "Error when attempting to make directory: "

    # set the exception to be underscore since checking for OSError with a
    # direct comparison is much harder than what we're doing here
    with pytest.raises(OSError) as _:
        res = package.make_dir("")
        # capturing the error message in its entirety with this
        captured = capsys.readouterr()

        raise OSError

    assert captured.out == f"{err_making_dir} [Errno 2] No such file or directory: ''\n"
    # assert not res since we should be getting a False return value
    assert not res


def test_make_dir(make_test_dir):
    """
    Tests the directory-creator helper function.
    """

    # make_dir returns True if dir exists or it creates a dir successfully
    dir_to_make = f"{make_test_dir}/1234/"
    assert package.make_dir(dir_to_make)


def test_check_dir_invalid(make_test_dir):
    """
    Tests the directory checker function with an invalid directory.
    """

    non_existent_dir = f"{make_test_dir}/1234/"
    assert not package.check_dir(non_existent_dir)


def test_check_dir(make_test_dir):
    """
    Tests the directory checker function with a valid directory.
    """

    assert package.check_dir(make_test_dir)


def test_check_file_invalid(make_test_dir):
    """
    Tests the file checker function with an invalid file.
    """

    non_existent_file = f"{make_test_dir}/blabla.txt"
    assert not package.check_file(non_existent_file)


def test_check_file(make_test_file):
    """
    Tests the file checker function with a valid file.
    """

    assert package.check_file(make_test_file)


def test_directory_maker(capsys, tmp_path):
    """
    Tests the directory maker function.
    """

    dir_path = tmp_path / "test"
    package.directory_maker(dir_path)

    # capsys.readouterr() captures print statements and has to be used just
    # after the function call
    captured = capsys.readouterr()
    expected_output = "Successfully created 'test' directory.\n"

    assert captured.out == expected_output


@pytest.fixture()
def get_song_link():
    """
    Returns a valid Spotify song link to be used when testing functions that
    require it.
    """

    song = "https://open.spotify.com/track/4kgNvCA8bcbeMozbGHDULB?\
si=35aba232e6c344ef"

    yield song
    del song


@pytest.fixture()
def get_album_link():
    """
    Returns a valid Spotify album link to be used when testing functions that
    require it.
    """

    album = "https://open.spotify.com/album/74EvGqq3t8JFRwscYjUI13?\
si=_W4OW5HsT96EPfjO6IwJBg"

    yield album
    del album


@pytest.fixture()
def get_playlist_link():
    """
    Returns a valid Spotify playlist link to be used when testing functions that
    require it.
    """

    playlist = "https://open.spotify.com/playlist/5Uf0UoZMAsKBSMe3QNBFBz?\
si=5465fbd51d5640d8"

    yield playlist
    del playlist


def test_check_spotify_link(get_song_link):
    """
    Tests the Spotify link checker function.
    """

    # we will need to pass on the regex patterns list ourselves
    assert not package.check_spotify_link(
        link="", patterns_list=config.spotify_link_patterns
    )

    assert package.check_spotify_link(
        link=get_song_link,
        patterns_list=config.spotify_link_patterns,
    )


def test_make_song_title():
    """
    Tests the song maker function.
    """

    artists = ["one", "two"]
    name = "song"
    delim = ", "
    expected_output = "one, two - song"

    assert package.make_song_title(artists, name, delim) == expected_output


def test_download_album_art_empty():
    """
    Tests the album art downloader function but feeds it an empty link.
    """

    assert package.download_album_art(path=".", link="", title="") == ""


def test_download_album_art(make_test_dir):
    """
    Tests the album art downloader function.
    """

    album_art_url = "https://i.scdn.co/image/ab67616d0000b273c91030650cb3fdf8c\
75394f0"
    title = "test"
    path = str(make_test_dir)

    # album art images are stored in the "/album-art" folder
    expected_output = f"{path}/album-art/test.jpeg"

    assert (
        package.download_album_art(path=path, link=album_art_url, title=title)
        == expected_output
    )

    assert os.path.isfile(expected_output)


def test_check_cli_wrong_args(capsys, get_song_link):
    """
    Tests the CLI arguments verifier function with a variety of different
    incorrect arguments.
    """

    link = get_song_link

    # testing the response to invalid codec argument
    expected_output = "Invalid codec entered! Using default value.\n"
    package.check_cli_args("wrong_input", "320", link)
    captured = capsys.readouterr()

    assert captured.out == expected_output

    # testing the response to invalid bitrate argument
    expected_output = "Invalid bitrate entered! Using default value.\n"
    package.check_cli_args("mp3", "wrong_input", link)
    captured = capsys.readouterr()

    assert captured.out == expected_output


def test_check_cli_empty_link():
    """
    Tests the CLI arguments verifier function with an empty link.
    """

    err_empty_link = "Spotify link needed to proceed!"
    with pytest.raises(exceptions.LinkError) as exc:
        package.check_cli_args("flac", "best", "")

    assert exc.value.message == err_empty_link


def test_check_cli_args(get_song_link):
    """
    Tests the CLI arguments verifier function with a variety of different
    correct arguments.
    """

    link = get_song_link

    assert package.check_cli_args("flac", "best", link)
    assert package.check_cli_args("flac", "32", link)
    assert package.check_cli_args("mp3", "worst", link)
    assert package.check_cli_args("mp3", "256", link)


def test_get_link_type(get_song_link, get_album_link, get_playlist_link):
    """
    Tests the link getter function.
    """

    assert package.get_link_type(get_song_link) == "track"

    assert package.get_link_type(get_album_link) == "album"

    assert package.get_link_type(get_playlist_link) == "playlist"


def test_correct_name():
    """
    Tests the songs' name checker function.
    """

    query = "/\\<>"

    assert package.correct_name(query) == "####"


def test_get_playlist_id(get_playlist_link):
    """
    Tests the playlist ID getter function.
    """

    assert package.get_playlist_id(get_playlist_link) == "5Uf0UoZMAsKBSMe3QNBFBz"


def test_check_ffmpeg_installed():
    """
    Tests the function that checks for the existence of ffmpeg in the system.
    """

    # we will have to check this here ourselves to be able to assert
    # since ffmpeg is a package which may or may not be on the user's system
    os_platform = platform.system()
    check = package.check_ffmpeg_installed()

    try:
        if os_platform == "Windows":
            subprocess.check_output(["where", "ffmpeg"])
        else:
            subprocess.check_output(["which", "ffmpeg"])

    except FileNotFoundError:
        assert not check

    assert check
