use crate::spotify;

use std::fmt;
use std::fs::File;
use std::io::BufReader;
use std::path::PathBuf;
use std::str::FromStr;

use lofty::{Accessor, Picture, Tag, TagExt, TaggedFileExt};

#[derive(Debug, PartialEq)]
pub enum Codec {
    MP3,
    Flac,
}

impl FromStr for Codec {
    type Err = ();
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "mp3" => Ok(Codec::MP3),
            "flac" => Ok(Codec::Flac),
            _ => Err(()),
        }
    }
}

impl fmt::Display for Codec {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Codec::MP3 => write!(f, "mp3"),
            Codec::Flac => write!(f, "flac"),
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

pub fn add_metadata(
    file_path: &PathBuf,
    album_art_path: &PathBuf,
    simple_song: &spotify::SimpleSong,
    album_name: &str,
) {
    println!("adding metadata for {}", simple_song.name);
    let mut tagged_file = lofty::Probe::open(file_path).unwrap().read().unwrap();

    let tag = match tagged_file.primary_tag_mut() {
        Some(primary_tag) => primary_tag,
        None => {
            if let Some(first_tag) = tagged_file.first_tag_mut() {
                first_tag
            } else {
                // create, add and return a new tag
                let tag_type = tagged_file.primary_tag_type();
                println!("using tag type: {:?}", &tag_type);

                tagged_file.insert_tag(Tag::new(tag_type));
                tagged_file.primary_tag_mut().unwrap()
            }
        }
    };

    let artists = simple_song.artists.join(", ");
    tag.set_artist(artists);
    tag.set_title(simple_song.name.clone());
    tag.set_album(album_name.to_string());
    tag.set_disk(simple_song.disc_number as u32);
    tag.set_track(simple_song.track_number);

    let album_art = File::open(album_art_path).unwrap();
    let mut reader = BufReader::new(album_art);

    let mut picture = Picture::from_reader(&mut reader).unwrap();
    picture.set_pic_type(lofty::PictureType::CoverFront);

    tag.push_picture(picture);
    tag.save_to_path(file_path).unwrap();

    println!("successfully added metadata for {}", simple_song.name);
}
