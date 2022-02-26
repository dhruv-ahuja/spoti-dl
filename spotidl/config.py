# will contain all config options with multiple choices available;
# modifiable by command line arguments

# adding everything availble in the yt_dlp docs though i highly doubt
# anyone would want to download songs at anything below 128kbps
audio_bitrates = ["best", "320", "256", "192", "128", "96", "32", "worst"]

audio_formats = ["mp3", "flac"]

spotify_link_types = ["track", "album", "playlist"]


# regex patterns for spotify URLs stored according to the url type
spotify_link_patterns = {
    "track": [
        # checks for the track URL w/o the https
        r"^(spotify:|[a-z]+\.spotify\.com/track/)",
        # checks for the track URL w/ the https
        r"^(spotify:|https://[a-z]+\.spotify\.com/track/)",
    ],
    "album": [
        # checks for the album URL w/o the https
        r"^(spotify:|[a-z]+\.spotify\.com/album/)",
        # checks for the album URL w/ the https
        r"^(spotify:|https://[a-z]+\.spotify\.com/album/)",
    ],
    "playlist": [
        # checks for the playlist URL w/o the https
        r"^(spotify:|[a-z]+\.spotify\.com/playlist/)"
        # checks for the playlist URL w/ the https
        r"^(spotify:|https://[a-z]+\.spotify\.com/playlist/)",
    ],
}

# list of illegal file name characters; replace them in case any of these
# is in the song name
illegal_chars = ["?", ">", "<", "|", ":", "/", "\\", "*"]
