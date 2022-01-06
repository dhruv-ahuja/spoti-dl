# reference file for spotipy library's code and experimentations

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dataclasses import dataclass

# from typing import List


# sp.track(<link>).keys()
# dict_keys(['album', 'artists', 'available_markets', 'disc_number', 'duration_ms', 'explicit', 'external_ids', 'external_urls', 'href', 'id', 'is_local', 'name', 'popularity', 'preview_url', 'track_number', 'type', 'uri'])

# sp.album(<link>).keys()
# album_keys = (['album_type', 'artists', 'available_markets', 'copyrights', 'external_ids', 'external_urls', 'genres', 'href', 'id', 'images', 'label', 'name', 'popularity', 'release_date', 'release_date_precision', 'total_tracks', 'tracks', 'type', 'uri'])


# define scopes for the api
scopes = ""
keys = []

# the SpotifyOAuth class automatically reads
# "SPOTIPY..." prefixed env variables for us
sp = Spotify(auth_manager=SpotifyOAuth())
# x = sp.album_tracks()


album_details = sp.new_releases(country="IN", limit=2)
album_details = album_details["albums"]["items"]
print(type(album_details))
# defining the structure for our albums to be parsed
# Album = namedtuple("Album", ["name", "artist", "album_art"])
@dataclass
class Album:
    """dataclass that defines the Album object"""

    name: str
    artist: str
    album_art_url: str


# defining the type makes extracting data much easier when looping
albums_list: list[Album] = []

for _, entry in enumerate(album_details):
    keys = entry.keys() if keys == [] else keys
    name = entry["name"]
    artist = entry["artists"][0]["name"]
    album_art_url = entry["images"][0]["url"]
    # albums_list.append(Album(name, artist, album_art))
    a = Album(name, artist, album_art_url)

    albums_list.append(a)

for _, entry in enumerate(albums_list):
    print(f"{entry.artist}: {entry.name}")

# with albums aspect complete, we can look to extract data from the song URI
@dataclass
class Song:
    """dataclass that defines the Song object"""

    name: str
    artist: list
    album_art_url: str


# the "track" method can take in track ID, URI or URL; it is very flexible
song_details = sp.track(
    "https://open.spotify.com/track/15aRuSQrMg9pFZmWSaeSgr?si=fa8e32e6fb3547f3"
)
# print(song_details.keys())

# there can be multiple artists, iterating over the list and extracting data
artists = []
for artist in song_details["artists"]:
    artists.append(artist["name"])

song = Song(
    song_details["name"],
    artists,
    song_details["album"]["images"][0]["url"],
)

print(f"\n{', '.join(song.artist)}: {song.name}")


# adding this func for backup just in case


def check(img_url, title, artist, album, track):

    response = requests.get(img_url, stream=True)
    with open("img.jpg", "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

    print(os.getcwd())
    # exit()
    audio = ID3("<song_name>.<codec>")
    audio["TPE1"] = TPE1(encoding=3, text=artist)
    audio["TIT2"] = TALB(encoding=3, text=title)
    audio["TRCK"] = TRCK(encoding=3, text=track)
    audio["TALB"] = TALB(encoding=3, text=album)

    with open("img.jpg", "rb") as albumart:
        audio["APIC"] = APIC(
            encoding=3, mime="image/jpeg", type=3, desc="Cover", data=albumart.read()
        )

    audio.save(v2_version=3)

    # print(os.getcwd()) base folder
    # when this program shall be run from the cli controller, the directory will
    # be yASD/<download directory>
