# will contain all config options with multiple choices available;
# modifiable by command line arguments

# adding everything availble in the yt_dlp docs though i highly doubt
# anyone would want to download songs at anything below 128kbps
audio_bitrates = ["best", "320", "256", "192", "128", "96", "32", "worst"]

audio_formats = ["mp3", "flac", "m4a"]

spotify_link_types = ["track", "album", "playlist"]


# regex patterns for spotify URLs stored according to the url type
spotify_link_patterns = {
    "track": [
        r"^(spotify:|[a-z]+\.spotify\.com/track/)",
        r"^(spotify:|https://[a-z]+\.spotify\.com/track/)",
    ],
    "album": [
        r"^(spotify:|[a-z]+\.spotify\.com/album/)",
        r"^(spotify:|https://[a-z]+\.spotify\.com/album/)",
    ],
    # playlist will be implemented soon!
    "playlist": [
        r"^(spotify:|[a-z]+\.spotify\.com/playlist/)"
        r"^(spotify:|https://[a-z]+\.spotify\.com/playlist/)",
    ],
}

# list of illegal file name characters; replace them in case any of these
# is in the song name
illegal_chars = ["?", ">", "<", "|", ":", "/", "\\", "*"]


if __name__ == "__main__":
    from exceptions import *

    print("ok")
