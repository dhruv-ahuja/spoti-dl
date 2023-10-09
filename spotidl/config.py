# will contain all config options with multiple choices available;
# modifiable by command line arguments

# adding everything availble in the yt_dlp docs though i highly doubt
# anyone would want to download songs at anything below 128kbps
audio_bitrates = ["best", "320", "256", "192", "128", "96", "32", "worst"]

audio_formats = ["mp3", "flac", "m4a", "opus"]

spotify_link_types = ["track", "album", "playlist"]


spotify_link_pattern = r"/(track|playlist|album|episode)/([^?/]+)"

# list of illegal file name characters; replace them in case any of these
# is in the song name
illegal_chars = {"?", ">", "<", "|", ":", "/", "\\", "*"}


ENV_VARS_ERROR = "Environment variables not properly configured! Please configure SPOTIPY_CLIENT_ID,\
 SPOTIPY_CLIENT_SECRET and SPOTIPY_REDIRECT_URI environment variables."
