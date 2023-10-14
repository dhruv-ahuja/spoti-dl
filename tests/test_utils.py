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
