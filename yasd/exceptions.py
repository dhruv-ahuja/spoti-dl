# contains the custom exceptions to be used when attempting to enforce
# certain aspects in the application


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
