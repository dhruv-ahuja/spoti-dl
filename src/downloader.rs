use crate::CliArgs;
use crate::{metadata, spotify, utils};

use youtube_dl::YoutubeDl;

use std::collections::HashSet;
use std::path::Path;

pub async fn download_song(
    file_path: &Path,
    song_name: &str,
    artists: &[String],
    args: &CliArgs,
) -> bool {
    let file_output_format = format!(
        "{}/{}.%(ext)s",
        file_path.parent().unwrap().display(),
        song_name
    );
    if file_path.exists() {
        println!("\n{} already exists, skipping download", song_name);
        return false;
    }

    let query = utils::generate_youtube_query(song_name, artists);
    let search_options = youtube_dl::SearchOptions::youtube(query);

    let mut yt_client = YoutubeDl::search_for(&search_options);
    println!("\nStarting {} song download", song_name);

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
        println!("Error downloading {} song: {err}", song_name);
        return false;
    }
    println!("{} downloaded", song_name);
    true
}

pub async fn download_album(
    album: spotify::SpotifyAlbum,
    illegal_path_chars: &HashSet<char>,
    args: &CliArgs,
    codec: &str,
) {
    let mut file_path = args.download_dir.to_path_buf();
    file_path.push(&album.name);

    let mut album_art_dir = match utils::make_download_directories(&file_path) {
        Err(err) => {
            println!("error creating download directories: {err}");
            return;
        }
        Ok(dir) => dir,
    };

    // downloading album art first as all songs will share the same album art
    let album_art_file = format!("{}.jpeg", &album.name);
    album_art_dir.push(album_art_file);

    utils::download_album_art(album.cover_url.clone().unwrap(), &album_art_dir).await;

    println!("\nstarting album {} download", &album.name);

    for song in album.songs {
        let mut file_path = file_path.clone();

        let corrected_song_name =
            utils::remove_illegal_path_characters(illegal_path_chars, &song.name, true);

        let file_name = format!("{}.{}", corrected_song_name, &codec);
        file_path.push(&file_name);

        if download_song(&file_path, &corrected_song_name, &song.artists, args).await {
            metadata::add_metadata(&file_path, &album_art_dir, &song, &album.name)
        }
    }
    println!("\nFinished downloading {} album", &album.name);
}
//
