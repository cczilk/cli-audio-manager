import subprocess
import os
import json
import socket
import time
import random
import threading
from database import Database

class MusicPlayer:
    def __init__(self):
        """
        Initialize player with advanced playback features
        """
        self.current_process = None
        self.current_track_id = None
        self.is_playing = False
        self.is_paused = False
        self.queue = [] 
        self.current_queue_index = -1
        self.db = Database()
        self.volume = 50
        self.socket_path = '/tmp/mpv-socket'
        
        self.shuffle_mode = False
        self.repeat_mode = 'off'  # 'off', 'one', 'all'
        self.original_queue = []  # Store original order for shuffle toggle
        
        self.monitor_thread = None
        self.should_monitor = False
        
    def _send_command(self, command):
        """Send command to mpv via IPC socket"""
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_path)
            sock.send((json.dumps(command) + '\n').encode('utf-8'))
            sock.close()
            return True
        except Exception:
            return False

    def _monitor_playback(self):
        """
        Monitor playback and auto-play next track when current ends
        """
        while self.should_monitor:
            if self.current_process and self.current_process.poll() is not None:
                if self.is_playing and not self.is_paused:
                    if self.repeat_mode == 'one':
                        self.play(self.current_track_id)
                    elif self.queue and self.current_queue_index >= 0:
                        if self.current_queue_index < len(self.queue) - 1:
                            self.current_queue_index += 1
                            self.play(self.queue[self.current_queue_index])
                        elif self.repeat_mode == 'all':
                            self.current_queue_index = 0
                            self.play(self.queue[0])
                        else:
                            self.is_playing = False
                            print("\nPlayback finished")
            time.sleep(1)

    def play(self, track_id=None):
        """Play a track or resume playback"""
        if track_id:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT filepath, title, artist FROM tracks WHERE id=?",
                (track_id,)
            )
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                print(f"Track {track_id} not found")
                return False
            
            filepath, title, artist = result
            
            if not os.path.isabs(filepath):
                filepath = os.path.abspath(filepath)
            
            if not os.path.exists(filepath):
                print(f"File not found: {filepath}")
                return False
            
            try:
                # Stop current playback if any
                if self.current_process and self.current_process.poll() is None:
                    self.current_process.terminate()
                    self.current_process.wait(timeout=1)
                
                # Remove old socket if exists
                if os.path.exists(self.socket_path):
                    os.remove(self.socket_path)
                
                # Start playback with IPC
                self.current_process = subprocess.Popen(
                    [
                        'mpv',
                        '--no-video',
                        f'--volume={self.volume}',
                        f'--input-ipc-server={self.socket_path}',
                        filepath
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                time.sleep(0.1)
                
                self.current_track_id = track_id
                self.is_playing = True
                self.is_paused = False
                
                # Start monitoring thread if not already running
                if not self.should_monitor:
                    self.should_monitor = True
                    self.monitor_thread = threading.Thread(target=self._monitor_playback, daemon=True)
                    self.monitor_thread.start()
                
                mode_str = ""
                if self.shuffle_mode:
                    mode_str += "[Shuffle] "
                if self.repeat_mode != 'off':
                    mode_str += f"[Repeat: {self.repeat_mode}] "
                
                print(f"{mode_str}Now playing: {title} - {artist}")
                return True
                
            except Exception as e:
                print(f"Error playing track: {e}")
                return False
        else:
            # Resume playback if paused
            if self.is_paused and self.current_track_id:
                if self._send_command({"command": ["set_property", "pause", False]}):
                    self.is_paused = False
                    self.is_playing = True
                    print("Resumed playback")
                    return True
            print("No track to resume")
            return False
    
    def pause(self):
        """Pause playback"""
        if self.is_playing and not self.is_paused:
            if self._send_command({"command": ["set_property", "pause", True]}):
                self.is_paused = True
                self.is_playing = False
                print('Paused')
                return True
        print("Nothing playing to pause")
        return False
    
    def stop(self):
        """Stop playback completely"""
        self.should_monitor = False
        
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
            try:
                self.current_process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.current_process.kill()
        
        self.current_track_id = None
        self.is_playing = False
        self.is_paused = False
        self.current_process = None
        print("Stopped")
        return True
    
    def next_track(self):
        """Skip to next track in queue"""
        if not self.queue:
            print("Queue is empty")
            return False
        
        if self.current_queue_index < len(self.queue) - 1:
            self.current_queue_index += 1
            next_track_id = self.queue[self.current_queue_index]
            return self.play(next_track_id)
        elif self.repeat_mode == 'all':
            self.current_queue_index = 0
            return self.play(self.queue[0])
        else:
            print("End of queue")
            return False
    
    def previous_track(self):
        """Go to previous track in queue"""
        if not self.queue:
            print("Queue is empty")
            return False
        
        if self.current_queue_index > 0:
            self.current_queue_index -= 1
            prev_track_id = self.queue[self.current_queue_index]
            return self.play(prev_track_id)
        else:
            print("Already at first track")
            return False
    
    def toggle_shuffle(self):
        """Toggle shuffle mode on/off"""
        self.shuffle_mode = not self.shuffle_mode
        
        if self.shuffle_mode:
            self.original_queue = self.queue.copy()
            if self.queue:
                current_track = None
                if self.current_queue_index >= 0:
                    current_track = self.queue[self.current_queue_index]
                
                random.shuffle(self.queue)
                
                if current_track:
                    self.queue.remove(current_track)
                    self.queue.insert(0, current_track)
                    self.current_queue_index = 0
            
            print("Shuffle: ON")
        else:
            if self.original_queue:
                current_track = None
                if self.current_queue_index >= 0:
                    current_track = self.queue[self.current_queue_index]
                
                self.queue = self.original_queue.copy()
                
                if current_track and current_track in self.queue:
                    self.current_queue_index = self.queue.index(current_track)
            
            print("Shuffle: OFF")
        
        return self.shuffle_mode
    
    def set_repeat(self, mode):
        """
        Set repeat mode
        mode: 'off', 'one' (repeat current), 'all' (repeat queue)
        """
        if mode not in ['off', 'one', 'all']:
            print("Invalid repeat mode. Use: off, one, or all")
            return False
        
        self.repeat_mode = mode
        mode_display = {
            'off': 'OFF',
            'one': 'ONE (current track)',
            'all': 'ALL (entire queue)'
        }
        print(f"Repeat: {mode_display[mode]}")
        return True
    
    def cycle_repeat(self):
        """Cycle through repeat modes: off -> one -> all -> off"""
        modes = ['off', 'one', 'all']
        current_idx = modes.index(self.repeat_mode)
        next_mode = modes[(current_idx + 1) % len(modes)]
        return self.set_repeat(next_mode)
    
    def set_volume(self, volume):
        """Set volume (changes current track if playing)"""
        if 0 <= volume <= 100:
            self.volume = volume
            if self.is_playing or self.is_paused:
                if self._send_command({"command": ["set_property", "volume", volume]}):
                    print(f"Volume: {volume}%")
                    return True
                else:
                    print(f"Volume set to {volume}% (will apply when playback starts)")
            else:
                print(f"Volume set to {volume}%")
            return True
        else:
            print("Volume must be between 0-100")
            return False
    
    def get_current_track_info(self):
        """Get info about currently playing track"""
        if not self.current_track_id:
            return None
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT title, artist, duration FROM tracks WHERE id=?",
            (self.current_track_id,)
        )
        result = cursor.fetchone()
        conn.close()

        if not result:
            return None
        
        title, artist, duration = result
        
        is_playing = False
        if self.current_process and self.current_process.poll() is None:
            is_playing = not self.is_paused
        else:
            self.is_playing = False
            self.is_paused = False
        
        return {
            'track_id': self.current_track_id,
            'title': title,
            'artist': artist,
            'position': 0,
            'duration': duration,
            'is_playing': is_playing,
            'volume': self.volume,
            'shuffle': self.shuffle_mode,
            'repeat': self.repeat_mode
        }
    
    def load_playlist(self, playlist_id):
        """Load tracks from a playlist into the queue"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT t.id
            FROM playlist_tracks pt
            JOIN tracks t ON pt.track_id = t.id
            WHERE pt.playlist_id = ?
            ORDER BY pt.position
        ''', (playlist_id,))

        tracks = cursor.fetchall()
        conn.close()

        if not tracks:
            print(f"Playlist {playlist_id} is empty")
            return False
        
        self.queue = [track[0] for track in tracks]
        self.original_queue = self.queue.copy()
        self.current_queue_index = 0

        print(f"Loaded {len(self.queue)} tracks from playlist")
        return self.play(self.queue[0])

    def add_to_queue(self, track_id):
        """Add a track to the playback queue"""
        self.queue.append(track_id)
        if not self.shuffle_mode:
            self.original_queue.append(track_id)
        print(f"Added track {track_id} to queue (position {len(self.queue)})")

    def clear_queue(self):
        """Clear the playback queue"""
        self.queue = []
        self.original_queue = []
        self.current_queue_index = -1
        print("Queue cleared")
    
    def show_queue(self):
        """Display the current queue"""
        if not self.queue:
            print("Queue is empty")
            return 
        
        mode_str = ""
        if self.shuffle_mode:
            mode_str += "[Shuffle] "
        if self.repeat_mode != 'off':
            mode_str += f"[Repeat: {self.repeat_mode}]"
        
        print(f"\n=== Current Queue {mode_str}===")
        conn = self.db.get_connection()
        cursor = conn.cursor()

        for i, track_id in enumerate(self.queue):
            cursor.execute(
                "SELECT title, artist FROM tracks WHERE id=?",
                (track_id,)
            )
            result = cursor.fetchone()
            
            if result:
                title, artist = result
                marker = ">" if i == self.current_queue_index else " "
                print(f"{marker} {i+1}. {title} - {artist}")
        
        conn.close()


if __name__ == "__main__":
    player = MusicPlayer()
    print("Player initialized with advanced features!")
    print("- Auto-play next track")
    print("- Shuffle mode")
    print("- Repeat modes (off/one/all)")