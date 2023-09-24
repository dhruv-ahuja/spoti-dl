use rspotify::model::TrackId;
use rspotify::prelude::*;
use rspotify::AuthCodeSpotify;

#[derive(Debug)]
pub struct SpotifySong {
    pub name: String,
    pub artists: Vec<String>,
    pub album_name: String,
    pub disc_number: i32,
    pub track_number: u32,
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

    SpotifySong {
        name: track.name,
        artists,
        album_name: track.album.name,
        disc_number: track.disc_number,
        track_number: track.track_number,
        cover_url,
    }
}
