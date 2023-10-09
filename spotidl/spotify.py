import spotipy
from spotipy.oauth2 import SpotifyOAuth

from spotidl.config import ENV_VARS_ERROR


def get_spotify_client() -> spotipy.Spotify:
    try:
        client = spotipy.Spotify(auth_manager=SpotifyOAuth())

    except spotipy.oauth2.SpotifyOauthError:
        print(ENV_VARS_ERROR)

    return client


def get_spotify_token(client: spotipy.Spotify) -> spotipy.SpotifyOAuth:
    auth_manager: SpotifyOAuth = client.auth_manager
    token = auth_manager.get_access_token(None, as_dict=False, check_cache=True)
    return token
