import { useState, useEffect } from 'react';
import { trackAPI, playerAPI, downloadAPI } from './api/client';
import { Play, Pause, SkipForward, SkipBack, Download, Loader2, Music, Folder, ChevronRight, ChevronDown } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import Terminal from './components/Terminal';

function App() {
  const [tracks, setTracks] = useState([]);
  const [currentTrack, setCurrentTrack] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [expandedArtists, setExpandedArtists] = useState({});

  useEffect(() => {
    loadTracks();
    const interval = setInterval(updatePlayerStatus, 2000);
    return () => clearInterval(interval);
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

  const updatePlayerStatus = async () => {
    try {
      const response = await playerAPI.getStatus();
      setCurrentTrack(response.data);
      setIsPlaying(response.data.is_playing);
    } catch (error) {
      // Silent fail
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

  // Group tracks by artist
  const groupedTracks = tracks.reduce((acc, track) => {
    const artist = track.artist || 'Unknown Artist';
    if (!acc[artist]) {
      acc[artist] = [];
    }
    acc[artist].push(track);
    return acc;
  }, {});

  const toggleArtist = (artist) => {
    setExpandedArtists(prev => ({
      ...prev,
      [artist]: !prev[artist]
    }));
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
      
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-6 border-b border-green-800 pb-4">
          <h1 className="text-2xl mb-2">
            <span className="text-green-500">~/</span>terminal-music-player
          </h1>
          <p className="text-green-600 text-sm">$ music-player --interactive</p>
        </div>

        {/* Download Section */}
        <div className="mb-6 bg-gray-900 border border-green-800 rounded p-4">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-green-500">$</span>
            <span className="text-green-600">download</span>
          </div>
          <form onSubmit={handleDownload} className="flex gap-2">
            <input
              type="text"
              value={downloadUrl}
              onChange={(e) => setDownloadUrl(e.target.value)}
              placeholder="https://youtube.com/..."
              disabled={downloading}
              className="flex-1 bg-black border border-green-800 rounded px-3 py-2 text-green-400 focus:outline-none focus:border-green-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={downloading}
              className="bg-green-900 hover:bg-green-800 disabled:bg-gray-800 px-4 py-2 rounded border border-green-700 transition flex items-center gap-2"
            >
              {downloading ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
              {downloading ? 'downloading...' : 'download'}
            </button>
          </form>
        </div>

        {/* Now Playing */}
        {currentTrack?.title && (
          <div className="mb-6 bg-gray-900 border border-green-700 rounded p-4">
            <div className="flex items-center gap-2 mb-3 text-green-500">
              <Music size={16} />
              <span>now_playing</span>
            </div>
            <div className="ml-6 mb-4">
              <p className="text-green-300">{currentTrack.title}</p>
              <p className="text-green-600 text-sm">by {currentTrack.artist}</p>
            </div>
            
            <div className="flex gap-2 ml-6">
              <button 
                onClick={handlePrevious}
                className="bg-black border border-green-800 hover:border-green-600 p-2 rounded transition"
              >
                <SkipBack size={16} />
              </button>
              <button 
                onClick={isPlaying ? handlePause : () => handlePlay(currentTrack.track_id)}
                className="bg-green-900 hover:bg-green-800 border border-green-700 p-2 rounded transition"
              >
                {isPlaying ? <Pause size={16} /> : <Play size={16} />}
              </button>
              <button 
                onClick={handleNext}
                className="bg-black border border-green-800 hover:border-green-600 p-2 rounded transition"
              >
                <SkipForward size={16} />
              </button>
            </div>
          </div>
        )}

        {/* Library - Tree View */}
        <div className="bg-gray-900 border border-green-800 rounded p-4">
          <div className="flex items-center gap-2 mb-4 text-green-500">
            <Folder size={16} />
            <span>library/ ({tracks.length} tracks)</span>
          </div>
          
          {loading ? (
            <div className="flex items-center gap-2 ml-6 text-green-600">
              <Loader2 size={16} className="animate-spin" />
              <span>loading...</span>
            </div>
          ) : tracks.length === 0 ? (
            <div className="ml-6 text-green-600">
              <p>└─ empty/</p>
              <p className="ml-6 text-green-700">$ download some tracks to get started</p>
            </div>
          ) : (
            <div className="ml-6 space-y-1">
              {Object.entries(groupedTracks).map(([artist, artistTracks], index) => {
                const isExpanded = expandedArtists[artist] ?? false;
                const isLast = index === Object.keys(groupedTracks).length - 1;
                
                return (
                  <div key={artist}>
                    <div 
                      onClick={() => toggleArtist(artist)}
                      className="flex items-center gap-2 hover:text-green-300 cursor-pointer group"
                    >
                      <span>{isLast ? '└─' : '├─'}</span>
                      {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                      <Folder size={14} className="text-green-600" />
                      <span className="group-hover:underline">{artist}/ ({artistTracks.length})</span>
                    </div>
                    
                    {isExpanded && (
                      <div className="ml-6 space-y-1 mt-1">
                        {artistTracks.map((track, trackIndex) => {
                          const isCurrentTrack = currentTrack?.track_id === track.id;
                          const isLastTrack = trackIndex === artistTracks.length - 1;
                          
                          return (
                            <div
                              key={track.id}
                              onClick={() => handlePlay(track.id)}
                              className={`flex items-center gap-2 cursor-pointer hover:text-green-300 ${
                                isCurrentTrack ? 'text-green-200' : ''
                              }`}
                            >
                              <span>{isLastTrack ? '└─' : '├─'}</span>
                              {isCurrentTrack && isPlaying ? (
                                <span className="animate-pulse">▶</span>
                              ) : (
                                <Music size={14} className="text-green-700" />
                              )}
                              <span className="flex-1 truncate">{track.title}</span>
                              <span className="text-green-700 text-xs">
                                {Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
  <div className="mt-6">
  <Terminal />
</div>
}

export default App;