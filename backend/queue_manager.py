"""
queue_manager.py - Manage multiple downloads at once
"""
from downloader import AudioDownloader
from database import Database

class QueueManager:
    def __init__(self):
        self.downloader = AudioDownloader()
        self.db = Database()
    
    def add_multiple_urls(self, urls):
        """
        Add multiple URLs to download queue at once
        urls: list of URLs or newline-separated string
        """
        if isinstance(urls, str):
            urls = [u.strip() for u in urls.split('\n') if u.strip()]
        
        added = 0
        for url in urls:
            if url.startswith('http'):
                self.downloader.add_to_queue(url)
                added += 1
        
        print(f"✓ Added {added} URLs to download queue")
        return added
    
    def process_all(self):
        """Process all pending downloads"""
        self.downloader.process_queue()
    
    def clear_completed(self):
        """Remove completed items from queue"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM download_queue WHERE status='completed'")
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        print(f"✓ Removed {deleted} completed downloads from queue")
        return deleted
    
    def clear_failed(self):
        """Remove failed items from queue"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM download_queue WHERE status='failed'")
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        print(f"✓ Removed {deleted} failed downloads from queue")
        return deleted