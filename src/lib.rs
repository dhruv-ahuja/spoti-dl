mod metadata;
mod spotify;
mod utils;

use std::{
    collections::HashSet,
    path::{Path, PathBuf},
};

use pyo3::prelude::*;
use youtube_dl::YoutubeDl;

/// A Python module implemented in Rust.
#[pymodule]
fn spotidl_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(handle_song_download, m)?)?;
    Ok(())
}

#[derive(Debug)]
struct CliArgs {
    download_dir: PathBuf,
    codec: metadata::Codec,
    bitrate: metadata::Bitrate,
}

/// Handles end-to-end flow for a song download: fetches song information from Spotify, prepares the song's source,
/// downloads it and writes song metadata.
#[pyfunction]
fn handle_song_download(
    py: Python<'_>,
    token: String,
    link: String,
    download_dir: String,
    codec: String,
    bitrate: String,
) -> PyResult<&PyAny> {
    pyo3_asyncio::tokio::future_into_py(py, async move {
        let Some(spotify_id) = utils::parse_link(&link) else {
            println!("Invalid Spotify link type entered!"); 
            return Ok(())
        };

        let illegal_path_chars: HashSet<char> = ['\\', '?', '%', '*', ':', '|', '"', '<', '>', '.']
            .iter()
            .cloned()
            .collect();

        let download_dir =
            utils::remove_illegal_path_characters(&illegal_path_chars, &download_dir, false);
        let download_dir = Path::new(&download_dir).to_owned();

        let args = CliArgs {
            download_dir,
            codec: codec.parse().unwrap(), // TODO: replace with proper error message on invalid input
            bitrate: bitrate.parse().unwrap(),
        };

        let mut album_art_dir = match utils::make_download_directories(&args.download_dir) {
            Err(err) => {
                println!("error creating download directories: {err}");
                return Ok(());
            }
            Ok(dir) => dir,
        };

        let song = spotify::get_song_details(token, spotify_id).await;
        let corrected_song_name =
            utils::remove_illegal_path_characters(&illegal_path_chars, &song.name, true);

        let file_name = format!("{}.{}", corrected_song_name, &codec);
        let mut file_path = args.download_dir.to_path_buf();
        file_path.push(&file_name);

        if download_song(&file_path, &song, &args).await {
            let album_art_file = format!("{}.jpeg", &song.album_name);
            album_art_dir.push(album_art_file);

            utils::download_album_art(song.cover_url.clone().unwrap(), &album_art_dir).await;
            metadata::add_metadata(&file_path, &album_art_dir, &song)
        }

        Ok(())
    })
}

async fn download_song(file_path: &Path, song: &spotify::SpotifySong, args: &CliArgs) -> bool {
    let file_output_format = format!("{}/{}.%(ext)s", &args.download_dir.display(), &song.name);

    if file_path.exists() {
        println!("{} already exists, skipping download", &song.name);
        return false;
    }

    let query = utils::generate_youtube_query(&song.name, &song.artists);
    let search_options = youtube_dl::SearchOptions::youtube(query);

    let mut yt_client = YoutubeDl::search_for(&search_options);
    println!("Starting {} song download", song.name);

    let codec = args.codec.to_string();
    let bitrate = args.bitrate.to_string();

    if let Err(err) = yt_client
        .extract_audio(true)
        .output_template(file_output_format)
        .extra_arg("--audio-format")
        .extra_arg(codec)
        .extra_arg("--audio-quality")
        .extra_arg(bitrate)
        .download_to_async("./")
        .await
    {
        println!("Error downloading {} song: {err}", &song.name);
        return false;
    }
    true
}
