use std::str::FromStr;

use rspotify::model::AlbumId;
use rspotify::model::TrackId;
use rspotify::prelude::*;
use rspotify::AuthCodeSpotify;

#[derive(Debug, PartialEq)]
pub enum LinkType {
    Track,
    Album,
    Playlist,
}

impl FromStr for LinkType {
    type Err = ();
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        use LinkType::*;

        match s {
            "track" => Ok(Track),
            "album" => Ok(Album),
            "playlist" => Ok(Playlist),
            _ => Err(()),
        }
    }
}

#[derive(Debug)]
pub struct SimpleSong {
    pub name: String,
    pub artists: Vec<String>,
    pub disc_number: i32,
    pub track_number: u32,
}

#[derive(Debug)]
pub struct SpotifySong {
    pub simple_song: SimpleSong,
    pub album_name: String,
    pub cover_url: Option<String>,
}

#[derive(Debug)]
pub struct SpotifyAlbum {
    pub name: String,
    pub songs: Vec<SimpleSong>,
    pub cover_url: Option<String>,
}

pub fn generate_client(token: String) -> AuthCodeSpotify {
    let access_token = rspotify::Token {
        access_token: token,
        expires_in: chrono::Duration::seconds(3600),
        ..Default::default()
    };
    rspotify::AuthCodeSpotify::from_token(access_token)
}

pub async fn get_song_details(token: String, spotify_id: String) -> SpotifySong {
    let mut spotify = generate_client(token);
    spotify.config.token_refreshing = false;

    let track_id = TrackId::from_id(spotify_id).unwrap();
    let track = spotify.track(track_id, None).await.unwrap();

    let cover_url = track.album.images.first().map(|image| image.url.clone());
    let artists = track
        .artists
        .iter()
        .map(|artist| artist.name.clone())
        .collect();

    let simple_song = SimpleSong {
        name: track.name,
        artists,
        disc_number: track.disc_number,
        track_number: track.track_number,
    };

    SpotifySong {
        simple_song,
        album_name: track.album.name,
        cover_url,
    }
}

pub async fn get_album_details(token: String, spotify_id: String) -> SpotifyAlbum {
    let mut spotify = generate_client(token);
    spotify.config.token_refreshing = false;

    let album_id = AlbumId::from_id(spotify_id).unwrap();
    let album = spotify.album(album_id, None).await.unwrap();

    let cover_url = album.images.first().map(|image| image.url.clone());
    let mut songs = Vec::with_capacity(album.tracks.total as usize);

    // todo: check whether we can optimize fetching the artists -- O(n*m) + extra cloning
    for track in album.tracks.items {
        let song = SimpleSong {
            name: track.name,
            artists: track
                .artists
                .iter()
                .map(|artist| artist.name.clone())
                .collect(),
            disc_number: track.disc_number,
            track_number: track.track_number,
        };
        songs.push(song)
    }

    SpotifyAlbum {
        name: album.name,
        songs,
        cover_url,
    }
}
