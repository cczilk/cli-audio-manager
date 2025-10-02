"""
downloader.py - Handles downloading audio from YouTube and SoundCloud
"""
import yt_dlp
import os
from database import Database

class AudioDownloader:
    def __init__(self, download_dir='./downloads'):
        """
        Initialize the downloader
        """
        self.download_dir = os.path.abspath(download_dir)
        os.makedirs(self.download_dir, exist_ok=True)
        self.db = Database()

    
    def download_from_youtube(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info without downloading to get metadata
                print(f"Fetching info for: {url}")
                info = ydl.extract_info(url, download=False)
                ydl.download([url])

                filepath = os.path.join(self.download_dir, f"{info['title']}.mp3")
                
                # Extract metadata
                title = info.get('title', 'Unknown')
                artist = info.get('artist', info.get('uploader', 'Unknown'))
                duration = info.get('duration', 0)
                
                print(f"Downloaded: {title} by {artist}")
                track_id = self.add_to_library(filepath, title, artist, url, duration)

                return {
                    'filepath': filepath,
                    'title': title,
                    'artist': artist,
                    'duration': duration,
                    'source_url': url,
                    'track_id': track_id
                }
        except Exception as e:
            print(f"Error downloading: {e}")
            return None
    
    def download_from_soundcloud(self, url):
        # SoundCloud downloads work the same way as YouTube with yt_dlp
        return self.download_from_youtube(url)
    
    def add_to_library(self, filepath, title, artist, source_url, duration):
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO tracks (title, artist, filepath, source_url, duration)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, artist, filepath, source_url, duration))
        
        track_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return track_id

    
    def process_queue(self):
        """
        Get all pending downloads, 
        try download each one and update status to completed or failed
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, url FROM download_queue WHERE status='pending'")
        pending = cursor.fetchall()
        print(f"Processing {len(pending)} downloads...")
        
        for queue_id, url in pending:
            try:
                result = self.download_from_youtube(url)

                if result:
                    cursor.execute(
                        "UPDATE download_queue SET status='completed' WHERE id=?",
                        (queue_id,)
                    )
                else:
                    cursor.execute(
                        "UPDATE download_queue SET status='failed' WHERE id=?",
                        (queue_id,)
                    )
                
                conn.commit()

            except Exception as e:
                print(f"Error processing queue item {queue_id}: {e}")
                cursor.execute(
                    "UPDATE download_queue SET status='failed' WHERE id=?",
                    (queue_id,)
                )
                conn.commit()
        
        conn.close()
        print("Queue processing complete")


    def add_to_queue(self, url):
        """
        Add URL to download queue for batch processing later
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO download_queue (url, status)
            VALUES (?, 'pending')
        ''', (url,))
        
        queue_id = cursor.lastrowid
        conn.commit()
        conn.close()

        print(f"Added to download queue: {url}")
        return queue_id

