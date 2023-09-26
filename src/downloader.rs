use crate::{spotify, utils, CliArgs};

use std::path::Path;

use youtube_dl::YoutubeDl;

pub async fn download_song(file_path: &Path, song: &spotify::SpotifySong, args: &CliArgs) -> bool {
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
