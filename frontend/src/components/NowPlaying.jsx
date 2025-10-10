import { Music, Play, Pause, SkipBack, SkipForward } from 'lucide-react';

function NowPlaying({ currentTrack, isPlaying, onPlay, onPause, onNext, onPrevious }) {
  if (!currentTrack?.title) return null;

  return (
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
          onClick={onPrevious}
          className="bg-black border border-green-800 hover:border-green-600 p-2 rounded transition"
        >
          <SkipBack size={16} />
        </button>
        <button 
          onClick={isPlaying ? onPause : () => onPlay(currentTrack.track_id)}
          className="bg-green-900 hover:bg-green-800 border border-green-700 p-2 rounded transition"
        >
          {isPlaying ? <Pause size={16} /> : <Play size={16} />}
        </button>
        <button 
          onClick={onNext}
          className="bg-black border border-green-800 hover:border-green-600 p-2 rounded transition"
        >
          <SkipForward size={16} />
        </button>
      </div>
    </div>
  );
}

export default NowPlaying;