from importlib import metadata

__version__ = metadata.version("spoti-dl")

del metadata  # optional, to avoid polluting the results of dir(__package__)
