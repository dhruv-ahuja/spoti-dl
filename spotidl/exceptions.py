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

    def __init__(self, message="Invalid Spotify link entered!"):
        self.message = message
        super().__init__(self.message)


class NoDataReceivedError(Exception):
    """
    Raised when no data received from the library service.
    """

    def __init__(self, message="No data received from the service."):
        self.message = message
        super().__init__(self.message)


class EnvVariablesError(Exception):
    """
    Raised when environment variables aren't configured.
    """

    def __init__(self, message="Environment variables aren't configured properly!"):
        self.message = message
        super().__init__(self.message)


class FFmpegNotInstalledError(Exception):
    """
    Raised when FFmpeg is not found in the user's PATH.
    """

    def __init__(self, message="FFMpeg is not installed!"):
        self.message = message
        super().__init__(self.message)
