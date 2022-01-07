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
    Gets relevant song details for the given Spotify song link.
    These are then passed onto other functions for further processing.
    """

    try:
        query = sp.track(link)

    except SpotifyException as e:
        # wrapping the Spotify Exception
        # still unsure whether this is the correct approach
        raise NoDataReceivedError(e)

    else:
        # there can be multiple results,
        # iterating over the list and extracting data
        artists = []
        for artist in query["artists"]:
            artists.append(artist["name"])

        song = SpotifySong(
            name=query["name"],
            artists=artists,
            album_name=query["album"]["name"],
            disc_number=query["disc_number"],
            track_number=query["track_number"],
            # typically the 1st link contains a link to the album art
            # of size 640 x 640 pixels
            cover_url=query["album"]["images"][0]["url"],
        )

        return song


def new_song(query: dict, type: str, album_name = None) -> SpotifySong:
    """
    Makes a new SpotifySong given a raw "track" type item received from Spotify API.
    The track queried using different methods returns slightly modified data.
    """

    artists = []
    for artist in query["artists"]:
        artists.append(artist)

    match type:
        # "song" refers to the case where the user enters a song link; we need
        # to fetch data for just a single song 
        case "song":
            song = SpotifySong(
            name=query["name"],
            artists=artists,
            album_name=query["album"]["name"],
            disc_number=query["disc_number"],
            track_number=query["track_number"],
            # typically the 1st link contains a link to the album art
            # of size 640 x 640 pixels
            cover_url=query["album"]["images"][0]["url"],
        )

        case "album":
            song = SpotifySong(
            name=query["name"],
            artists=artists,
            album_name=query["name"],
            disc_number=query["disc_number"],
            track_number=query["track_number"],
            cover_url=query["images"][0]["url"],
        )

    
    return song 


def get_album_data(link: str) -> list[SpotifySong]:
    """
    Gets album data for the given Spotify album link.
    It is then passed onto other functions for further processing.
    """

    # since our main data(all the relevant metadata, song URL) is associated
    # with the spotify song(referred to as "Track" in the spotify api), we
    # will need to make a list of all the songs in the album and then pass on
    # that list onto other functions.
    try:
        query = sp.album(link)

    except SpotifyException as e:
        NoDataReceivedError(e)

    album: list[SpotifySong] = []

    for track in query["tracks"]["items"]:
        # since this time we are directly receiving data that we otherwise
        # extracted from get_song_data using a link entered by the user, we
        # will need to generate a SpotifySong object another way
        artists = []
        for artist in track["artists"]:
            artists.append(artist["name"])

        song = new_song(track, album_name=query["name"])

        album.append(song)

    return album


if __name__ == "__main__":

    song = get_song_data(
        "https://open.spotify.com/track/0Ey8buiWgtBQjb7ypaACKN?si=22882b3a21ae4c71"
    )
    print(song.__repr__())

    album = get_album_data(
        "https://open.spotify.com/album/0bWYlK9rRmIB68icHx9PNR?si=0PRvNMbBSticZvfdCeGdjw"
    )
    print(album[0])
