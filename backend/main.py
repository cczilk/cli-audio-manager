import sys
from player import MusicPlayer
from downloader import AudioDownloader
from database import Database
from ascii_art_defaults import get_random_art

class CLI:
    def __init__(self):
        print("Initializing Terminal Music Player...")
        self.player = MusicPlayer()
        self.downloader = AudioDownloader()
        self.db = Database()
        print("✓ Ready!\n")
    
    def show_help(self):
        """Display available commands"""
        print("\n=== Music Player Commands ===")
        print("  play [track_id]      - Play a track by ID")
        print("  pause                - Pause playback")
        print("  stop                 - Stop playback")
        print("  next                 - Skip to next track in queue")
        print("  prev                 - Go to previous track")
        print("  vol [0-100]          - Set volume (works in real-time!)")
        print("  now                  - Show currently playing track")
        print("  progress             - Show playback progress bar")
        print("")
        print("  shuffle              - Toggle shuffle mode")
        print("  repeat [off|one|all] - Set repeat mode (or cycle through)")
        print("")
        print("  list                 - List all tracks in library")
        print("  search [query]       - Search for tracks")
        print("  download [url]       - Download from YouTube/SoundCloud")
        print("  queue                - Show download queue")
        print("  process              - Process pending downloads")
        print("")
        print("  playlist list        - List all playlists")
        print("  playlist create [name] - Create new playlist")
        print("  playlist load [id]   - Load and play playlist")
        print("  playlist add [playlist_id] [track_id] - Add track to playlist")
        print("")
        print("  q                    - Show playback queue")
        print("  qadd [track_id]      - Add track to playback queue")
        print("  qclear               - Clear playback queue")
        print("")
        print("  art                  - Show album art for current track (ASCII)")
        print("")
        print("  help                 - Show this help")
        print("  exit                 - Quit the player")
        print("==============================\n")
    
    def list_tracks(self):
        """Display all tracks in library"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, artist, duration FROM tracks ORDER BY id")
        tracks = cursor.fetchall()
        conn.close()
        
        if not tracks:
            print("No tracks in library. Use 'download [url]' to add music!")
            return
        
        print("\n=== Music Library ===")
        print(f"{'ID':<5} | {'Title':<40} | {'Artist':<25} | Duration")
        print("-" * 90)
        
        for track_id, title, artist, duration in tracks:
            title = title or "Unknown Title"
            artist = artist or "Unknown Artist"

            minutes = int(duration) // 60
            seconds = int(duration) % 60
            duration_str = f"{minutes}:{seconds:02d}"
            
            title_short = title[:37] + "..." if len(title) > 40 else title
            artist_short = artist[:22] + "..." if len(artist) > 25 else artist
            
            print(f"{track_id:<5} | {title_short:<40} | {artist_short:<25} | {duration_str}")
        
        print(f"\nTotal tracks: {len(tracks)}\n")
    
    def search_tracks(self, query):
        """Search for tracks by title or artist"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, artist FROM tracks 
            WHERE title LIKE ? OR artist LIKE ?
            ORDER BY id
        ''', (f'%{query}%', f'%{query}%'))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            print(f"No tracks found matching '{query}'")
            return
        
        print(f"\n=== Search Results for '{query}' ===")
        for track_id, title, artist in results:
            print(f"{track_id:<5} | {title} - {artist}")
        print()
    
    def handle_play(self, args):
        """Handle play command"""
        if args:
            try:
                track_id = int(args[0])
                self.player.play(track_id)
            except ValueError:
                print("Error: Track ID must be a number")
            except Exception as e:
                print(f"Error playing track: {e}")
        else:
            if not self.player.play():
                print("Use: play [track_id] to play a track")
            
    def handle_download(self, args):
        """Handle download command"""
        if not args:
            print("Usage: download [url]")
            return
        
        url = args[0]
        
        if 'youtube.com' in url or 'youtu.be' in url:
            print(f"Downloading from YouTube: {url}")
        elif 'soundcloud.com' in url:
            print(f"Downloading from SoundCloud: {url}")
        else:
            print("Warning: Unknown platform, trying anyway...")
        
        result = self.downloader.download_from_youtube(url)
        
        if result:
            print(f"Successfully downloaded: {result['title']}")
            print(f"Track ID: {result['track_id']}")
        else:
            print("Download failed")
    
    def handle_download_queue(self):
        """Show download queue status"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, url, status FROM download_queue ORDER BY added_at")
        queue_items = cursor.fetchall()
        conn.close()
        
        if not queue_items:
            print("Download queue is empty")
            return
        
        print("\n=== Download Queue ===")
        for item_id, url, status in queue_items:
            status_symbol = "..." if status == "pending" else "✓" if status == "completed" else "✗"
            print(f"[{status_symbol}] {item_id}: {url}")
        print()
    
    def handle_playlist_list(self):
        """List all playlists"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, created_at FROM playlists ORDER BY id")
        playlists = cursor.fetchall()
        conn.close()
        
        if not playlists:
            print("No playlists. Create one with: playlist create [name]")
            return
        
        print("\n=== Playlists ===")
        for playlist_id, name, created_at in playlists:
            print(f"{playlist_id}: {name} (created {created_at})")
        print()
    
    def handle_playlist_create(self, args):
        """Create new playlist"""
        if not args:
            print("Usage: playlist create [name]")
            return
        
        name = ' '.join(args)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO playlists (name) VALUES (?)", (name,))
        playlist_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"Created playlist '{name}' (ID: {playlist_id})")
    
    def handle_playlist_add(self, playlist_id, track_id):
        """Add track to playlist"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM playlists WHERE id=?", (playlist_id,))
        if not cursor.fetchone():
            conn.close()
            print(f"Error: Playlist {playlist_id} not found")
            return
        
        cursor.execute("SELECT id FROM tracks WHERE id=?", (track_id,))
        if not cursor.fetchone():
            conn.close()
            print(f"Error: Track {track_id} not found")
            return
        
        cursor.execute(
            "SELECT MAX(position) FROM playlist_tracks WHERE playlist_id=?",
            (playlist_id,)
        )
        result = cursor.fetchone()
        next_position = (result[0] or 0) + 1
        
        try:
            cursor.execute('''
                INSERT INTO playlist_tracks (playlist_id, track_id, position)
                VALUES (?, ?, ?)
            ''', (playlist_id, track_id, next_position))
            
            conn.commit()
            print(f"Added track {track_id} to playlist {playlist_id}")
        except Exception as e:
            print(f"Error adding track to playlist: {e}")
        finally:
            conn.close()
    
    def display_now_playing(self):
        info = self.player.get_current_track_info()
        
        if not info:
            print("Nothing is currently playing")
            return
        
        pos_min = int(info['position']) // 60
        pos_sec = int(info['position']) % 60
        dur_min = int(info['duration']) // 60
        dur_sec = int(info['duration']) % 60
        
        status = "Playing" if info['is_playing'] else "Paused"
        
        print(f"\n{status}:")
        print(f"  {info['title']}")
        print(f"  by {info['artist']}")
        print(f"  [{pos_min}:{pos_sec:02d} / {dur_min}:{dur_sec:02d}]")
        print(f"  Volume: {info.get('volume', 50)}%")
        
        modes = []
        if info.get('shuffle'):
            modes.append("Shuffle")
        if info.get('repeat') != 'off':
            modes.append(f"Repeat: {info.get('repeat')}")
        if modes:
            print(f"  Modes: {', '.join(modes)}")
        
        print()
    
    def run(self):
        """Main command loop"""
        print("Welcome to Terminal Music Player!")
        self.show_help()
        
        while True:
            try:
                user_input = input(">> ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:]
                
                if command == 'help':
                    self.show_help()
                
                elif command in ('exit', 'quit'):
                    print("Goodbye!")
                    self.player.stop()
                    break
                
                elif command == 'play':
                    self.handle_play(args)
                
                elif command == 'pause':
                    self.player.pause()
                
                elif command == 'stop':
                    self.player.stop()
                
                elif command == 'next':
                    self.player.next_track()
                
                elif command == 'prev':
                    self.player.previous_track()
                
                elif command in ('vol', 'volume'):
                    if args:
                        try:
                            volume = int(args[0])
                            self.player.set_volume(volume)
                        except ValueError:
                            print("Volume must be a number (0-100)")
                    else:
                        print("Usage: vol [0-100]")
                
                elif command == 'now':
                    self.display_now_playing()
                
                elif command == 'progress':
                    progress = self.player.get_progress()
                    if progress:
                        print(f"\n[{progress['bar']}] {progress['time']} ({progress['percent']}%)\n")
                    else:
                        print("No track playing")
                
                elif command == 'list':
                    self.list_tracks()
                
                elif command == 'search':
                    if args:
                        query = ' '.join(args)
                        self.search_tracks(query)
                    else:
                        print("Usage: search [query]")
                
                elif command == 'download':
                    self.handle_download(args)
                
                elif command == 'queue':
                    self.handle_download_queue()
                
                elif command == 'process':
                    print("Processing download queue...")
                    self.downloader.process_queue()
                
                elif command == 'playlist':
                    if not args:
                        print("Usage: playlist [list|create|load|add]")
                    else:
                        subcmd = args[0].lower()
                        
                        if subcmd == 'list':
                            self.handle_playlist_list()
                        
                        elif subcmd == 'create':
                            self.handle_playlist_create(args[1:])
                        
                        elif subcmd == 'load':
                            if len(args) < 2:
                                print("Usage: playlist load [playlist_id]")
                            else:
                                try:
                                    playlist_id = int(args[1])
                                    self.player.load_playlist(playlist_id)
                                except ValueError:
                                    print("Playlist ID must be a number")
                        
                        elif subcmd == 'add':
                            if len(args) < 3:
                                print("Usage: playlist add [playlist_id] [track_id]")
                            else:
                                try:
                                    playlist_id = int(args[1])
                                    track_id = int(args[2])
                                    self.handle_playlist_add(playlist_id, track_id)
                                except ValueError:
                                    print("IDs must be numbers")
                        
                        else:
                            print(f"Unknown playlist command: {subcmd}")
                
                elif command == 'q':
                    self.player.show_queue()
                
                elif command == 'qadd':
                    if args:
                        try:
                            track_id = int(args[0])
                            self.player.add_to_queue(track_id)
                        except ValueError:
                            print("Track ID must be a number")
                    else:
                        print("Usage: qadd [track_id]")
                
                elif command == 'qclear':
                    self.player.clear_queue()
                
                elif command == 'shuffle':
                    self.player.toggle_shuffle()
                
                elif command == 'repeat':
                    if args:
                        mode = args[0].lower()
                        self.player.set_repeat(mode)
                    else:
                        self.player.cycle_repeat()
                
                elif command == 'art':
                    info = self.player.get_current_track_info()
                    if info:
                        conn = self.db.get_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT filepath FROM tracks WHERE id=?", (info['track_id'],))
                        result = cursor.fetchone()
                        conn.close()
                        
                        if result:
                            from metadata_extractor import MetadataExtractor
                            extractor = MetadataExtractor()
                            art_path = extractor.extract_album_art(result[0])
                            if art_path:
                                extractor.display_album_art_terminal(art_path)
                            else:
                                print("No album art found in this file")
                                print(get_random_art())
                    else:
                        print("No track currently playing")
                
                else:
                    print(f"Unknown command: {command}. Type 'help' for commands.")
            
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                self.player.stop()
                break
            
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    cli = CLI()
    cli.run()