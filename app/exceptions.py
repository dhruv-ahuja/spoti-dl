# contains the custom exceptions to be used when attempting to enforce
# certain aspects in the application


class LinkError(Exception):
    """
    Exception raised when the provided link is incorrect.
    """

    # spits out whatever error message is passed to it
    pass
