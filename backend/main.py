"""
Main interface for which users will interact with
Creates a loop that will read user commands ie, play, pause etc
Parse user input with .split() to separate commands and arguments
CLI will run forever until user types "exit" or presses CTRL+C
"""
import sys
from player import MusicPlayer
from downloader import AudioDownloader
from database import Database

class CLI:
    def __init__(self):
        print("Initializing Terminal Music Player...")
        self.player = MusicPlayer()
        self.downloader = AudioDownloader()
        self.db = Database()
        print("✓ Ready!\n")
    
    def show_help(self):
        """
        Display available commands
        """
        print("\n=== Music Player Commands ===")
        print("  play [track_id]      - Play a track by ID (or resume if no ID)")
        print("  pause                - Pause playback")
        print("  stop                 - Stop playback")
        print("  next                 - Skip to next track in queue")
        print("  prev                 - Go to previous track")
        print("  vol [0-100]          - Set volume")
        print("  now                  - Show currently playing track")
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
        print("  help                 - Show this help")
        print("  exit                 - Quit the player")
        print("==============================\n")
    
    def list_tracks(self):
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
            # Convert duration from seconds to MM:SS format
            minutes = int(duration) // 60
            seconds = int(duration) % 60
            duration_str = f"{minutes}:{seconds:02d}"
            
            # Truncate long titles/artists
            title_short = title[:37] + "..." if len(title) > 40 else title
            artist_short = artist[:22] + "..." if len(artist) > 25 else artist
            
            print(f"{track_id:<5} | {title_short:<40} | {artist_short:<25} | {duration_str}")
        
        print(f"\nTotal tracks: {len(tracks)}\n")
    
    def search_tracks(self, query):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Search in both title and artist fields (case insensitive)
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
        if args:
            # Play specific track
            try:
                track_id = int(args[0])
                self.player.play(track_id)
            except ValueError:
                print("Error: Track ID must be a number")
        else:
            # Resume playback
            self.player.play()
    
    def handle_download(self, args):
        if not args:
            print("Usage: download [url]")
            return
        
        url = args[0]
        
        # Determine platform 
        if 'youtube.com' in url or 'youtu.be' in url:
            print(f"Downloading from YouTube: {url}")
        elif 'soundcloud.com' in url:
            print(f"Downloading from SoundCloud: {url}")
        else:
            print("Warning: Unknown platform, trying anyway...")
        
        # Start download 
        result = self.downloader.download_from_youtube(url)
        
        if result:
            print(f"✓ Successfully downloaded: {result['title']}")
            print(f"  Track ID: {result['track_id']}")
        else:
            print("✗ Download failed")
    
    def handle_download_queue(self):
        """
        Show download queue status
        """
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
            status_emoji = "⏳" if status == "pending" else "✓" if status == "completed" else "✗"
            print(f"{status_emoji} {item_id}: {url} [{status}]")
        print()
    
    def handle_playlist_list(self):
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
        if not args:
            print("Usage: playlist create [name]")
            return
        
        name = ' '.join(args)  # Join all args as playlist name
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO playlists (name) VALUES (?)", (name,))
        playlist_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✓ Created playlist '{name}' (ID: {playlist_id})")
    
    def handle_playlist_add(self, playlist_id, track_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Verify playlist exists
        cursor.execute("SELECT id FROM playlists WHERE id=?", (playlist_id,))
        if not cursor.fetchone():
            conn.close()
            print(f"Error: Playlist {playlist_id} not found")
            return
        
        # Verify track exists
        cursor.execute("SELECT id FROM tracks WHERE id=?", (track_id,))
        if not cursor.fetchone():
            conn.close()
            print(f"Error: Track {track_id} not found")
            return
        
        # Get next position in playlist
        cursor.execute(
            "SELECT MAX(position) FROM playlist_tracks WHERE playlist_id=?",
            (playlist_id,)
        )
        result = cursor.fetchone()
        next_position = (result[0] or 0) + 1
        
        # Add track to playlist
        try:
            cursor.execute('''
                INSERT INTO playlist_tracks (playlist_id, track_id, position)
                VALUES (?, ?, ?)
            ''', (playlist_id, track_id, next_position))
            
            conn.commit()
            print(f"✓ Added track {track_id} to playlist {playlist_id}")
        except Exception as e:
            print(f"Error adding track to playlist: {e}")
        finally:
            conn.close()
    
    def display_now_playing(self):
        """
        Show currently playing track with progress
        """
        info = self.player.get_current_track_info()
        
        if not info:
            print("Nothing is currently playing")
            return
        
        # Format time
        pos_min = int(info['position']) // 60
        pos_sec = int(info['position']) % 60
        dur_min = int(info['duration']) // 60
        dur_sec = int(info['duration']) % 60
        
        status = "▶" if info['is_playing'] else "⏸"
        
        print(f"\n{status} Now Playing:")
        print(f"  {info['title']}")
        print(f"  by {info['artist']}")
        print(f"  [{pos_min}:{pos_sec:02d} / {dur_min}:{dur_sec:02d}]")
        print(f"  Volume: {info.get('volume', 50)}%")
        print()
    
    def run(self):
        """
        Main command loop
        
        How this works:
        1. Display welcome message and help
        2. Loop forever:
           - Show prompt ">> "
           - Get user input
           - Split input into command and arguments
           - Call appropriate handler based on command
           - Handle errors gracefully
        3. Exit on "exit" command or Ctrl+C
        """
        print("♪ Welcome to Terminal Music Player! ♪")
        self.show_help()
        
        while True:
            try:
                # Get user input
                user_input = input(">> ").strip()
                
                if not user_input:
                    continue
                
                # Split into command and arguments
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:]
                
                # Handle commands
                if command == 'help':
                    self.show_help()
                
                elif command in ('exit', 'quit'):
                    print("Goodbye!")
                    self.player.stop()  # Clean up audio before exiting
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
                            if 0 <= volume <= 100:
                                self.player.set_volume(volume)
                            else:
                                print("Volume must be between 0 and 100")
                        except ValueError:
                            print("Volume must be a number (0-100)")
                    else:
                        print("Usage: vol [0-100]")
                
                elif command == 'now':
                    self.display_now_playing()
                
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
                            print("Usage: playlist [list|create|load|add]")
                
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
                
                else:
                    print(f"Unknown command: {command}. Type 'help' for commands.")
            
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                self.player.stop()  # Clean up audio before exiting
                break
            
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    cli = CLI()
    cli.run()