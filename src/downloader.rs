use crate::spotify::{SimpleSong, SpotifyAlbum, SpotifyPlaylist, SpotifySong};
use crate::types::{CliArgs, INTERNAL_ERROR_MSG};
use crate::utils::{self, correct_path_names, download_album_art};
use crate::{metadata, spotify};

use std::error::Error;
use std::path::{Path, PathBuf};
use std::sync::Arc;

use colored::Colorize;
use log::error;
use rspotify::AuthCodeSpotify;
use youtube_dl::YoutubeDl;

pub async fn download_song(
    file_path: &Path,
    song_name: &str,
    artists: &[String],
    track_number: Option<u32>,
    cli_args: &CliArgs,
) -> bool {
    let parent_dir_display = match file_path.parent() {
        None => {
            println!("{}", INTERNAL_ERROR_MSG.red());
            error!(
                "no parent found for file path {:?} during download",
                file_path.display()
            );
            return false;
        }
        Some(v) => v.display(),
    };
    let file_output_format = if cli_args.add_track_number {
        format!(
            "{}/{} {}.%(ext)s",
            parent_dir_display,
            track_number.unwrap(),
            song_name
        )
    } else {
        format!("{}/{}.%(ext)s", parent_dir_display, song_name)
    };

    if file_path.exists() {
        let path_exists_msg =
            format!("{} already exists, skipping download", song_name).bright_yellow();
        println!("{path_exists_msg}");
        return false;
    }

    let query = utils::generate_youtube_query(song_name, artists);
    let search_options = youtube_dl::SearchOptions::youtube(query);

    let mut yt_client = YoutubeDl::search_for(&search_options);
    let download_start_msg = format!("Starting {} download", song_name).cyan();
    println!("{download_start_msg}");

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
        let error_msg = format!("Unable to download {} song!", &song_name).red();
        println!("{error_msg}");
        error!("error {err} downloading {song_name} song");
        return false;
    }

    let download_completed_msg = format!("{} downloaded", song_name).green();
    println!("{download_completed_msg}");
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
        let corrected_song_name = correct_path_names(&song.name, true);

        let file_name = format!("{}.{}", corrected_song_name, cli_args.codec);
        file_path.push(&file_name);

        let track_number = if cli_args.add_track_number {
            Some(song.track_number)
        } else {
            None
        };

        if download_song(
            &file_path,
            &corrected_song_name,
            &song.artists,
            track_number,
            &cli_args,
        )
        .await
        {
            if cli_args.add_track_number {
                file_path.pop();
                file_path.push(format!("{} {}", song.track_number, file_name));
            }
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
                    let error_msg = format!("Unable to download {album_name}'s album art!").red();
                    println!("{error_msg}");
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

        let track_number = if cli_args.add_track_number {
            Some(item.simple_song.track_number)
        } else {
            None
        };

        if download_song(
            &file_path,
            &song_name,
            &item.simple_song.artists,
            track_number,
            &cli_args,
        )
        .await
        {
            if cli_args.add_track_number {
                file_path.pop();
                file_path.push(format!("{} {}", item.simple_song.track_number, file_name));
            }
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
    let corrected_song_name = correct_path_names(&song.simple_song.name, true);
    let corrected_album_name = correct_path_names(&song.album_name, true);

    let Some(mut album_art_dir) = utils::create_download_directories(&cli_args.download_dir) else {
        return;
    };

    let file_name = format!("{}.{}", corrected_song_name, cli_args.codec);
    let mut file_path = cli_args.download_dir.clone();

    file_path.push(&file_name);
    let artists = &song.simple_song.artists;

    let track_number = if cli_args.add_track_number {
        Some(song.simple_song.track_number)
    } else {
        None
    };

    if download_song(
        &file_path,
        &corrected_song_name,
        artists,
        track_number,
        &cli_args,
    )
    .await
    {
        if cli_args.add_track_number {
            file_path.pop();
            file_path.push(format!("{} {}", song.simple_song.track_number, file_name));
        }
        let album_art_file = format!("{}.jpeg", &corrected_album_name);
        album_art_dir.push(album_art_file);

        if let Some(cover_url) = song.cover_url {
            if let Err(err) = download_album_art(cover_url, &album_art_dir).await {
                let error_msg =
                    format!("Unable to download {}'s album art!", song.album_name).red();
                println!("{error_msg}");
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
    let corrected_album_name = correct_path_names(&album.name, true);
    let mut file_path = cli_args.download_dir.clone();
    file_path.push(&album.name);

    let Some(mut album_art_dir) = utils::create_download_directories(&cli_args.download_dir) else {
        return Ok(());
    };

    let album_art_file = format!("{}.jpeg", &corrected_album_name);
    album_art_dir.push(album_art_file);

    if let Some(cover_url) = album.cover_url {
        if let Err(err) = download_album_art(cover_url, &album_art_dir).await {
            let error_msg = format!("Unable to download {}'s album art!", album.name).red();
            println!("{error_msg}");
            error!("error downloading {}'s album art: {err}", album.name);
        };
    }
    let download_start_msg = format!("starting album {} download", album.name).cyan();
    println!("{download_start_msg}");

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

    let download_completed_msg =
        format!("Download for album {} completed, enjoy!", album_name).green();
    println!("{download_completed_msg}");
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
        let no_songs_msg = "no songs to download in the playlist!"
            .to_string()
            .bright_yellow();

        println!("{no_songs_msg}");
        return Ok(());
    }

    let mut file_path = cli_args.download_dir.clone();
    file_path.push(&playlist.name);

    let Some(album_art_dir) = utils::create_download_directories(&cli_args.download_dir) else {
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

    let start_download_msg = format!(
        "starting playlist {} download. Any podcast episodes in the playlist will be skipped!",
        playlist.name
    )
    .cyan();
    println!("{start_download_msg}");

    while total_songs > offset {
        if offset > 0 {
            match spotify::get_playlist_songs(&spotify_client, &spotify_id, offset).await {
                None => {
                    println!("{}", INTERNAL_ERROR_MSG.red());
                    return Ok(());
                }
                Some(v) => song_details = v,
            };
        }

        if song_details.is_empty() {
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

    let download_completed_msg =
        format!("Download for playlist {} completed, enjoy!", &playlist.name).green();
    println!("{download_completed_msg}");
    Ok(())
}
