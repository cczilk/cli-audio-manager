import { Music, FolderPlus } from 'lucide-react';

function TrackItem({ track, isLast, isCurrentTrack, isPlaying, onPlay, onAddToPlaylist }) {
  return (
    <div className="flex items-center gap-2 group">
      <div
        onClick={() => onPlay(track.id)}
        className={`flex items-center gap-2 cursor-pointer hover:text-green-300 flex-1 min-w-0 ${
          isCurrentTrack ? 'text-green-200' : ''
        }`}
      >
        <span>{isLast ? '└─' : '├─'}</span>
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
      
      {onAddToPlaylist && (
        <button
          onClick={(e) => onAddToPlaylist(track, e)}
          className="opacity-0 group-hover:opacity-100 text-green-700 hover:text-green-500 transition-opacity ml-2"
          title="Add to playlist"
        >
          <FolderPlus size={14} />
        </button>
      )}
    </div>
  );
}

export default TrackItem;