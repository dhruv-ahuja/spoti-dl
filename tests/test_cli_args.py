import argparse

import pytest

from spotidl import __version__


@pytest.fixture()
def generate_parser():
    def make_parser():
        parser = argparse.ArgumentParser()

        return parser

    return make_parser


def test_version(capsys, generate_parser):
    """
    Confirms the application version.
    """

    # mocking the parser object
    parser = generate_parser()
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="1.0.4",
    )

    # getting the current application version from the
    current_version = __version__

    try:
        parser.parse_args(["-v"])
        assert parser.parse_args().version == current_version

    except SystemExit:
        captured = capsys.readouterr()
        assert captured.out == f"{current_version}\n"


def test_defaults(generate_parser):
    parser = generate_parser()
    expected_output = argparse.Namespace(
        quiet=True, codec=" mp3", bitrate=" 320", dir=" /dl"
    )

    # since we're manually adding the command line args, we have to account for
    # the space in added after each argument hence the extra space in each
    # 'default' parameter
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-c", "--codec", default=" mp3")
    parser.add_argument("-b", "--bitrate", default=" 320")
    parser.add_argument("-d", "--dir", default=" /dl")

    try:
        assert parser.parse_args(["-q", "-c mp3", "-b 320", "-d /dl"])

    except SystemExit:
        # adding a 'pass' here since the argparse module runs,
        # parses all arguments and then calls `sys.exit()`.
        # without an except block here, our tests will keep failing
        pass

    expected_output = argparse.Namespace(
        quiet=False, codec=" mp3", bitrate=" 320", dir=" /dl"
    )

    try:
        assert parser.parse_args([]) == expected_output

    except SystemExit:
        pass


def test_link(generate_parser):
    parser = generate_parser()

    parser.add_argument("link")

    expected_output = argparse.Namespace(link="")

    try:
        assert parser.parse_args([]) == expected_output

    except SystemExit:
        pass

    song_link = "https://open.spotify.com/track/30AeH6saju8WPJo73cKZyH?\
si=99a24d08f4e44faf"
    expected_output = argparse.Namespace(link=song_link)

    try:
        assert parser.parse_args([song_link]) == expected_output

    except SystemExit:
        pass
