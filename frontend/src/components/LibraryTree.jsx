import { useState } from 'react';
import { Folder, Loader2, FolderPlus, Music } from 'lucide-react';
import ArtistFolder from './ArtistFolder';

function LibraryTree({ 
  tracks, 
  loading, 
  expandedArtists, 
  currentTrack, 
  isPlaying,
  playlists,
  onToggleArtist, 
  onPlayTrack,
  onCreatePlaylist,
  onPlayPlaylist,
  onAddToPlaylist,
  onTogglePlaylist,
  expandedPlaylists
}) {
  const [view, setView] = useState('library'); // 'library' or 'playlists'
  const [newPlaylistName, setNewPlaylistName] = useState('');
  const [showCreatePlaylist, setShowCreatePlaylist] = useState(false);
  const [selectedTrackForPlaylist, setSelectedTrackForPlaylist] = useState(null);
  const [showPlaylistSelector, setShowPlaylistSelector] = useState(false);

  // Group tracks by artist
  const groupedTracks = tracks.reduce((acc, track) => {
    const artist = track.artist || 'Unknown Artist';
    if (!acc[artist]) {
      acc[artist] = [];
    }
    acc[artist].push(track);
    return acc;
  }, {});

  const handleCreatePlaylist = () => {
    if (newPlaylistName.trim()) {
      onCreatePlaylist(newPlaylistName);
      setNewPlaylistName('');
      setShowCreatePlaylist(false);
    }
  };

  const handleAddToPlaylist = (playlistId) => {
    if (selectedTrackForPlaylist) {
      onAddToPlaylist(playlistId, selectedTrackForPlaylist.id);
      setShowPlaylistSelector(false);
      setSelectedTrackForPlaylist(null);
    }
  };

  const openPlaylistSelector = (track, e) => {
    e.stopPropagation();
    setSelectedTrackForPlaylist(track);
    setShowPlaylistSelector(true);
  };

  return (
    <div className="bg-gray-900 border border-green-800 rounded p-4 mb-6">
      {/* Header with view toggle */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setView('library')}
            className={`flex items-center gap-2 ${
              view === 'library' ? 'text-green-500' : 'text-green-700 hover:text-green-600'
            }`}
          >
            <Folder size={16} />
            <span>library/ ({tracks.length} tracks)</span>
          </button>
          
          <button
            onClick={() => setView('playlists')}
            className={`flex items-center gap-2 ${
              view === 'playlists' ? 'text-green-500' : 'text-green-700 hover:text-green-600'
            }`}
          >
            <Music size={16} />
            <span>playlists/ ({playlists.length})</span>
          </button>
        </div>

        {view === 'playlists' && !showCreatePlaylist && (
          <button
            onClick={() => setShowCreatePlaylist(true)}
            className="flex items-center gap-1 text-green-600 hover:text-green-500 text-sm"
          >
            <FolderPlus size={14} />
            <span>new</span>
          </button>
        )}
      </div>

      {/* Create Playlist Input */}
      {showCreatePlaylist && (
        <div className="ml-6 mb-3 flex items-center gap-2">
          <span className="text-green-700">$</span>
          <span className="text-green-600">mkdir</span>
          <input
            type="text"
            value={newPlaylistName}
            onChange={(e) => setNewPlaylistName(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') handleCreatePlaylist();
              if (e.key === 'Escape') {
                setShowCreatePlaylist(false);
                setNewPlaylistName('');
              }
            }}
            onBlur={() => {
              if (!newPlaylistName.trim()) {
                setShowCreatePlaylist(false);
              }
            }}
            placeholder="playlist_name"
            className="flex-1 bg-black border border-green-800 rounded px-2 py-1 text-green-400 text-sm focus:outline-none focus:border-green-600"
            autoFocus
          />
        </div>
      )}
      
      {/* Library View */}
      {view === 'library' && (
        <>
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
                  <ArtistFolder
                    key={artist}
                    artist={artist}
                    tracks={artistTracks}
                    isExpanded={isExpanded}
                    isLast={isLast}
                    currentTrack={currentTrack}
                    isPlaying={isPlaying}
                    onToggle={() => onToggleArtist(artist)}
                    onPlayTrack={onPlayTrack}
                    onAddToPlaylist={openPlaylistSelector}
                  />
                );
              })}
            </div>
          )}
        </>
      )}

      {/* Playlists View */}
      {view === 'playlists' && (
        <>
          {playlists.length === 0 ? (
            <div className="ml-6 text-green-600">
              <p>└─ empty/</p>
              <p className="ml-6 text-green-700">$ create a playlist to get started</p>
            </div>
          ) : (
            <div className="ml-6 space-y-1">
              {playlists.map((playlist, index) => {
                const isExpanded = expandedPlaylists[playlist.id] ?? false;
                const isLast = index === playlists.length - 1;
                const prefix = isLast ? '└─' : '├─';
                
                return (
                  <div key={playlist.id}>
                    {/* Playlist Folder */}
                    <div className="flex items-center gap-2 group">
                      <button
                        onClick={() => onTogglePlaylist(playlist.id)}
                        className="flex items-center gap-2 text-green-500 hover:text-green-400"
                      >
                        <span className="text-green-700">{prefix}</span>
                        <Folder size={14} />
                        <span>{playlist.name}/ ({playlist.track_count || 0})</span>
                      </button>
                      <button
                        onClick={() => onPlayPlaylist(playlist.id)}
                        className="opacity-0 group-hover:opacity-100 text-green-600 hover:text-green-500 text-xs ml-2"
                      >
                        [▶ play]
                      </button>
                    </div>

                    {/* Playlist Tracks */}
                    {isExpanded && (
                      <div className="ml-6">
                        {playlist.tracks && playlist.tracks.length > 0 ? (
                          playlist.tracks.map((track, trackIndex) => {
                            const trackPrefix = trackIndex === playlist.tracks.length - 1 ? '└─' : '├─';
                            const isCurrentTrack = currentTrack?.track_id === track.id;
                            
                            return (
                              <button
                                key={track.id}
                                onClick={() => onPlayTrack(track.id)}
                                className={`flex items-center gap-2 w-full text-left hover:text-green-400 ${
                                  isCurrentTrack ? 'text-green-400' : 'text-green-600'
                                }`}
                              >
                                <span className="text-green-700">{trackPrefix}</span>
                                <span className="text-green-600">
                                  {isCurrentTrack && isPlaying ? '▶' : '♪'}
                                </span>
                                <span className="truncate">{track.title}</span>
                                {track.duration > 0 && (
                                  <span className="text-green-800 text-xs ml-auto">
                                    [{Math.floor(track.duration / 60)}:{String(track.duration % 60).padStart(2, '0')}]
                                  </span>
                                )}
                              </button>
                            );
                          })
                        ) : (
                          <p className="text-green-700 text-sm">└─ empty/</p>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {/* Playlist Selector Modal */}
      {showPlaylistSelector && (
        <div 
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" 
          onClick={() => setShowPlaylistSelector(false)}
        >
          <div 
            className="bg-gray-900 border border-green-800 rounded p-6 max-w-md w-full mx-4" 
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-2 mb-4 text-green-500">
              <FolderPlus size={16} />
              <span>Add to Playlist</span>
            </div>
            
            <div className="text-green-600 text-sm mb-4 ml-4">
              <span className="text-green-700">└─</span> {selectedTrackForPlaylist?.title}
            </div>
            
            {playlists.length === 0 ? (
              <p className="text-green-700 text-sm mb-4 ml-4">
                No playlists available. Create one first!
              </p>
            ) : (
              <div className="space-y-1 max-h-60 overflow-y-auto mb-4">
                {playlists.map((playlist) => (
                  <button
                    key={playlist.id}
                    onClick={() => handleAddToPlaylist(playlist.id)}
                    className="w-full px-4 py-2 text-left hover:bg-gray-800 text-green-500 hover:text-green-400 rounded flex items-center gap-2"
                  >
                    <Folder size={14} />
                    <span>{playlist.name}/</span>
                  </button>
                ))}
              </div>
            )}
            
            <button
              onClick={() => setShowPlaylistSelector(false)}
              className="w-full px-4 py-2 bg-gray-800 hover:bg-gray-700 text-green-600 rounded text-sm"
            >
              [ESC] Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default LibraryTree;