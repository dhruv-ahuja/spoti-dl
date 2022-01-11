# Introduction

yet Another Song Downloader, yASD for short(I couldn't think of a better name, sorry!), is a song downloader app that accepts Spotify links, fetches individual song—and basic album—metadata from Spotify, downloads the song from Youtube. The metadata is then written onto the downloaded song file using the trusty Mutagen library, this includes the album/song cover art as well. 

The app currently supports downloading songs, albums and playlists in the mp3, flac and m4a formats(the m4a format right now does not have full textual metadata support but I'm working on it 😅). 

I got the inspiration for the project from my friend Swapnil's [spotify-dl](https://github.com/SwapnilSoni1999/spotify-dl) app written in JavaScript. This seemed like the perfect pet project to make and consequently learn from :)


# Setup

yASD needs two things to work: [FFmpeg](https://ffmpeg.org/download.html) and a Spotify developer account.

Steps to make a Spotify developer account:
1. Go to [Spotify Dev Dashboard](https://developer.spotify.com/dashboard/applications)
2. Login with your credentials and click on "create an app".
3. Enter any name of choice, app description, tick the checkbox and proceed.
4. Now you have access to your client ID. Click on "Show client secret" to get your client secret.
5. From here, click on "edit settings" and in the "redirect URIs" section add any localhost URL. I personally use ```http://localhost:8080/callback```

Finally, copy your client ID, client secret and the redirect URI and paste them in the .env.example file opposite the appropriate variables. Rename the .env.example file to .env and you're good to go!


# Usage

WIP
