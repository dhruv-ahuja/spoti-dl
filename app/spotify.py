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
    album_name: str
    disc_number: int
    track_number: int
    cover_url: str


def get_song_data(link: str) -> SpotifySong:
    """
    Get relevant song details for the given Spotify song link.
    The link can be be a URL or URI.
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
            name=song_details["name"],
            artists=artists,
            album_name=song_details["album"]["name"],
            disc_number=song_details["disc_number"],
            track_number=song_details["track_number"],
            # typically the 1st link contains a link to the album art
            # of size 640 x 640 pixels
            cover_url=song_details["album"]["images"][0]["url"],
        )

        return song


def parse_album(link: str) -> list[SpotifySong]:
    pass


if __name__ == "__main__":

    song = get_song_data(
        "https://open.spotify.com/track/0Ey8buiWgtBQjb7ypaACKN?si=22882b3a21ae4c71"
    )
    print(song.__repr__())
