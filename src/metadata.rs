use crate::{spotify, utils};

use std::fs::File;
use std::io::BufReader;

use lofty::{Accessor, Picture, Tag, TagExt, TaggedFileExt};

// TODO: maybe separate out the album art download function as well
// TODO: add flac support
// TODO: implement block_on tasks for this functions IO operations: lofty file read-write, picture operations
pub async fn add_metadata(download_dir: &str, file_path: &str, song: &spotify::SpotifySong) {
    let mut tagged_file = lofty::Probe::open(file_path).unwrap().read().unwrap();

    let tag = match tagged_file.primary_tag_mut() {
        Some(primary_tag) => primary_tag,
        None => {
            if let Some(first_tag) = tagged_file.first_tag_mut() {
                first_tag
            } else {
                // create, add and return a new tag
                let tag_type = tagged_file.primary_tag_type();

                tagged_file.insert_tag(Tag::new(tag_type));
                tagged_file.primary_tag_mut().unwrap()
            }
        }
    };

    let artists = song.artists.join(", ");
    tag.set_artist(artists);
    tag.set_title(song.name.clone());
    tag.set_album(song.album_name.clone());
    tag.set_disk(song.disc_number as u32);
    tag.set_track(song.track_number);

    let album_art_path = format!("{}/album-art/{}.jpeg", download_dir, &song.album_name);
    utils::download_album_art(song.cover_url.clone().unwrap(), &album_art_path).await;

    let album_art = File::open(album_art_path).unwrap();
    let mut reader = BufReader::new(album_art);

    let mut picture = Picture::from_reader(&mut reader).unwrap();
    picture.set_pic_type(lofty::PictureType::CoverFront);
    tag.push_picture(picture);

    tag.save_to_path(file_path).unwrap();
}
