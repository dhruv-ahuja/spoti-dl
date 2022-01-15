# contains the custom exceptions to be used when attempting to enforce
# certain aspects in the application

# not entering anything in the exceptions since all I want to do is to
# convey to the end user that something is wrong.
# a custom exception allows me to do that, with a related name and a custom
# description to explain the same in simple terms


class LinkError(Exception):
    """
    Raised when the provided link is incorrect.
    """

    # spits out whatever error message is passed to it
    pass


class NoDataReceivedError(Exception):
    """
    Raised when no data received from the external libraries.
    """

    pass


class EnvVariablesError(Exception):
    """
    Raised when environment variables aren't configured.
    """

    pass


class FFmpegNotInstalledError(Exception):
    """
    Raised when FFmpeg is not found in the user's PATH.
    """

    pass
