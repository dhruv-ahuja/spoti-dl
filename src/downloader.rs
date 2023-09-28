use crate::spotify::{SimpleSong, SpotifyAlbum};
use crate::CliArgs;
use crate::{metadata, utils};

use std::collections::HashSet;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::time::Instant;

use youtube_dl::YoutubeDl;

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

async fn download_multiple_songs(
    mut file_path: PathBuf,
    illegal_path_chars: &HashSet<char>,
    args: Arc<CliArgs>,
    codec: String,
    album_art_dir: Arc<PathBuf>,
    album_name: Arc<String>,
    songs: Vec<SimpleSong>,
) {
    println!("{:?}", &songs);
    for song in songs {
        let corrected_song_name =
            utils::remove_illegal_path_characters(illegal_path_chars, &song.name, true);

        let file_name = format!("{}.{}", corrected_song_name, &codec);
        file_path.push(&file_name);

        let now = Instant::now();
        if download_song(&file_path, &corrected_song_name, &song.artists, &args).await {
            println!("time to download: {:?}", now.elapsed());
            let now = Instant::now();

            tokio::task::block_in_place(|| {
                let album_art_dir = album_art_dir.clone();
                println!(
                    "adding metadata for {} AT PATH {}",
                    &song.name,
                    file_path.display()
                );
                metadata::add_metadata(
                    file_path.clone(),
                    album_art_dir.to_path_buf(),
                    song,
                    album_name.clone().to_string(),
                )
            });
            println!("time to write metadata: {:?}", now.elapsed());
            // remove the current song name from the path for subsequent songs
            file_path.pop();
        }
    }
}

pub async fn download_album(
    album: SpotifyAlbum,
    illegal_path_chars: &'static HashSet<char>,
    args: CliArgs,
    codec: String,
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

    let album_art_file = format!("{}.jpeg", &album.name);
    album_art_dir.push(album_art_file);

    utils::download_album_art(album.cover_url.clone().unwrap(), &album_art_dir).await;
    println!("\nstarting album {} download", &album.name);

    let parallel_tasks_count = 10;
    let songs_per_task = (album.songs.len() + parallel_tasks_count - 1) / parallel_tasks_count;
    println!("{songs_per_task}, {}", album.songs.len());

    let args = Arc::new(args);
    let album_art_dir = Arc::new(album_art_dir);
    let album_name = Arc::new(album.name);

    let handles = album
        .songs
        .chunks(songs_per_task)
        .map(|chunk| {
            tokio::spawn(download_multiple_songs(
                file_path.clone(),
                illegal_path_chars,
                args.clone(),
                codec.clone(),
                album_art_dir.clone(),
                album_name.clone(),
                chunk.to_vec(),
            ))
        })
        .collect::<Vec<_>>();

    for handle in handles {
        handle.await.unwrap();
    }

    println!("\nFinished downloading {} album", &album_name);
}
