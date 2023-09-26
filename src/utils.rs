use crate::spotify::LinkType;

use std::collections::HashSet;
use std::io::Write;
use std::path::{Path, PathBuf};

use regex::Regex;

/// Corrects a given file or directory path by replacing illegal characters with '#'; replaces `/` if the given path is a file
pub fn remove_illegal_path_characters(
    illegal_path_chars: &HashSet<char>,
    path: &str,
    is_file: bool,
) -> String {
    path.chars()
        .map(|c| match (is_file, c) {
            (true, c) if illegal_path_chars.contains(&c) || c == '/' => '#',
            (false, c) if illegal_path_chars.contains(&c) => '#',
            (_, c) => c,
        })
        .collect()
}

pub fn make_download_directories(download_dir: &Path) -> std::io::Result<PathBuf> {
    let mut album_art_dir: PathBuf = download_dir.to_owned();
    album_art_dir.push("album-art");

    if !album_art_dir.exists() {
        std::fs::create_dir_all(&album_art_dir)?
    }

    Ok(album_art_dir)
}

pub fn generate_youtube_query(song_name: &str, artists: &[String]) -> String {
    format!("{} - {} audio", artists.join(", "), song_name)
}

pub fn parse_link(link: &str) -> Option<(LinkType, String)> {
    let re = Regex::new(r"/(track|playlist|album|episode)/([^?/]+)").unwrap();

    let Some(captures) = re.captures(link) else {
        return None
    };

    match (captures.get(1), captures.get(2)) {
        (Some(link_type), Some(spotify_id)) => Some((
            link_type.as_str().parse().unwrap(),
            spotify_id.as_str().to_string(),
        )),
        _ => None,
    }
}

pub async fn download_album_art(link: String, album_art_path: &Path) {
    if album_art_path.exists() {
        return;
    }

    let response = reqwest::get(link).await.unwrap();
    let image_data = response.bytes().await.unwrap();

    let mut image = std::fs::File::create(album_art_path).unwrap();
    image.write_all(&image_data).unwrap();
}
