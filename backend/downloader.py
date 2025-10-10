import yt_dlp
import os
from database import Database

class AudioDownloader:
    def __init__(self, download_dir='./downloads'):
        self.download_dir = os.path.abspath(download_dir)
        os.makedirs(self.download_dir, exist_ok=True)
        self.db = Database()

    def download_from_youtube(self, url):
        """
        Download audio from YouTube URL and extract album art
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            'quiet': False,
            'restrictfilenames': True,
            'writethumbnail': True,  
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Fetching info for: {url}")
                info = ydl.extract_info(url, download=False)
                
                print(f"Downloading: {info['title']}")
                ydl.download([url])
                
                filepath = ydl.prepare_filename(info)
                filepath = os.path.splitext(filepath)[0] + '.mp3'
                
                # Check for downloaded thumbnail
                thumbnail_path = None
                possible_thumb_extensions = ['.jpg', '.png', '.webp']
                base_filepath = os.path.splitext(filepath)[0]
                
                for ext in possible_thumb_extensions:
                    thumb_file = base_filepath + ext
                    if os.path.exists(thumb_file):
                        thumbnail_path = thumb_file
                        print(f"Found thumbnail: {thumb_file}")
                        break
                
                if not os.path.exists(filepath):
                    print(f"Warning: File not found at {filepath}")
                    return None
                
                title = info.get('title', 'Unknown')
                artist = info.get('artist', info.get('uploader', 'Unknown'))
                duration = info.get('duration', 0)
                
                print(f"✓ Downloaded: {title} by {artist}")
                print(f"  Saved to: {filepath}")
                if thumbnail_path:
                    print(f"  Album art: {thumbnail_path}")
                
                track_id = self.add_to_library(filepath, title, artist, url, duration, thumbnail_path)
                
                return {
                    'track_id': track_id,
                    'filepath': filepath,
                    'title': title,
                    'artist': artist,
                    'duration': duration,
                    'source_url': url,
                    'thumbnail_path': thumbnail_path
                }
                
        except Exception as e:
            print(f"✗ Error downloading: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def download_from_soundcloud(self, url):
        """
        Download audio from SoundCloud
        SoundCloud downloads work the same way as YouTube with yt_dlp
        """
        return self.download_from_youtube(url)
    
    def add_to_library(self, filepath, title, artist, source_url, duration, thumbnail_path=None):
        """
        Add downloaded track to database with optional thumbnail
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tracks (title, artist, filepath, source_url, duration, thumbnail_path)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, artist, filepath, source_url, duration, thumbnail_path))
        
        track_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return track_id

    def add_to_queue(self, url):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO download_queue (url, status)
            VALUES (?, 'pending')
        ''', (url,))
        
        queue_id = cursor.lastrowid
        conn.commit()
        conn.close()

        print(f"✓ Added to download queue: {url}")
        return queue_id
    
    def process_queue(self):
        """
        Get all pending downloads, 
        try download each one and update status to completed or failed
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, url FROM download_queue WHERE status='pending'")
        pending = cursor.fetchall()
        
        if not pending:
            print("No pending downloads in queue")
            return
        
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
        print("✓ Queue processing complete")



if __name__ == "__main__":
    downloader = AudioDownloader()
    
    if result:
        print(f"\nSuccess! Downloaded to: {result['filepath']}")
        print(f"Track ID in database: {result['track_id']}")