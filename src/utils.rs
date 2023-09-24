use std::collections::HashSet;
use std::io::Write;
use std::path::Path;

use regex::Regex;

pub fn path_exists(file_path: &str) -> bool {
    Path::new(&file_path).exists()
}

/// Create a new direcotry path where illegal characters are replaced with "#"
pub fn correct_directory_name(illegal_path_chars: &HashSet<char>, directory: String) -> String {
    directory
        .chars()
        .map(|c| {
            if illegal_path_chars.contains(&c) {
                '#'
            } else {
                c
            }
        })
        .collect()
}

pub fn make_download_directories(download_dir: &str) -> std::io::Result<()> {
    let album_art_dir = format!("{}/album-art", download_dir);
    if !path_exists(&album_art_dir) {
        std::fs::create_dir_all(album_art_dir)?
    }
    Ok(())
}

pub fn generate_youtube_query(song_name: &str, artists: &[String]) -> String {
    format!("{} - {} audio", artists.join(", "), song_name)
}

pub fn parse_link(link: &str) -> Option<String> {
    let re = Regex::new(r"/(track|playlist|album|episode)/([^?/]+)").unwrap();

    let Some(captures) = re.captures(link) else {
        return None
    };
    match captures.get(2) {
        None => None,
        Some(needle) => return Some(needle.as_str().into()),
    }
}

pub async fn download_album_art(link: String, album_art_path: &str) {
    if path_exists(album_art_path) {
        return;
    }

    let response = reqwest::get(link).await.unwrap();
    let image_data = response.bytes().await.unwrap();

    let mut image = std::fs::File::create(album_art_path).unwrap();
    image.write_all(&image_data).unwrap();
}
