use std::collections::HashSet;
use std::io::Write;
use std::path::Path;

use regex::Regex;

pub fn path_exists(file_path: &str) -> bool {
    Path::new(&file_path).exists()
}

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
