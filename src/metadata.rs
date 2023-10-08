use crate::spotify;

use std::fmt::Debug;
use std::fs::File;
use std::io::BufReader;
use std::path::Path;

use lofty::{Accessor, Picture, Tag, TagExt, TaggedFileExt};
use log::error;

/// Adds metadata for the downloaded song given its path and requisite metadata information
pub fn add_metadata<P, S>(
    file_path: P,
    album_art_path: P,
    simple_song: spotify::SimpleSong,
    album_name: S,
) where
    P: AsRef<Path> + Debug,
    S: Into<String>,
{
    let error_msg = format!("Unable to write metadata for {} song!", simple_song.name);

    let mut tagged_file = match lofty::Probe::open(&file_path) {
        Err(err) => {
            println!("{error_msg}");
            error!(
                "error {} opening song file {:?} for writing metadata",
                err, file_path
            );
            return;
        }
        Ok(file) => match file.read() {
            Err(err) => {
                println!("{error_msg}");
                error!(
                    "error {} reading song file {:?} for writing metadata",
                    err, file_path
                );
                return;
            }
            Ok(tf) => tf,
        },
    };

    let tag = match tagged_file.primary_tag_mut() {
        Some(primary_tag) => primary_tag,
        None => {
            if let Some(first_tag) = tagged_file.first_tag_mut() {
                first_tag
            } else {
                // create, add and return a new tag
                let tag_type = tagged_file.primary_tag_type();

                tagged_file.insert_tag(Tag::new(tag_type));

                match tagged_file.primary_tag_mut() {
                    None => {
                        println!("{error_msg}");
                        error!("unable to add metadata tag to song file {:?}", file_path);
                        return;
                    }
                    Some(v) => v,
                }
            }
        }
    };

    let artists = simple_song.artists.join(", ");
    tag.set_artist(artists);
    tag.set_title(simple_song.name.clone());
    tag.set_album(album_name.into());
    tag.set_disk(simple_song.disc_number as u32);
    tag.set_track(simple_song.track_number);

    let album_art = match File::open(&album_art_path) {
        Err(err) => {
            println!("{error_msg}");
            error!("error {} reading album art file {:?}", err, album_art_path);
            return;
        }
        Ok(v) => v,
    };
    let mut reader = BufReader::new(album_art);

    let mut picture = match Picture::from_reader(&mut reader) {
        Err(err) => {
            println!("{error_msg}");
            error!("error {} reading album art file {:?}", err, album_art_path);
            return;
        }
        Ok(v) => v,
    };

    picture.set_pic_type(lofty::PictureType::CoverFront);
    tag.push_picture(picture);

    if let Err(err) = tag.save_to_path(file_path) {
        println!("{error_msg}");
        error!(
            "error {} saving file {:?} after writing metadata",
            err, album_art_path
        );
    }
}
