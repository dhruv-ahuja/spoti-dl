use std::collections::HashSet;
use std::fmt;
use std::path::PathBuf;
use std::str::FromStr;

use lazy_static::lazy_static;

#[derive(Debug)]
pub struct CliArgs {
    pub download_dir: PathBuf,
    pub codec: Codec,
    pub bitrate: Bitrate,
    pub add_track_number: bool,
    pub parallel_downloads: u32,
}

pub const SPOTIFY_ERROR_MSG: &str =
    "Encountered an error fetching details from Spotify. Please check your input \
Spotify link!\nIf the issue persists, please share the log file (located at ~/.spotidl.log) on the \
spoti-dl Github repo (https://github.com/dhruv-ahuja/spoti-dl)";

pub const INTERNAL_ERROR_MSG: &str =
    "Something went wrong! If the issue persists, please share the log file (located at ~/.spotidl.log) on the \
spoti-dl Github repo (https://github.com/dhruv-ahuja/spoti-dl)";

lazy_static! {
    pub static ref ILLEGAL_PATH_CHARS: HashSet<char> = ['?', '%', '*', '|', '"', '<', '>', '.']
        .iter()
        .cloned()
        .collect();
}

#[derive(Debug, PartialEq)]
pub enum Codec {
    MP3,
    Flac,
    M4A,
    Opus,
}

impl FromStr for Codec {
    type Err = ();
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "mp3" => Ok(Codec::MP3),
            "flac" => Ok(Codec::Flac),
            "m4a" => Ok(Codec::M4A),
            "opus" => Ok(Codec::Opus),
            _ => Err(()),
        }
    }
}

impl fmt::Display for Codec {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Codec::MP3 => write!(f, "mp3"),
            Codec::Flac => write!(f, "flac"),
            Codec::M4A => write!(f, "m4a"),
            Codec::Opus => write!(f, "opus"),
        }
    }
}

#[derive(Debug, PartialEq)]
pub enum Bitrate {
    Worst,
    Worse = 32,
    Poor = 96,
    Low = 128,
    Medium = 192,
    Good = 256,
    High = 320,
    Best,
}

impl FromStr for Bitrate {
    type Err = ();

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "worst" => Ok(Bitrate::Worst),
            "32" => Ok(Bitrate::Worse),
            "96" => Ok(Bitrate::Poor),
            "128" => Ok(Bitrate::Low),
            "192" => Ok(Bitrate::Medium),
            "256" => Ok(Bitrate::Good),
            "320" => Ok(Bitrate::High),
            "best" => Ok(Bitrate::Best),
            _ => Err(()),
        }
    }
}

impl fmt::Display for Bitrate {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Bitrate::Worst => write!(f, "worst"),
            Bitrate::Worse => write!(f, "worse"),
            Bitrate::Poor => write!(f, "poor"),
            Bitrate::Low => write!(f, "low"),
            Bitrate::Medium => write!(f, "medium"),
            Bitrate::Good => write!(f, "good"),
            Bitrate::High => write!(f, "high"),
            Bitrate::Best => write!(f, "best"),
        }
    }
}
