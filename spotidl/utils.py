import os
import subprocess
import platform
import pathlib
import logging


default_save_dir = os.getcwd() + "/dl"


def initialize_logger(log_file: str, msg_format: str, datetime_format: str, log_level: int):
    """
    Initializes an app-wide logger, for use in the Rust code, with the given configuration values.
    """

    home_dir = os.path.expanduser("~")
    log_path = pathlib.Path(home_dir).joinpath(log_file)

    logging.basicConfig(filename=log_path, level=log_level, format=msg_format, datefmt=datetime_format)


def load_env_vars() -> dict:
    """
    Loads the environment variables into a dictionary.
    """

    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

    env_vars = {
        "id": client_id,
        "secret": client_secret,
        "redirect_uri": redirect_uri,
    }

    return env_vars


def check_env_vars(env_vars: dict) -> bool:
    """
    Run a barebones check to ensure that the three needed environment variables
    are not blank.
    """

    return all([env_vars.get("id"), env_vars.get("secret"), env_vars.get("redirect_uri")])


def check_ffmpeg_installed() -> bool:
    """
    Checks whether FFmpeg is installed or not.
    """

    os_platform = platform.system()
    command = "where" if os_platform == "Windows" else "which"

    try:
        output = subprocess.run([command, "ffmpeg"], stdout=subprocess.PIPE)
        return output.returncode == 0

    except Exception:
        return False
