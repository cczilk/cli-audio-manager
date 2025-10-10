# cli-audio-manager
terminal based audio player with web-interface for managing youtube/soundcloud downloads and playlists
<img width="1886" height="907" alt="image" src="https://github.com/user-attachments/assets/101a7253-118a-4f58-99b5-44f83b8179d3" />

## Features
-Download music from Soundcloud & Youtube
-Terminal inspired UI with with built in terminal for CLI commands
-Organize tracks by artist with folder tree view
-Playback controlls (play, pause, next, previous, volume)
-Playlist managment
-Album art extraction from downloads
-Web interface + CLI interface

##
Backend: Python, Flask, yt-dlp, mpv, SQLite
Frontend: React, Tailwind CSS, xterm.js

## Installation
Prerequisites: Python 3+, Node.js 16+, mpv, ffmpeg

## Project Structure
cli-audio-manager/
├── backend/
│   ├── main.py               # CLI interface
│   ├── api.py                # Flask REST API
│   ├── player.py             # Audio playback
│   ├── downloader.py         # YouTube/SoundCloud downloader
│   ├── queue_manager.py      # Track queue management
│   ├── database.py           # SQLite database interactions
│   ├── metadata_extractor.py # Album art & metadata extraction
│   └── downloads/            # Downloaded music
├── frontend/
│   ├── src/                  # React app source code
│   ├── public/               # Static assets
│   ├── index.html
│   ├── package.json
│   └── tailwind.config.js
├── LICENSE
└── README.md
