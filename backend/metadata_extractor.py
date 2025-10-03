"""
metadata_extractor.py - Extract album art and metadata from audio files
"""
from mutagen import File
from mutagen.id3 import ID3, APIC
from PIL import Image
import io
import os

class MetadataExtractor:
    def extract_album_art(self, filepath, output_path=None):
        """
        Extract album art from audio file
        Returns path to saved image or None
        """
        try:
            audio = File(filepath)
            
            if audio is None:
                return None
            
            artwork_data = None
            
            # MP3 files
            if hasattr(audio, 'tags') and audio.tags:
                for key in audio.tags:
                    if key.startswith('APIC'):
                        artwork_data = audio.tags[key].data
                        break
            
            # MP4/M4A files
            elif hasattr(audio, 'get') and 'covr' in audio:
                artwork_data = bytes(audio['covr'][0])
            
            if artwork_data:
                if not output_path:
                    base = os.path.splitext(filepath)[0]
                    output_path = f"{base}_cover.jpg"
                
                img = Image.open(io.BytesIO(artwork_data))
                img.save(output_path)
                return output_path
            
            return None
            
        except Exception as e:
            print(f"Error extracting album art: {e}")
            return None
    
    def display_album_art_terminal(self, image_path):
        """Display album art in terminal using ASCII"""
        try:
            img = Image.open(image_path)
            img = img.resize((80, 40), Image.LANCZOS)
            img = img.convert('L')
            
            chars = "@%#*+=-:. "
            
            print("\nAlbum Art:")
            for y in range(img.height):
                for x in range(img.width):
                    pixel = img.getpixel((x, y))
                    char_index = int(pixel / 255 * (len(chars) - 1))
                    print(chars[char_index], end='')
                print()
            print()
            
        except Exception as e:
            print(f"Could not display album art: {e}")