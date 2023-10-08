use crate::metadata::{Bitrate, Codec};
use crate::spotify::LinkType;
use crate::types::{CliArgs, INTERNAL_ERROR_MSG};
use crate::utils;

use std::collections::HashSet;
use std::io::Write;
use std::path::{Path, PathBuf};

use log::error;
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
            error!("invalid codec passed: {codec_str}");
            return None;
        }
        Ok(v) => v,
    };

    let bitrate = match bitrate_str.parse::<Bitrate>() {
        Err(_) => {
            println!("Please pass a valid bitrate!");
            error!("invalid codec passed: {bitrate_str}");
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

/// Creates the album-art and its parent download directory given the download directory's path
pub fn create_download_directories(download_dir: &Path) -> Option<PathBuf> {
    let mut album_art_dir: PathBuf = download_dir.to_owned();
    album_art_dir.push("album-art");

    if !album_art_dir.exists() {
        if let Err(err) = std::fs::create_dir_all(&album_art_dir) {
            println!("Unable to create the download directories, please check your input path and try again!");
            error!(
                "invalid download directory passed: {:?}; error: {:?}",
                download_dir.display(),
                err
            );
            return None;
        }
    }

    Some(album_art_dir)
}

/// Generates the search query to fetch song audio stream from Youtube
pub fn generate_youtube_query(song_name: &str, artists: &[String]) -> String {
    format!("{} - {} audio", artists.join(", "), song_name)
}

/// Parses the link type and the Spotify item ID from the input Spotify link
pub fn parse_link(link: &str) -> Option<(LinkType, String)> {
    let invalid_link_msg = "Invalid Spotify link type entered!";

    let re = match Regex::new(r"/(track|playlist|album)/([^?/]+)") {
        Err(err) => {
            println!("{INTERNAL_ERROR_MSG}");
            error!("error initializing spotify URL regex pattern: {err}");
            return None;
        }
        Ok(v) => v,
    };

    let Some(captures) = re.captures(link) else {
        println!("{INTERNAL_ERROR_MSG}");
        error!("invalid spotify link entered: {link}");
        return None
    };

    // capture the link's first and second parts according to the matched pattern
    match (captures.get(1), captures.get(2)) {
        (Some(link_type), Some(spotify_id)) => Some((
            match link_type.as_str().parse() {
                Err(_) => {
                    println!("{INTERNAL_ERROR_MSG}");
                    error!("error parsing {} link's type as LinkType value:", link);
                    return None;
                }
                Ok(v) => v,
            },
            spotify_id.as_str().to_string(),
        )),
        _ => {
            println!("{invalid_link_msg}");
            error!("invalid spotify link entered: {link}");
            None
        }
    }
}

// Downloads an album art image and writes its data to the target path; the path contains the file name
pub async fn download_album_art(
    link: String,
    album_art_path: &Path,
) -> Result<(), Box<dyn std::error::Error>> {
    if !album_art_path.exists() {
        let response = reqwest::get(link).await?;
        let image_data = response.bytes().await?;

        let mut image = std::fs::File::create(album_art_path)?;
        image.write_all(&image_data)?;
    }

    Ok(())
}
