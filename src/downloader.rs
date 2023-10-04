use crate::spotify::{SimpleSong, SpotifyAlbum, SpotifyPlaylist, SpotifySong};
use crate::utils::{self, download_album_art, remove_illegal_path_characters};
use crate::CliArgs;
use crate::{metadata, spotify};

use std::collections::HashSet;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::time::Instant;

use color_eyre::eyre::Result;
use rspotify::AuthCodeSpotify;
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

async fn download_album_songs(
    mut file_path: PathBuf,
    illegal_path_chars: &HashSet<char>,
    args: Arc<CliArgs>,
    album_art_dir: Arc<PathBuf>,
    album_name: Arc<String>,
    songs: Vec<SimpleSong>,
) {
    for song in songs {
        let corrected_song_name =
            remove_illegal_path_characters(illegal_path_chars, &song.name, true);

        let file_name = format!("{}.{}", corrected_song_name, args.codec);
        file_path.push(&file_name);

        let now = Instant::now();
        if download_song(&file_path, &corrected_song_name, &song.artists, &args).await {
            println!("time to download: {:?}", now.elapsed());
            let now = Instant::now();

            tokio::task::block_in_place(|| {
                let album_art_dir = album_art_dir.clone();
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

async fn download_album_covers(
    unique_covers: Vec<(String, String)>,
    album_art_dir: PathBuf,
    parallel_tasks_count: usize,
) {
    let mut chunks = Vec::with_capacity(parallel_tasks_count);
    for _ in 0..parallel_tasks_count {
        chunks.push(Vec::new())
    }

    for (i, item) in unique_covers.into_iter().enumerate() {
        let idx = i % parallel_tasks_count;
        chunks[idx].push(item);
    }

    let mut handles = Vec::with_capacity(parallel_tasks_count);

    for chunk in chunks {
        let mut cover_dir = album_art_dir.clone();

        let handle = tokio::spawn(async move {
            for (album_name, cover_url) in chunk {
                let album_art_file = format!("{}.jpeg", album_name);
                cover_dir.push(album_art_file);

                download_album_art(cover_url.to_string(), &cover_dir).await;
                cover_dir.pop();
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.await.unwrap()
    }
}
async fn download_playlist_songs(
    mut file_path: PathBuf,
    args: Arc<CliArgs>,
    album_art_dir: PathBuf,
    song_details: Vec<SpotifySong>,
) {
    for item in song_details {
        let song_name = item.simple_song.name.clone();
        let file_name = format!("{}.{}", &song_name, args.codec);
        file_path.push(&file_name);

        let album_art_file = format!("{}.jpeg", &item.album_name);
        let mut cover_dir = album_art_dir.clone();
        cover_dir.push(album_art_file);

        if download_song(&file_path, &song_name, &item.simple_song.artists, &args).await {
            tokio::task::block_in_place(|| {
                println!(
                    "adding metadata for {} AT PATH {}",
                    &item.simple_song.name,
                    file_path.display()
                );

                metadata::add_metadata(
                    file_path.clone(),
                    cover_dir.to_path_buf(),
                    item.simple_song,
                    item.album_name,
                );
            });
        }
        cover_dir.pop();
        file_path.pop();
    }
}

pub async fn process_song_download(
    song: SpotifySong,
    illegal_path_chars: &'static HashSet<char>,
    args: CliArgs,
) {
    let corrected_song_name =
        remove_illegal_path_characters(illegal_path_chars, &song.simple_song.name, true);

    let mut album_art_dir = match utils::make_download_directories(&args.download_dir) {
        Err(err) => {
            println!("error creating download directories: {err}");
            return;
        }
        Ok(dir) => dir,
    };

    let file_name = format!("{}.{}", corrected_song_name, args.codec);
    let mut file_path = args.download_dir.clone();

    file_path.push(&file_name);
    let artists = &song.simple_song.artists;

    if download_song(&file_path, &corrected_song_name, artists, &args).await {
        let album_art_file = format!("{}.jpeg", &song.album_name);
        album_art_dir.push(album_art_file);

        utils::download_album_art(song.cover_url.clone().unwrap(), &album_art_dir).await;
        metadata::add_metadata(file_path, album_art_dir, song.simple_song, song.album_name)
    }
}

pub async fn process_album_download(
    album: SpotifyAlbum,
    illegal_path_chars: &'static HashSet<char>,
    args: CliArgs,
) {
    let mut file_path = args.download_dir.clone();
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

    let parallel_tasks_count: usize = if album.songs.len() >= args.parallel_downloads as usize {
        args.parallel_downloads as usize
    } else {
        album.songs.len()
    };

    let songs_per_task = (album.songs.len() + parallel_tasks_count - 1) / parallel_tasks_count;
    println!("{songs_per_task}, {}", album.songs.len());

    let args = Arc::new(args);
    let album_art_dir = Arc::new(album_art_dir);
    let album_name = Arc::new(album.name);

    let handles = album
        .songs
        .chunks(songs_per_task)
        .map(|chunk| {
            tokio::spawn(download_album_songs(
                file_path.clone(),
                illegal_path_chars,
                args.clone(),
                album_art_dir.clone(),
                album_name.clone(),
                chunk.to_vec(),
            ))
        })
        .collect::<Vec<_>>();

    for handle in handles {
        handle.await.unwrap();
    }

    println!("\nDownload for album {} completed, enjoy!", &album_name);
}

pub async fn process_playlist_download(
    spotify_id: String,
    spotify_client: AuthCodeSpotify,
    playlist: SpotifyPlaylist,
    illegal_path_chars: &'static HashSet<char>,
    args: CliArgs,
) -> Result<()> {
    color_eyre::install()?;

    let total_songs = playlist.total_songs;
    if total_songs == 0 || playlist.songs.is_empty() {
        println!("no songs to download in the playlist!");
        return Ok(());
    }

    let mut file_path = args.download_dir.clone();
    file_path.push(&playlist.name);

    let album_art_dir = match utils::make_download_directories(&file_path) {
        Err(err) => {
            println!("error creating download directories: {err}");
            return Ok(());
        }
        Ok(dir) => dir,
    };

    let mut offset = 0;
    let parallel_tasks_count: usize = if total_songs >= args.parallel_downloads {
        args.parallel_downloads as usize
    } else {
        total_songs as usize
    };

    let args = Arc::new(args);
    let mut song_details = playlist.songs;

    while total_songs > offset {
        if offset > 0 {
            song_details = spotify::get_playlist_songs(
                &spotify_client,
                &spotify_id,
                offset,
                illegal_path_chars,
            )
            .await;
        }

        if song_details.is_empty() {
            println!("no more songs left to download");
            return Ok(());
        }

        let songs_per_task = (song_details.len() + parallel_tasks_count - 1) / parallel_tasks_count;
        println!(
            "songs per task: {}, total len: {}",
            songs_per_task,
            song_details.len()
        );

        let unique_covers_map = spotify::get_unique_cover_urls(&song_details);
        let unique_covers: Vec<_> = unique_covers_map.into_iter().collect();

        download_album_covers(unique_covers, album_art_dir.clone(), parallel_tasks_count).await;

        let handles = song_details
            .chunks(songs_per_task)
            .map(|chunk| {
                tokio::spawn(download_playlist_songs(
                    file_path.clone(),
                    args.clone(),
                    album_art_dir.clone(),
                    chunk.to_vec(),
                ))
            })
            .collect::<Vec<_>>();

        for handle in handles {
            handle.await.unwrap();
        }

        offset += 100;
    }

    println!(
        "\nDownload for playlist {} completed, enjoy!",
        &playlist.name
    );
    Ok(())
}
