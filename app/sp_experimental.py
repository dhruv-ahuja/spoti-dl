from collections import namedtuple
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from typing import List


# define scopes for the api
scopes = ""
keys = []

# the SpotifyOAuth class automatically reads
# "SPOTIPY..." prefixed env variables for us
sp = Spotify(auth_manager=SpotifyOAuth())

album_details = sp.new_releases(country="IN", limit=2)
album_details = album_details["albums"]["items"]
# x = sp.album_tracks()
album_info = namedtuple("Song", ["name", "artist", "album_art"])
album_list: List[album_info] = []

for _, entry in enumerate(album_details):
    keys = entry.keys() if keys == [] else keys
    # break
    name = entry["name"]
    artist = entry["artists"][0]["name"]
    album_art = entry["images"][0]["url"]
    album_list.append(album_info(name, artist, album_art))

for _, entry in enumerate(album_list):
    print(f"{entry.artist}: {entry.name}")
