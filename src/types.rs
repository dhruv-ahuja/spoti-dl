use std::path::PathBuf;

use crate::metadata;

#[derive(Debug)]
pub struct CliArgs {
    download_dir: PathBuf,
    codec: metadata::Codec,
    bitrate: metadata::Bitrate,
    parallel_downloads: u32,
}
