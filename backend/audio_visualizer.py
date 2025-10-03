"""
audio_visualizer.py - Simple non-blocking visualization
"""
import subprocess
import threading
import time
import numpy as np

class AudioVisualizer:
    def __init__(self):
        self.is_visualizing = False
        self.visualization_thread = None
        self.enabled = False  # Start disabled
    
    def toggle(self):
        """Toggle visualization on/off"""
        self.enabled = not self.enabled
        return self.enabled
    
    def start_visualization(self, audio_file):
        """Start visualization if enabled"""
        if not self.enabled:
            return
        
        self.is_visualizing = True
        self.visualization_thread = threading.Thread(
            target=self._visualize,
            args=(audio_file,),
            daemon=True
        )
        self.visualization_thread.start()
    
    def _visualize(self, audio_file):
        """Print waveform snapshots periodically"""
        try:
            process = subprocess.Popen(
                ['ffmpeg', '-i', audio_file, '-f', 's16le', '-acodec', 'pcm_s16le',
                 '-ac', '1', '-ar', '4000', '-'],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**8
            )
            
            while self.is_visualizing:
                data = process.stdout.read(2048)
                if len(data) < 2048:
                    break
                
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Create 40-bar waveform
                bars = 40
                samples_per = len(audio_data) // bars
                heights = []
                
                for i in range(bars):
                    chunk = audio_data[i*samples_per:(i+1)*samples_per]
                    heights.append(int((np.abs(chunk).mean() / 32768) * 8))
                
                # Print waveform
                print('\n🎵 ', end='')
                for h in heights:
                    if h == 0: print('▁', end='')
                    elif h == 1: print('▂', end='')
                    elif h == 2: print('▃', end='')
                    elif h == 3: print('▄', end='')
                    elif h == 4: print('▅', end='')
                    elif h == 5: print('▆', end='')
                    elif h == 6: print('▇', end='')
                    else: print('█', end='')
                print('\n')
                
                time.sleep(2)  # Update every 2 seconds
            
            process.terminate()
        except:
            pass
    
    def stop_visualization(self):
        self.is_visualizing = False