use crate::spotify::{SimpleSong, SpotifyAlbum, SpotifyPlaylist, SpotifySong};
use crate::types::{CliArgs, INTERNAL_ERROR_MSG};
use crate::utils::{self, download_album_art, remove_illegal_path_characters};
use crate::{metadata, spotify};

use std::error::Error;
use std::path::{Path, PathBuf};
use std::sync::Arc;

use log::error;
use rspotify::AuthCodeSpotify;
use youtube_dl::YoutubeDl;

pub async fn download_song(
    file_path: &Path,
    song_name: &str,
    artists: &[String],
    cli_args: &CliArgs,
) -> bool {
    let parent_dir_display = match file_path.parent() {
        None => {
            println!("{INTERNAL_ERROR_MSG}");
            error!(
                "no parent found for file path {:?} during download",
                file_path.display()
            );
            return false;
        }
        Some(v) => v.display(),
    };
    let file_output_format = format!("{}/{}.%(ext)s", parent_dir_display, song_name);

    if file_path.exists() {
        println!("\n{} already exists, skipping download", song_name);
        return false;
    }

    let query = utils::generate_youtube_query(song_name, artists);
    let search_options = youtube_dl::SearchOptions::youtube(query);

    let mut yt_client = YoutubeDl::search_for(&search_options);
    println!("\nStarting {} song download", song_name);

    let codec = cli_args.codec.to_string();
    let bitrate = cli_args.bitrate.to_string();

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
        println!("Unable to download {} song!", &song_name);
        error!("error {err} downloading {song_name} song");
        return false;
    }

    println!("{} downloaded", song_name);
    true
}

async fn download_album_songs(
    mut file_path: PathBuf,
    cli_args: Arc<CliArgs>,
    album_art_dir: Arc<PathBuf>,
    album_name: Arc<String>,
    songs: Vec<SimpleSong>,
) {
    for song in songs {
        let corrected_song_name = remove_illegal_path_characters(&song.name, true);

        let file_name = format!("{}.{}", corrected_song_name, cli_args.codec);
        file_path.push(&file_name);

        if download_song(&file_path, &corrected_song_name, &song.artists, &cli_args).await {
            tokio::task::block_in_place(|| {
                let album_art_dir = album_art_dir.clone();
                metadata::add_metadata(
                    file_path.clone(),
                    album_art_dir.to_path_buf(),
                    song,
                    album_name.clone().to_string(),
                )
            });

            // remove the current song name from the path for subsequent songs
            file_path.pop();
        }
    }
}

async fn download_album_covers(
    unique_covers: Vec<(String, String)>,
    album_art_dir: PathBuf,
    parallel_tasks_count: usize,
) -> Result<(), Box<dyn Error>> {
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
                let album_art_file = format!("{}.jpeg", &album_name);
                cover_dir.push(album_art_file);

                if let Err(err) = download_album_art(cover_url.to_string(), &cover_dir).await {
                    println!("Unable to download {album_name}'s album art!");
                    error!("error downloading {album_name}'s album art: {err}");
                };
                cover_dir.pop();
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.await?
    }
    Ok(())
}
async fn download_playlist_songs(
    mut file_path: PathBuf,
    cli_args: Arc<CliArgs>,
    album_art_dir: PathBuf,
    song_details: Vec<SpotifySong>,
) {
    for item in song_details {
        let song_name = item.simple_song.name.clone();
        let file_name = format!("{}.{}", &song_name, cli_args.codec);
        file_path.push(&file_name);

        let album_art_file = format!("{}.jpeg", &item.album_name);
        let mut cover_dir = album_art_dir.clone();
        cover_dir.push(album_art_file);

        if download_song(&file_path, &song_name, &item.simple_song.artists, &cli_args).await {
            tokio::task::block_in_place(|| {
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

pub async fn process_song_download(song: SpotifySong, cli_args: CliArgs) {
    let corrected_song_name = remove_illegal_path_characters(&song.simple_song.name, true);
    let corrected_album_name = remove_illegal_path_characters(&song.album_name, true);

    let Some(mut album_art_dir) = utils::create_download_directories(&cli_args.download_dir) else {
        return;
    };

    let file_name = format!("{}.{}", corrected_song_name, cli_args.codec);
    let mut file_path = cli_args.download_dir.clone();

    file_path.push(&file_name);
    let artists = &song.simple_song.artists;

    if download_song(&file_path, &corrected_song_name, artists, &cli_args).await {
        let album_art_file = format!("{}.jpeg", &corrected_album_name);
        album_art_dir.push(album_art_file);

        if let Some(cover_url) = song.cover_url {
            if let Err(err) = download_album_art(cover_url, &album_art_dir).await {
                println!("Unable to download {}'s album art!", song.album_name);
                error!("error downloading {}'s album art: {err}", song.album_name);
            };
        }
        metadata::add_metadata(file_path, album_art_dir, song.simple_song, song.album_name)
    }
}

pub async fn process_album_download(
    album: SpotifyAlbum,
    cli_args: CliArgs,
) -> Result<(), Box<dyn Error>> {
    let corrected_album_name = remove_illegal_path_characters(&album.name, true);
    let mut file_path = cli_args.download_dir.clone();
    file_path.push(&album.name);

    let Some(mut album_art_dir) = utils::create_download_directories(&cli_args.download_dir) else {
        return Ok(());
    };

    let album_art_file = format!("{}.jpeg", &corrected_album_name);
    album_art_dir.push(album_art_file);

    if let Some(cover_url) = album.cover_url {
        if let Err(err) = download_album_art(cover_url, &album_art_dir).await {
            println!("Unable to download {}'s album art!", album.name);
            error!("error downloading {}'s album art: {err}", album.name);
        };
    }
    println!("\nstarting album {} download", &album.name);

    let parallel_tasks_count: usize = if album.songs.len() >= cli_args.parallel_downloads as usize {
        cli_args.parallel_downloads as usize
    } else {
        album.songs.len()
    };

    let songs_per_task = (album.songs.len() + parallel_tasks_count - 1) / parallel_tasks_count;

    let cli_args = Arc::new(cli_args);
    let album_art_dir = Arc::new(album_art_dir);
    let album_name = Arc::new(album.name);

    let handles = album
        .songs
        .chunks(songs_per_task)
        .map(|chunk| {
            tokio::spawn(download_album_songs(
                file_path.clone(),
                cli_args.clone(),
                album_art_dir.clone(),
                album_name.clone(),
                chunk.to_vec(),
            ))
        })
        .collect::<Vec<_>>();

    for handle in handles {
        handle.await?;
    }

    println!("\nDownload for album {} completed, enjoy!", &album_name);
    Ok(())
}

pub async fn process_playlist_download(
    spotify_id: String,
    spotify_client: AuthCodeSpotify,
    playlist: SpotifyPlaylist,
    cli_args: CliArgs,
) -> Result<(), Box<dyn Error>> {
    let total_songs = playlist.total_songs;
    if total_songs == 0 || playlist.songs.is_empty() {
        println!("no songs to download in the playlist!");
        return Ok(());
    }

    let mut file_path = cli_args.download_dir.clone();
    file_path.push(&playlist.name);

    let Some( album_art_dir) = utils::create_download_directories(&cli_args.download_dir) else {
        return Ok(());
    };

    let mut offset = 0;
    let parallel_tasks_count: usize = if total_songs >= cli_args.parallel_downloads {
        cli_args.parallel_downloads as usize
    } else {
        total_songs as usize
    };

    let cli_args = Arc::new(cli_args);
    let mut song_details = playlist.songs;

    while total_songs > offset {
        if offset > 0 {
            match spotify::get_playlist_songs(&spotify_client, &spotify_id, offset).await {
                None => return Ok(()),
                Some(v) => song_details = v,
            };
        }

        if song_details.is_empty() {
            println!("no more songs left to download");
            return Ok(());
        }

        let songs_per_task = (song_details.len() + parallel_tasks_count - 1) / parallel_tasks_count;

        let unique_covers_map = spotify::get_unique_cover_urls(&song_details);
        let unique_covers: Vec<_> = unique_covers_map.into_iter().collect();

        if let Err(err) =
            download_album_covers(unique_covers, album_art_dir.clone(), parallel_tasks_count).await
        {
            error!("error in tokio thread when downloading album covers, propogating!");
            return Err(err);
        };

        let handles = song_details
            .chunks(songs_per_task)
            .map(|chunk| {
                tokio::spawn(download_playlist_songs(
                    file_path.clone(),
                    cli_args.clone(),
                    album_art_dir.clone(),
                    chunk.to_vec(),
                ))
            })
            .collect::<Vec<_>>();

        for handle in handles {
            if let Err(err) = handle.await {
                error!("error in tokio thread when downloading songs, propogating!");
                return Err(err.into());
            };
        }

        offset += 100;
    }

    println!(
        "\nDownload for playlist {} completed, enjoy!",
        &playlist.name
    );
    Ok(())
}
