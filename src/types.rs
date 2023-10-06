use std::path::PathBuf;

use crate::metadata;

#[derive(Debug)]
pub struct CliArgs {
    pub download_dir: PathBuf,
    pub codec: metadata::Codec,
    pub bitrate: metadata::Bitrate,
    pub parallel_downloads: u32,
}
