import pytest
import mutagen
import mutagen.easyid3
import mutagen.flac

import os

import spotidl.metadata as package
from tests.test_spotify import generate_new_song
import spotidl.downloader as yt
import spotidl.utils as utils


@pytest.fixture()
def generate_metadata():
    return {
        # the metadata is converted to string before during the writing
        "title": ["Le sort de Circé"],
        "artist": ["Juliette"],
        "album": ["Mutatis mutandis"],
        "tracknumber": ["1"],
        "discnumber": ["1"],
    }


@pytest.fixture()
def generate_album_art():
    album_art_url = "https://i.scdn.co/image/ab67616d0000b273c91030650cb3fdf8c\
75394f0"

    download_path = utils.download_album_art(
        path=".", link=album_art_url, title="Mutatis mutandis"
    )

    return download_path


def test_add_metadata_mp3(
    generate_new_song,
    generate_metadata,
    generate_album_art,
):
    directory = "dl"
    file_name = f"{directory}/Juliette - Le sort de Circé.mp3"
    song = generate_new_song
    # since we haven't been downloading album art to the root folder,
    # we will be looking in the "dl" folder
    album_art_path = generate_album_art

    # calling the func
    package.add_metadata_mp3(file_name, song, album_art_path)

    try:
        meta = mutagen.easyid3.EasyID3(file_name)

    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(file_name, easy=True)
        meta.add_tags()

    song_info = generate_metadata

    assert meta["title"] == song_info["title"]
    assert meta["artist"] == song_info["artist"]
    assert meta["album"] == song_info["album"]
    assert meta["tracknumber"] == song_info["tracknumber"]
    assert meta["discnumber"] == song_info["discnumber"]


def test_add_metadata_flac(
    generate_new_song,
    generate_metadata,
    generate_album_art,
):
    directory = "dl"
    file_name = "Juliette - Le sort de Circé.flac"
    song = generate_new_song
    album_art_path = generate_album_art

    # changing the dir since FLAC seems to only accept song name and codec
    os.chdir(directory)

    # calling the func
    package.add_metadata_flac(file_name, song, album_art_path)

    meta = mutagen.flac.FLAC(file_name)

    song_info = generate_metadata

    assert meta["title"] == song_info["title"]
    assert meta["artist"] == song_info["artist"]
    assert meta["album"] == song_info["album"]
    assert meta["tracknumber"] == song_info["tracknumber"]
    assert meta["discnumber"] == song_info["discnumber"]

    os.chdir("..")


def test_controller_mp3(generate_new_song, generate_metadata):
    directory = "dl"
    codec = "mp3"
    song = generate_new_song
    file_name = f"{directory}/Juliette - Le sort de Circé.mp3"

    package.controller(file_name, song, directory, codec)

    try:
        meta = mutagen.easyid3.EasyID3(file_name)

    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(file_name, easy=True)
        meta.add_tags()

    song_info = generate_metadata

    assert meta["title"] == song_info["title"]
    assert meta["artist"] == song_info["artist"]
    assert meta["album"] == song_info["album"]
    assert meta["tracknumber"] == song_info["tracknumber"]
    assert meta["discnumber"] == song_info["discnumber"]


def test_controller_flac(generate_new_song, generate_metadata):

    directory = "dl"
    file_name = "Juliette - Le sort de Circé.flac"
    song = generate_new_song
    codec = "flac"

    # changing the dir since FLAC seems to only accept song name and codec
    os.chdir(directory)

    package.controller(file_name, song, ".", codec)

    meta = mutagen.flac.FLAC(file_name)

    song_info = generate_metadata

    assert meta["title"] == song_info["title"]
    assert meta["artist"] == song_info["artist"]
    assert meta["album"] == song_info["album"]
    assert meta["tracknumber"] == song_info["tracknumber"]
    assert meta["discnumber"] == song_info["discnumber"]

    os.chdir("..")


# def cleanup():
#     os.remove("dl/Juliette - Le sort de Circé.flac")
#     os.remove("dl/Juliette - Le sort de Circé.mp3")
#     os.remove("dl/album-art/Mutatis mutandis.jpeg")
