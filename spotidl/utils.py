import os
import subprocess
import platform
import pathlib
import logging


from spotidl import exceptions


default_save_dir = os.getcwd() + "/dl"


def initialize_logger():
    home_dir = os.path.expanduser("~")
    log_path = pathlib.Path(home_dir).joinpath("spotidl.log")

    datetime_format = "%m/%d/%Y %I:%M:%S %p"
    log_format = "%(asctime)s | %(levelname)s: %(message)s"

    logging.basicConfig(filename=log_path, level=logging.WARN, format=log_format, datefmt=datetime_format)


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


def check_env_vars(env_vars: dict):
    """
    Run a barebones check to ensure that the three needed environment variables
    are not blank.
    """

    if not env_vars["id"]:
        raise exceptions.EnvVariablesError("SPOTIPY_CLIENT_ID not configured!")

    if not env_vars["secret"]:
        raise exceptions.EnvVariablesError("SPOTIPY_CLIENT_SECRET not configured!")

    if not env_vars["redirect_uri"]:
        raise exceptions.EnvVariablesError("SPOTIPY_REDIRECT_URI not configured!")


def check_ffmpeg_installed() -> bool:
    """
    Checks whether FFmpeg is installed or not.
    """

    os_platform = platform.system()

    try:
        if os_platform == "Windows":
            subprocess.check_call(["where", "ffmpeg"])
        else:
            subprocess.check_call(["which", "ffmpeg"])

    # occurs if the commands are run on the wrong platforms
    except FileNotFoundError:
        return False
    return True
