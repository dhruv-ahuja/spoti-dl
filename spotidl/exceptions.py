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
