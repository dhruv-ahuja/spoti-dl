# contains the custom exceptions to be used when attempting to enforce
# certain aspects in the application


class AppError(Exception):
    def __init__(
        self, err_msg="An error occured during the exeuction of the application!"
    ):
        self.err_msg = err_msg
        super().__init__(self.err_msg)


class IncorrectSpotifyLinkError(AppError):
    def __init__(self, err_msg: str):
        self.err_msg = err_msg
        super().__init__(self.err_msg)
