"""
player.py - Handles audio playback using mpv
"""
import mpv
import time
from database import Database

class MusicPlayer:
    def __init__(self):
        self.player = mpv.MPV(video='no', ytdl=False)  # no video just audio
        # player state
        self.current_track_id = None
        self.is_playing = False
        self.queue = [] 
        self.current_queue_index = -1  # Current Que position

        self.db = Database()
        self.player.volume = 50  # default vol

    
    def play(self, track_id=None):
        # If track_id provided, load that track and play
        # else if no track_id resume current track if paused
        if track_id:
            # get our track info from database
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

            # check if file exists
            import os
            if not os.path.exists(filepath):
                print(f"File not found: {filepath}")
                return False
            # play track
            self.player.play(filepath)
            self.current_track_id = track_id
            self.is_playing = True  # FIXED: was self.is_player

            print(f"Now playing: {title} - {artist}")
            return True
        else:
            # if paused, resume playback
            if self.current_track_id:
                self.player.pause = False
                self.is_playing = True  # FIXED: was on same line as print
                print(" ▶ Resumed playback")
                return True
            else:
                print("No track to resume")
                return False
    
    def pause(self):
        if self.is_playing:
            self.player.pause = True
            self.is_playing = False
            print(' ⏸ Paused')
            return True
        return False
    
    def stop(self):
        self.player.stop()
        self.current_track_id = None
        self.is_playing = False
        print("⏹ Stopped")
    
    def next_track(self):
        # Skip to next track in Que
        if not self.queue:
            print("Queue is empty")
            return False
        if self.current_queue_index < len(self.queue) - 1:
            self.current_queue_index += 1
            next_track_id = self.queue[self.current_queue_index]
            return self.play(next_track_id)
        else:
            print("End of Queue")
            return False  
    
    def previous_track(self):
        if not self.queue:
            print("Queue is empty")
            return False
        if self.current_queue_index > 0:
            self.current_queue_index -= 1
            prev_track_id = self.queue[self.current_queue_index]
            return self.play(prev_track_id)
        else:
            print("No previous track, already at first track")
            return False
    
    def set_volume(self, volume):
        if 0 <= volume <= 100:
            self.player.volume = volume
            print(f"Current Volume: {volume}%")
            return True
        else:
            print("Volume must be between 0-100")
            return False

    
    def get_current_track_info(self):
        """
        return a dict with, track_id, title, artist, postion, duration, and boolean is_playing
        """
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
        #  get our current playback pos
        
        try:
            position = self.player.time_pos or 0
        except:
            position = 0
        
        return {  # FIXED: indentation was wrong (had 7 spaces, needs 8)
            'track_id': self.current_track_id,
            'title': title,
            'artist': artist,
            'position': int(position),
            'duration': duration,
            'is_playing': self.is_playing
        }
    
    def load_playlist(self, playlist_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get all tracks in playlist ordered by pos
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
        self.current_queue_index = 0

        print(f"Loaded {len(self.queue)} tracks from playlist")
        # start playing from first track in playlist
        return self.play(self.queue[0])

    
    def add_to_queue(self, track_id):
        self.queue.append(track_id)
        print(f"Added {track_id} to queue (position {len(self.queue)})")

    def clear_queue(self):
        self.queue = []
        self.current_queue_index = -1
        print("Queue cleared")
    
    def show_queue(self):
        if not self.queue:
            print("Queue is empty")
            return 
        
        print("\n=== Current Queue ===")
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
                marker = "→" if i == self.current_queue_index else " "
                print(f"{marker} {i+1}. {title} - {artist}")
        
        conn.close()


# Test function
if __name__ == "__main__":
    player = MusicPlayer()