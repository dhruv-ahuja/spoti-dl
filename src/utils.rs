use crate::metadata::{Bitrate, Codec};
use crate::spotify::LinkType;
use crate::types::CliArgs;
use crate::utils;

use std::collections::HashSet;
use std::io::Write;
use std::path::{Path, PathBuf};

use regex::Regex;

/// Parses, validates and returns arguments passed to the application; prints out apt messages to the user if it fails
pub fn parse_cli_arguments(
    download_dir_str: String,
    codec_str: String,
    bitrate_str: String,
    parallel_downloads_str: String,
    illegal_path_chars: &HashSet<char>,
) -> Option<CliArgs> {
    let corrected_download_dir =
        utils::remove_illegal_path_characters(illegal_path_chars, &download_dir_str, false);
    let download_dir = Path::new(&corrected_download_dir).to_owned();

    let parallel_downloads = match parallel_downloads_str.parse() {
        Err(_) => return None,
        Ok(v) => {
            if !(1..=50).contains(&v) {
                return None;
            }
            v
        }
    };

    let codec = match codec_str.parse::<Codec>() {
        Err(_) => {
            println!("Please pass a valid codec!");
            log::error!("invalid codec passed: {codec_str}");
            return None;
        }
        Ok(v) => v,
    };

    let bitrate = match bitrate_str.parse::<Bitrate>() {
        Err(_) => {
            println!("Please pass a valid bitrate!");
            log::error!("invalid codec passed: {bitrate_str}");
            return None;
        }
        Ok(v) => v,
    };

    Some(CliArgs {
        download_dir,
        codec,
        bitrate,
        parallel_downloads,
    })
}

/// Corrects a given file or directory path by replacing illegal characters with '#'; replaces `/` if the given path is a file
pub fn remove_illegal_path_characters(
    illegal_path_chars: &HashSet<char>,
    name: &str,
    is_file: bool,
) -> String {
    name.chars()
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
    let re = Regex::new(r"/(track|playlist|album)/([^?/]+)").unwrap();

    let Some(captures) = re.captures(link) else {
        println!("Invalid Spotify link type entered!"); 
        log::info!("invalid spotify link entered: {link}");
        return None
    };

    // capture the link's first and second parts according to the matched pattern
    match (captures.get(1), captures.get(2)) {
        (Some(link_type), Some(spotify_id)) => Some((
            link_type.as_str().parse().unwrap(),
            spotify_id.as_str().to_string(),
        )),
        _ => {
            println!("Invalid Spotify link type entered!");
            log::info!("invalid spotify link entered: {link}");
            None
        }
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
