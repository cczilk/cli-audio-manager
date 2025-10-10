# cli-audio-manager
Terminal-based audio player with web interface for managing YouTube/SoundCloud downloads and playlists.
### Web Interface
<img width="1886" height="907" alt="image" src="https://github.com/user-attachments/assets/101a7253-118a-4f58-99b5-44f83b8179d3" />

### ClI Player
<img width="889" height="911" alt="image" src="https://github.com/user-attachments/assets/49bb72e6-72c3-4194-819c-3fec0b34e1d4" />


## Features
- Download music from SoundCloud & YouTube
- Terminal-inspired UI with built-in terminal for CLI commands
- Organize tracks by artist with folder tree view
- Playback controls (play, pause, next, previous, volume)
- Playlist management
- Album art extraction from downloads
- Web interface + CLI interface

## Tech Stack
**Backend:** Python, Flask, yt-dlp, mpv, SQLite  
**Frontend:** React, Tailwind CSS, xterm.js

## Installation
**Prerequisites:** Python 3+, Node.js 16+, mpv, ffmpeg

## Project Structure

```
cli-audio-manager/
├── backend/
│ ├── main.py # CLI interface
│ ├── api.py # Flask REST API
│ ├── player.py # Audio playback
│ ├── downloader.py # YouTube/SoundCloud downloader
│ ├── queue_manager.py # Track queue management
│ ├── database.py # SQLite database interactions
│ ├── metadata_extractor.py # Album art & metadata extraction
│ └── downloads/ # Downloaded music
├── frontend/
│ ├── src/ # React app source code
│ ├── public/ # Static assets
│ ├── index.html
│ ├── package.json
│ └── tailwind.config.js
├── LICENSE
└── README.md
```
