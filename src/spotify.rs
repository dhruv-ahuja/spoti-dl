use std::collections::HashMap;
use std::str::FromStr;

use log::error;
use rspotify::model::{AlbumId, PlayableItem, PlaylistId, PlaylistItem, TrackId};
use rspotify::prelude::*;
use rspotify::AuthCodeSpotify;

use crate::utils::correct_path_names;

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

#[derive(Debug, Clone)]
pub struct SimpleSong {
    pub name: String,
    pub artists: Vec<String>,
    pub disc_number: i32,
    pub track_number: u32,
}

#[derive(Debug, Clone)]
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

#[derive(Debug)]
pub struct SpotifyPlaylist {
    pub name: String,
    pub total_songs: u32,
    pub songs: Vec<SpotifySong>,
}

pub fn generate_client(token: String) -> AuthCodeSpotify {
    let access_token = rspotify::Token {
        access_token: token,
        expires_in: chrono::Duration::seconds(3600),
        ..Default::default()
    };
    rspotify::AuthCodeSpotify::from_token(access_token)
}

pub async fn get_song_details(
    spotify_id: String,
    spotify_client: AuthCodeSpotify,
) -> Option<SpotifySong> {
    let track_id = match TrackId::from_id(&spotify_id) {
        Err(err) => {
            error!("error {err} extracting track id {spotify_id}");
            return None;
        }
        Ok(v) => v,
    };
    let track = match spotify_client.track(track_id, None).await {
        Err(err) => {
            error!("error {err} fetching track details with id {spotify_id}");
            return None;
        }
        Ok(v) => v,
    };

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

    Some(SpotifySong {
        simple_song,
        album_name: track.album.name,
        cover_url,
    })
}

pub async fn get_album_details(
    spotify_id: String,
    spotify_client: AuthCodeSpotify,
) -> Option<SpotifyAlbum> {
    let album_id = match AlbumId::from_id(&spotify_id) {
        Err(err) => {
            error!("error {err} extracting album id {spotify_id}");
            return None;
        }
        Ok(v) => v,
    };
    let album = match spotify_client.album(album_id, None).await {
        Err(err) => {
            error!("error {err} fetching album details with id {spotify_id}");
            return None;
        }
        Ok(v) => v,
    };

    let cover_url = album.images.first().map(|image| image.url.clone());
    let mut songs = Vec::with_capacity(album.tracks.total as usize);

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

    Some(SpotifyAlbum {
        name: album.name,
        songs,
        cover_url,
    })
}

pub fn filter_playlist_items(items: Vec<PlaylistItem>) -> Vec<SpotifySong> {
    let mut songs = Vec::with_capacity(items.len());
    for item in items {
        let Some(track) = item.track else { continue };
        let PlayableItem::Track(song_track) = track else {
            continue;
        };
        if let Some(href) = song_track.href {
            if href.contains("show") || href.contains("episode") {
                continue;
            }
        }

        let corrected_song_name = correct_path_names(&song_track.name, true);
        let corrected_album_name = correct_path_names(&song_track.album.name, true);

        let simple_song = SimpleSong {
            name: corrected_song_name,
            artists: song_track
                .artists
                .iter()
                .map(|artist| artist.name.clone())
                .collect(),
            disc_number: song_track.disc_number,
            track_number: song_track.track_number,
        };

        let song = SpotifySong {
            simple_song,
            album_name: corrected_album_name,
            cover_url: song_track
                .album
                .images
                .first()
                .map(|image| image.url.clone()),
        };
        songs.push(song);
    }
    songs
}

// fetches the playlists' details and the 100 initial tracks; skips any podcast episodes as the app cannot reliably download
//  them reliably
pub async fn get_playlist_details(
    spotify_client: &AuthCodeSpotify,
    spotify_id: &str,
) -> Option<SpotifyPlaylist> {
    let playlist_id = match PlaylistId::from_id(spotify_id) {
        Err(err) => {
            error!("error {err} extracting playlist id {spotify_id}");
            return None;
        }
        Ok(v) => v,
    };
    let playlist = match spotify_client.playlist(playlist_id, None, None).await {
        Err(err) => {
            error!("error {err} fetching playlist details with id {spotify_id}");
            return None;
        }
        Ok(v) => v,
    };

    let total_songs = playlist.tracks.total;
    let songs = filter_playlist_items(playlist.tracks.items);

    Some(SpotifyPlaylist {
        name: playlist.name,
        total_songs,
        songs,
    })
}

pub async fn get_playlist_songs(
    spotify_client: &AuthCodeSpotify,
    spotify_id: &str,
    offset: u32,
) -> Option<Vec<SpotifySong>> {
    let playlist_id = match PlaylistId::from_id(spotify_id) {
        Err(err) => {
            error!("error {err} extracting playlist id {spotify_id}");
            return None;
        }
        Ok(v) => v,
    };
    let playlist_items = match spotify_client
        .playlist_items_manual(playlist_id, None, None, Some(100), Some(offset))
        .await
    {
        Err(err) => {
            error!(
                "error {err} fetching playlist items with id {spotify_id}\
                \nwith offset {offset}"
            );
            return None;
        }
        Ok(v) => v,
    };

    Some(filter_playlist_items(playlist_items.items))
}

pub fn get_unique_cover_urls(songs: &Vec<SpotifySong>) -> HashMap<String, String> {
    let mut unique_covers_map = HashMap::with_capacity(songs.len());

    for song in songs {
        if unique_covers_map.contains_key(&song.album_name) {
            continue;
        };

        let album_name = correct_path_names(&song.album_name, true);
        let cover_url = match song.cover_url.clone() {
            None => continue,
            Some(v) => v,
        };

        unique_covers_map.insert(album_name, cover_url);
    }
    unique_covers_map
}
