from spotipy import Spotify
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

from dataclasses import dataclass
from exceptions import NoDataReceivedError


# initializing the spotify api connection
# the OAuth object automatically reads valid env. variables
sp = Spotify(auth_manager=SpotifyOAuth())

# defining structure for the song data we are going to be parsing
@dataclass
class SpotifySong:
    name: str
    artists: list
    album_art_url: str

    def __repr__(self):
        return f"{', '.join(self.artists)}- {self.name}"


def get_song_data(link: str) -> SpotifySong:
    """
    Get relevant song details for the given Spotify song link.
    The link can be be a URL, URI or even a Spotify song ID.
    """

    try:
        song_details = sp.track(link)

    except SpotifyException as e:
        # wrapping the Spotify Exception
        # still unsure whether this is the correct approach
        raise NoDataReceivedError(e)

    else:
        # there can be multiple results,
        # iterating over the list and extracting data
        artists = []
        for artist in song_details["artists"]:
            artists.append(artist["name"])

        song = SpotifySong(
            song_details["name"],
            artists,
            # typically the 1st link contains a link to the album art
            # of size 640 x 640 pixels
            song_details["album"]["images"][0]["url"],
        )

        return song


if __name__ == "__main__":
    pass
