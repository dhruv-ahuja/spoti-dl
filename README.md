[![Downloads](https://pepy.tech/badge/spoti-dl)](https://pepy.tech/project/spoti-dl)
[![Downloads](https://pepy.tech/badge/spoti-dl/month)](https://pepy.tech/project/spoti-dl)


# Introduction

spoti-dl(I had a better name but that was already taken on PyPi), is a song downloader app that accepts Spotify links, fetches individual song—and basic album—metadata from Spotify, downloads the song from Youtube. The metadata is then written onto the downloaded song file using the trusty Mutagen library, this includes the album/song cover art as well. 

The app currently supports downloading songs, albums and playlists. 

# Setup

Run ```pip install spoti-dl``` to install the app first and foremost.

spoti-dl needs two things to work: [FFmpeg](https://ffmpeg.org/download.html) and a Spotify developer account.

Steps to make a Spotify developer account:
1. Go to [Spotify Dev Dashboard](https://developer.spotify.com/dashboard/applications)
2. Login with your credentials and click on "create an app".
3. Enter any name of choice, app description, tick the checkbox and proceed.
4. Now you have access to your client ID. Click on "Show client secret" to get your client secret.
5. From here, click on "edit settings" and in the "redirect URIs" section add any localhost URL. I personally use ```http://localhost:8080/callback```

Finally, define these three environment variables: 
```
SPOTIPY_CLIENT_ID
SPOTIPY_CLIENT_SECRET
SPOTIPY_REDIRECT_URI
```

Also note that the first time you run the app you might get a popup window in your browser asking to integrate your account to the app you just created in the Spotify app dashboard. Accept and close the window.

# Usage

```
spotidl <spotify link>
``` 

as an example, running this would download Rick Astley's 'Never Gonna Give You Up'- 
```
spotidl https://open.spotify.com/track/4PTG3Z6ehGkBFwjybzWkR8?si=06f5d7ab5bd240e7
```

The following audio formats are supported:
- mp3 
- flac

The following bitrates are supported:
- best 
- 320kbps
- 256kbps 
- 192kbps (slightly better than Spotify's 'high' audio setting, this is the bare minimum in my opinion to have a good listening experience)
- 96kbps
- 32kbps
- worst

Again, the following link types are supported:
- song links
- album links
- playlist links 

Note: File names (audio files or folder names (eg., playlist's directory name) are changed to ensure compatibility with the operating systems since many characters like '?' or the '/' are illegal when making files/folders.

## Flags
 
| Flag  | Long Flag         | Usage                                                                   |
| ----- | ----------------- | ----------------------------------------------------------------------- |
| -h    | --help            | shows all the argument flags and their details                          |
| -d    | --dir             | the save directory to use while downloading                             |
| -q    | --quiet           | changes the verbosity level to be "quiet"                               |
| -c    | --codec           | the codec to use for downloads                                          |
| -b    | --bitrate         | set the bitrate to use for downloads                                    |
| -v    | --version         | displays the current app version                                        |
