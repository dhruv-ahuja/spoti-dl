mod downloader;
mod metadata;
mod spotify;
mod utils;

use std::collections::HashSet;
use std::path::{Path, PathBuf};

use lazy_static::lazy_static;
use pyo3::prelude::*;
use spotify::LinkType;

/// A Python module implemented in Rust.
#[pymodule]
fn spotidl_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(process_downloads, m)?)?;
    Ok(())
}

lazy_static! {
    pub static ref ILLEGAL_PATH_CHARS: HashSet<char> =
        ['\\', '?', '%', '*', ':', '|', '"', '<', '>', '.']
            .iter()
            .cloned()
            .collect();
}

#[derive(Debug)]
pub struct CliArgs {
    download_dir: PathBuf,
    codec: metadata::Codec,
    bitrate: metadata::Bitrate,
}

impl CliArgs {
    fn new(download_dir: String, codec: String, bitrate: String) -> Self {
        let corrected_download_dir =
            utils::remove_illegal_path_characters(&ILLEGAL_PATH_CHARS, &download_dir, false);
        let download_dir = Path::new(&corrected_download_dir).to_owned();

        CliArgs {
            download_dir,
            codec: codec.parse().unwrap(), // TODO: replace with proper error message on invalid input
            bitrate: bitrate.parse().unwrap(),
        }
    }
}

/// Processes end-to-end flow for processing song, album and playlist downloads by validating and parsing user input
/// and calling apt functions to process the steps relating to the downloads
#[pyfunction]
fn process_downloads(
    py: Python<'_>,
    token: String,
    link: String,
    download_dir: String,
    codec: String,
    bitrate: String,
) -> PyResult<&PyAny> {
    pyo3_asyncio::tokio::future_into_py(py, async move {
        let Some((link_type,spotify_id)) = utils::parse_link(&link) else {
            println!("Invalid Spotify link type entered!"); 
            return Ok(())
        };
        let args = CliArgs::new(download_dir, codec, bitrate);

        match link_type {
            LinkType::Track => {
                let song = spotify::get_song_details(token, spotify_id).await;
                downloader::process_song_download(song, &ILLEGAL_PATH_CHARS, args).await;
            }
            LinkType::Album => {
                let album = spotify::get_album_details(token, spotify_id).await;
                downloader::process_album_download(album, &ILLEGAL_PATH_CHARS, args).await;
            }
            _ => process_playlist_download(),
        }

        Ok(())
    })
}

fn process_playlist_download() {
    todo!()
}
