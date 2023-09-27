use crate::{spotify, utils, CliArgs};

use std::path::Path;

use youtube_dl::YoutubeDl;

pub async fn download_song(
    file_path: &Path,
    song_name: &str,
    artists: &[String],
    args: &CliArgs,
) -> bool {
    let file_output_format = format!("{}/{}.%(ext)s", &args.download_dir.display(), song_name);

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
        println!("\nError downloading {} song: {err}", song_name);
        return false;
    }
    println!("{} downloaded", song_name);
    true
}
