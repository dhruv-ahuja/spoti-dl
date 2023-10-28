use crate::spotify::LinkType;
use crate::types::{Bitrate, CliArgs, Codec, ILLEGAL_PATH_CHARS, INTERNAL_ERROR_MSG};
use crate::utils;

use std::io::Write;
use std::path::{Path, PathBuf};

use colored::Colorize;
use log::error;
use regex::Regex;

/// Parses, validates and returns arguments passed to the application; prints out apt messages to the user if it fails
pub fn parse_cli_arguments(
    download_dir_str: String,
    codec_str: String,
    bitrate_str: String,
    add_track_number: bool,
    parallel_downloads_str: String,
) -> Option<CliArgs> {
    let corrected_download_dir = utils::correct_path_names(&download_dir_str, false);
    let download_dir = Path::new(&corrected_download_dir).to_owned();

    let parallel_downloads = match parallel_downloads_str.parse() {
        Err(_) => return None,
        Ok(v) => {
            if !(1..=50).contains(&v) {
                let error_msg = "Please pass a valid parallel_downloads value!".red();
                println!("{error_msg}");
                error!("invalid parallel_downloads value passed: {parallel_downloads_str}");
                return None;
            }
            v
        }
    };

    let codec = match codec_str.parse::<Codec>() {
        Err(_) => {
            let error_msg = "Please pass a valid codec!".red();
            println!("{error_msg}");
            error!("invalid codec passed: {codec_str}");
            return None;
        }
        Ok(v) => v,
    };

    let bitrate = match bitrate_str.parse::<Bitrate>() {
        Err(_) => {
            let error_msg = "Please pass a valid bitrate!".red();
            println!("{error_msg}");
            error!("invalid bitrate passed: {bitrate_str}");
            return None;
        }
        Ok(v) => v,
    };

    Some(CliArgs {
        download_dir,
        codec,
        bitrate,
        add_track_number,
        parallel_downloads,
    })
}

/// Corrects a given file or directory path by replacing illegal characters with '#'; replaces `/` if the given name
/// is a file as files cannot contain the `/` directory indicators
pub fn correct_path_names(name: &str, is_file: bool) -> String {
    name.chars()
        .filter(|c| {
            if is_file {
                !ILLEGAL_PATH_CHARS.contains(c) && *c != '/'
            } else {
                !ILLEGAL_PATH_CHARS.contains(c)
            }
        })
        .collect()
}

/// Creates the album-art and its parent download directory given the download directory's path
pub fn create_download_directories(download_dir: &Path) -> Option<PathBuf> {
    let mut album_art_dir: PathBuf = download_dir.to_owned();
    album_art_dir.push("album-art");

    if !album_art_dir.exists() {
        if let Err(err) = std::fs::create_dir_all(&album_art_dir) {
            let error_msg = "Unable to create the download directories, please check your input path and try again!".red();
            println!("{error_msg}");
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
    let invalid_link_msg = "Invalid Spotify link type entered!".red();

    let re = match Regex::new(r"/(track|playlist|album)/([^?/]+)") {
        Err(err) => {
            println!("{}", INTERNAL_ERROR_MSG.red());
            error!("error initializing spotify URL regex pattern: {err}");
            return None;
        }
        Ok(v) => v,
    };

    let Some(captures) = re.captures(link) else {
        println!("{}", INTERNAL_ERROR_MSG.red());
        error!("invalid spotify link entered: {link}");
        return None;
    };

    // capture the link's first and second parts according to the matched pattern
    match (captures.get(1), captures.get(2)) {
        (Some(link_type), Some(spotify_id)) => Some((
            match link_type.as_str().parse() {
                Err(_) => {
                    println!("{}", INTERNAL_ERROR_MSG.red());
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
