import { Download, Loader2 } from 'lucide-react';

function DownloadForm({ downloadUrl, setDownloadUrl, downloading, onSubmit }) {
  return (
    <div className="mb-6 bg-gray-900 border border-green-800 rounded p-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-green-500">$</span>
        <span className="text-green-600">download</span>
      </div>
      <form onSubmit={onSubmit} className="flex gap-2">
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
  );
}

export default DownloadForm;