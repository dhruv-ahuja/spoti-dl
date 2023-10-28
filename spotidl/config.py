audio_bitrates = ["best", "320", "256", "192", "128", "96", "32", "worst"]
audio_formats = ["mp3", "flac", "m4a", "opus"]

ENV_VARS_ERROR = "Environment variables not properly configured! Please configure SPOTIPY_CLIENT_ID,\
 SPOTIPY_CLIENT_SECRET and SPOTIPY_REDIRECT_URI environment variables."

# * logger default config
LOG_FILE = "spotidl.log"
LOG_DATETIME_FORMAT = "%d/%m/%Y %I:%M:%S %p"
LOG_MESSAGE_FORMAT = "%(asctime)s | %(levelname)s: %(message)s"

# * text color ANSI escape codes
RED_COLOR_CODE = "\033[91m"
RESET_COLOR_CODE = "\033[0m"
