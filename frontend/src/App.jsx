/* 
  App.jsx - Main UI container for the music player
  Handles the playback, download playlist managment and responsive layout
*/
import { useState, useEffect } from 'react';
import { trackAPI, playerAPI, downloadAPI } from './api/client';
import toast, { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import DownloadForm from './components/DownloadForm';
import NowPlaying from './components/NowPlaying';
import LibraryTree from './components/LibraryTree';
import Terminal from './components/Terminal';

function App() {
  const [tracks, setTracks] = useState([]);
  const [currentTrack, setCurrentTrack] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [expandedArtists, setExpandedArtists] = useState({});
  const [isWideScreen, setIsWideScreen] = useState(window.innerWidth > 1400);
  const [playlists, setPlaylists] = useState([]);
  const [expandedPlaylists, setExpandedPlaylists] = useState({});

  useEffect(() => {
    loadTracks();
    loadPlaylists();
    const interval = setInterval(updatePlayerStatus, 2000);
    
    const handleResize = () => {
      setIsWideScreen(window.innerWidth > 1400);
    };
    
    window.addEventListener('resize', handleResize);
    
    return () => {
      clearInterval(interval);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const loadTracks = async () => {
    try {
      setLoading(true);
      const response = await trackAPI.getAll();
      setTracks(response.data);
    } catch (error) {
      console.error('Failed to load tracks:', error);
      toast.error('Failed to load tracks');
    } finally {
      setLoading(false);
    }
  };

  const loadPlaylists = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/playlists');
      const data = await response.json();
      
      // Fetch playlist details to include track list and count
      const playlistsWithTracks = await Promise.all(
        data.map(async (playlist) => {
          const detailResponse = await fetch(`http://localhost:5000/api/playlists/${playlist.id}`);
          const details = await detailResponse.json();
          return {
            ...playlist,
            tracks: details.tracks || [],
            track_count: details.tracks?.length || 0
          };
        })
      );
      
      setPlaylists(playlistsWithTracks);
    } catch (error) {
      console.error('Failed to load playlists:', error);
    }
  };

  const updatePlayerStatus = async () => {
    try {
      const response = await playerAPI.getStatus();
      setCurrentTrack(response.data);
      setIsPlaying(response.data.is_playing);
    } catch (error) {
      // Fail silently - backend offline
    }
  };

  const handlePlay = async (trackId) => {
    try {
      await playerAPI.play(trackId);
      toast.success('Playing');
      updatePlayerStatus();
    } catch (error) {
      toast.error('Failed to play');
    }
  };

  const handlePause = async () => {
    try {
      await playerAPI.pause();
      setIsPlaying(false);
    } catch (error) {
      toast.error('Failed to pause');
    }
  };

  const handleNext = async () => {
    try {
      await playerAPI.next();
      updatePlayerStatus();
    } catch (error) {
      toast.error('No next track');
    }
  };

  const handlePrevious = async () => {
    try {
      await playerAPI.previous();
      updatePlayerStatus();
    } catch (error) {
      toast.error('No previous track');
    }
  };

  const handleDownload = async (e) => {
    e.preventDefault();
    if (!downloadUrl.trim()) {
      toast.error('Please enter a URL');
      return;
    }
    
    try {
      setDownloading(true);
      await downloadAPI.addToQueue(downloadUrl);
      toast.success('Added to queue');
      setDownloadUrl('');
      
      toast.loading('Downloading...', { id: 'download' });
      await downloadAPI.processQueue();
      
      setTimeout(async () => {
        await loadTracks();
        toast.success('Download complete!', { id: 'download' });
      }, 3000);
    } catch (error) {
      toast.error('Download failed', { id: 'download' });
    } finally {
      setDownloading(false);
    }
  };

  const toggleArtist = (artist) => {
    setExpandedArtists(prev => ({
      ...prev,
      [artist]: !prev[artist]
    }));
  };

  const togglePlaylist = (playlistId) => {
    setExpandedPlaylists(prev => ({
      ...prev,
      [playlistId]: !prev[playlistId]
    }));
  };

  const handleCreatePlaylist = async (name) => {
    try {
      const response = await fetch('http://localhost:5000/api/playlists', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });
      
      if (response.ok) {
        toast.success(`Playlist "${name}" created`);
        await loadPlaylists();
      } else {
        toast.error('Failed to create playlist');
      }
    } catch (error) {
      toast.error('Failed to create playlist');
    }
  };

  const handlePlayPlaylist = async (playlistId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/playlists/${playlistId}/play`, {
        method: 'POST'
      });
      
      if (response.ok) {
        toast.success('Playing playlist');
        updatePlayerStatus();
      } else {
        toast.error('Failed to play playlist');
      }
    } catch (error) {
      toast.error('Failed to play playlist');
    }
  };

  const handleAddToPlaylist = async (playlistId, trackId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/playlists/${playlistId}/tracks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ track_id: trackId })
      });
      
      if (response.ok) {
        toast.success('Added to playlist');
        await loadPlaylists();
      } else {
        toast.error('Failed to add to playlist');
      }
    } catch (error) {
      toast.error('Failed to add to playlist');
    }
  };

  return (
    <div className="min-h-screen bg-black text-green-400 font-mono">
      <Toaster 
        position="top-right"
        toastOptions={{
          style: {
            background: '#0a0a0a',
            color: '#4ade80',
            border: '1px solid #22c55e',
          },
        }}
      />
      
      {/* Wide Screen Layout (Fullscreen) */}
      {isWideScreen ? (
        <div className="grid grid-cols-12 gap-6 p-6 h-screen">
          {/* Left Column: Header + Download + Terminal */}
          <div className="col-span-3 flex flex-col gap-6">
            <Header />
            <DownloadForm
              downloadUrl={downloadUrl}
              setDownloadUrl={setDownloadUrl}
              downloading={downloading}
              onSubmit={handleDownload}
            />
            <div className="flex-1 overflow-hidden">
              <Terminal />
            </div>
          </div>

          {/* Middle Column: Library */}
          <div className="col-span-6 overflow-auto">
            <LibraryTree
              tracks={tracks}
              loading={loading}
              expandedArtists={expandedArtists}
              currentTrack={currentTrack}
              isPlaying={isPlaying}
              playlists={playlists}
              expandedPlaylists={expandedPlaylists}
              onToggleArtist={toggleArtist}
              onPlayTrack={handlePlay}
              onCreatePlaylist={handleCreatePlaylist}
              onPlayPlaylist={handlePlayPlaylist}
              onAddToPlaylist={handleAddToPlaylist}
              onTogglePlaylist={togglePlaylist}
            />
          </div>

          {/* Right Column: Album Art + Now Playing */}
          <div className="col-span-3 flex flex-col gap-6">
            <div className="bg-gray-900 border border-green-800 rounded p-4">
              <div className="aspect-square bg-black border border-green-700 rounded flex items-center justify-center overflow-hidden mb-4">
                {currentTrack?.track_id ? (
                  <img 
                    src={`http://localhost:5000/api/tracks/${currentTrack.track_id}/thumbnail`}
                    alt="Album Art"
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div className="text-center" style={{ display: currentTrack?.track_id ? 'none' : 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div className="text-4xl mb-2 text-green-800">♪</div>
                  <p className="text-green-800 text-xs">No track playing</p>
                </div>
              </div>
            </div>

            <NowPlaying
              currentTrack={currentTrack}
              isPlaying={isPlaying}
              onPlay={handlePlay}
              onPause={handlePause}
              onNext={handleNext}
              onPrevious={handlePrevious}
            />
          </div>
        </div>
      ) : (
        // Narrow Screen Layout (Split screen or mobile)
        <div className="container mx-auto p-6 max-w-none px-8">
          <div className="flex justify-center mb-6">
            <Header />
          </div>

          <div className="max-w-5xl mx-auto mb-8">
            <DownloadForm
              downloadUrl={downloadUrl}
              setDownloadUrl={setDownloadUrl}
              downloading={downloading}
              onSubmit={handleDownload}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="lg:col-span-2">
              <LibraryTree
                tracks={tracks}
                loading={loading}
                expandedArtists={expandedArtists}
                currentTrack={currentTrack}
                isPlaying={isPlaying}
                playlists={playlists}
                expandedPlaylists={expandedPlaylists}
                onToggleArtist={toggleArtist}
                onPlayTrack={handlePlay}
                onCreatePlaylist={handleCreatePlaylist}
                onPlayPlaylist={handlePlayPlaylist}
                onAddToPlaylist={handleAddToPlaylist}
                onTogglePlaylist={togglePlaylist}
              />
            </div>

            <div className="space-y-6">
              <div className="bg-gray-900 border border-green-800 rounded p-4">
                <div className="aspect-square bg-black border border-green-700 rounded flex items-center justify-center overflow-hidden mb-4">
                  {currentTrack?.track_id ? (
                    <img 
                      src={`http://localhost:5000/api/tracks/${currentTrack.track_id}/thumbnail`}
                      alt="Album Art"
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        // Fallback if image fails to load
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <div className="text-center" style={{ display: currentTrack?.track_id ? 'none' : 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <div className="text-4xl mb-2 text-green-800">♪</div>
                    <p className="text-green-800 text-xs">No track playing</p>
                  </div>
                </div>
              </div>

              <NowPlaying
                currentTrack={currentTrack}
                isPlaying={isPlaying}
                onPlay={handlePlay}
                onPause={handlePause}
                onNext={handleNext}
                onPrevious={handlePrevious}
              />
            </div>
          </div>

          <div className="max-w-6xl mx-auto">
            <Terminal />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;