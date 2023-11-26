# spoti-dl

[![Downloads](https://pepy.tech/badge/spoti-dl)](https://pepy.tech/project/spoti-dl)
[![Downloads](https://pepy.tech/badge/spoti-dl/month)](https://pepy.tech/project/spoti-dl)

## Introduction

spoti-dl(I had a better name but that was already taken on PyPi), is a song downloader app that accepts Spotify links, fetches songs and and their albums' information from Spotify, downloads the song from Youtube. The metadata is then written onto the downloaded song file, including the album art cover.

It supports downloading songs, albums and playlists as podcast episodes cannot be reliably downloaded through Youtube.

## Version 2.0.0 Update

The version 2.0.0 update introduces several improvements. I've shifted the app to be predominantly Rust-based, all core functionality is now written in Rust, which should result in about 20-25% performance improvement directly.

Albums and playlists are now downloaded in parallel, with 5 songs being downloaded in parallel by default. This has allowed for massive speedups - a 19-song album that earlier took about 115 seconds to download now took me roughly 25 seconds, that's more than a 4.5x speedup. You can download faster if you increase the number of parallel downloads, by setting the `-p` flag.
This fixes a big issue with the app which was the unreasonable download times for albums and playlists, which can easily have 500 or even 1000 songs.

I have also cleaned up the error messages, added error-logging to a file (`~/.spotidl.log`), color coded output messages and made several other minor improvements. All in all, the app should feel much better to use now :)

The main reason to use FFI with Rust was mostly just to code in Rust, and also get some extra performance out of the application. I have been enjoying Rust a lot lately and Python has always been nice to work with too.

## Setup

Run ```pip install spoti-dl``` to install the app first and foremost.

spoti-dl needs two things to work: [FFmpeg](https://ffmpeg.org/download.html) and a Spotify developer account.

Steps to make a Spotify developer account:

1. Go to [Spotify Dev Dashboard](https://developer.spotify.com/dashboard/applications)
2. Login with your credentials and click on "create an app".
3. Enter any name of choice, app description, tick the checkbox and proceed.
4. Now you have access to your client ID. Click on "Show client secret" to get your client secret.
5. From here, click on "edit settings" and in the "redirect URIs" section add any localhost URL. I personally use ```http://localhost:8080/callback```

Finally, define these three environment variables:

```bash
SPOTIPY_CLIENT_ID
SPOTIPY_CLIENT_SECRET
SPOTIPY_REDIRECT_URI
```

Also note that the first time you run the app you might get a popup window in your browser asking to integrate your account to the app you just created in the Spotify app dashboard. Accept and close the window. The window will automatically close if you've already granted access to the app in the past.

## Usage

**Note**: Please try updating `yt-dlp` through `pip` if encountering random download failures.

```bash
spoti-dl <spotify URL or URI> 
```

as an example, running either of the commands would download Rick Astley's 'Never Gonna Give You Up':

```bash
spoti-dl https://open.spotify.com/track/4PTG3Z6ehGkBFwjybzWkR8
```

```bash
spoti-dl spotify:track:4PTG3Z6ehGkBFwjybzWkR8
```

The following audio formats are supported:

- mp3
- flac
- m4a
- opus (default)

The following bitrates are supported:

- best (default)
- 320kbps
- 256kbps
- 192kbps (slightly better than Spotify's 'high' audio setting, this is the bare minimum in my opinion to have a good listening experience)
- 96kbps
- 32kbps
- worst

Again, the following link types are supported:

- song,
- album, and
- playlist links

**Note**: File names (audio files or folder names (eg., playlist's directory name)) are changed to ensure compatibility with the operating systems since many characters like '?' or the '/' are illegal when making files/folders in certain systems and are removed during the downloads.

## Flags

| Flag | Long Flag            | Usage                                                       |
| ---- | -------------------- | ----------------------------------------------------------- |
| -h   | --help               | shows all the argument flags and their details              |
| -d   | --dir                | the save directory to use while downloading                 |
| -c   | --codec              | the codec to use for downloads                              |
| -b   | --bitrate            | set the bitrate to use for downloads                        |
| -t   | --track-number       | prepend downloaded song names with their track order number |
| -p   | --parallel-downloads | maximum number of parallel song downloads                   |
| -v   | --version            | displays the current app version                            |

## TODO

- [ ] add tests
