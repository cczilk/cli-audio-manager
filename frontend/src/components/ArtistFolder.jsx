import { Folder, ChevronDown, ChevronRight } from 'lucide-react';
import TrackItem from './TrackItem';

function ArtistFolder({ 
  artist, 
  tracks, 
  isExpanded, 
  isLast, 
  currentTrack, 
  isPlaying, 
  onToggle, 
  onPlayTrack,
  onAddToPlaylist
}) {
  return (
    <div>
      <div 
        onClick={onToggle}
        className="flex items-center gap-2 hover:text-green-300 cursor-pointer group"
      >
        <span>{isLast ? '└─' : '├─'}</span>
        {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        <Folder size={14} className="text-green-600" />
        <span className="group-hover:underline">{artist}/ ({tracks.length})</span>
      </div>
      
      {isExpanded && (
        <div className="ml-6 space-y-1 mt-1">
          {tracks.map((track, trackIndex) => {
            const isCurrentTrack = currentTrack?.track_id === track.id;
            const isLastTrack = trackIndex === tracks.length - 1;
            
            return (
              <TrackItem
                key={track.id}
                track={track}
                isLast={isLastTrack}
                isCurrentTrack={isCurrentTrack}
                isPlaying={isPlaying}
                onPlay={onPlayTrack}
                onAddToPlaylist={onAddToPlaylist}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}

export default ArtistFolder;