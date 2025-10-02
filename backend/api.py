from flask import Flask, jsonify, request
from flask_cors import CORS
from player import MusicPlayer
from downloader import AudioDownloader
from database import Database
import os

app = Flask(__name__)
CORS(app)

player = MusicPlayer()
downloader = AudioDownloader()
db = Database()

# ============= TRACK ENDPOINTS =============

@app.route('/api/tracks', methods=['GET'])
def get_tracks():
    """
    Get all tracks from library.
    Returns JSON array of all tracks.
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, artist, duration, source_url, added_at FROM tracks")
    tracks = cursor.fetchall()
    conn.close()
    
    result = []
    for track in tracks:
        result.append({
            'id': track[0],
            'title': track[1],
            'artist': track[2],
            'duration': track[3],
            'source_url': track[4],
            'added_at': track[5]
        })
    
    return jsonify(result)

@app.route('/api/tracks/<int:track_id>', methods=['GET'])
def get_track(track_id):
    """Get single track by ID."""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, artist, duration, filepath, source_url FROM tracks WHERE id=?",
        (track_id,)
    )
    track = cursor.fetchone()
    conn.close()
    
    if not track:
        return jsonify({'error': 'Track not found'}), 404
    
    return jsonify({
        'id': track[0],
        'title': track[1],
        'artist': track[2],
        'duration': track[3],
        'filepath': track[4],
        'source_url': track[5]
    })

@app.route('/api/tracks/<int:track_id>', methods=['DELETE'])
def delete_track(track_id):
    """Delete track from library and filesystem."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT filepath FROM tracks WHERE id=?", (track_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'Track not found'}), 404
    
    filepath = result[0]
    cursor.execute("DELETE FROM tracks WHERE id=?", (track_id,))
    cursor.execute("DELETE FROM playlist_tracks WHERE track_id=?", (track_id,))
    conn.commit()
    conn.close()
    
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Warning: Could not delete file {filepath}: {e}")
    
    return jsonify({'message': 'Track deleted successfully'})

# ============= PLAYER ENDPOINTS =============

@app.route('/api/player/play', methods=['POST'])
def play():
    """Play a track or resume playback."""
    data = request.json or {}
    track_id = data.get('track_id')
    
    if track_id:
        success = player.play(track_id)
    else:
        success = player.play()
    
    if success:
        info = player.get_current_track_info()
        return jsonify({'status': 'playing', 'track': info})
    else:
        return jsonify({'error': 'Failed to play'}), 400

@app.route('/api/player/pause', methods=['POST'])
def pause():
    """Pause playback."""
    player.pause()
    return jsonify({'status': 'paused'})

@app.route('/api/player/stop', methods=['POST'])
def stop():
    """Stop playback."""
    player.stop()
    return jsonify({'status': 'stopped'})

@app.route('/api/player/next', methods=['POST'])
def next_track():
    """Skip to next track in queue."""
    success = player.next_track()
    
    if success:
        info = player.get_current_track_info()
        return jsonify({'status': 'playing', 'track': info})
    else:
        return jsonify({'error': 'No next track'}), 400

@app.route('/api/player/previous', methods=['POST'])
def previous_track():
    """Go to previous track."""
    success = player.previous_track()
    
    if success:
        info = player.get_current_track_info()
        return jsonify({'status': 'playing', 'track': info})
    else:
        return jsonify({'error': 'No previous track'}), 400

@app.route('/api/player/volume', methods=['POST'])
def set_volume():
    """Set player volume."""
    data = request.json
    
    if not data or 'volume' not in data:
        return jsonify({'error': 'Volume required'}), 400
    
    volume = data['volume']
    
    if not isinstance(volume, int) or volume < 0 or volume > 100:
        return jsonify({'error': 'Volume must be between 0-100'}), 400
    
    player.set_volume(volume)
    return jsonify({'volume': volume})

@app.route('/api/player/status', methods=['GET'])
def get_status():
    """Get current player status."""
    info = player.get_current_track_info()
    
    if info:
        return jsonify(info)
    else:
        return jsonify({
            'track_id': None,
            'is_playing': False,
            'title': None,
            'artist': None
        })

@app.route('/api/player/queue', methods=['GET'])
def get_player_queue():
    """Get the playback queue."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    queue_tracks = []
    for track_id in player.queue:
        cursor.execute(
            "SELECT id, title, artist FROM tracks WHERE id=?",
            (track_id,)
        )
        result = cursor.fetchone()
        if result:
            queue_tracks.append({
                'id': result[0],
                'title': result[1],
                'artist': result[2]
            })
    
    conn.close()
    
    return jsonify({
        'queue': queue_tracks,
        'current_index': player.current_queue_index
    })

@app.route('/api/player/queue', methods=['POST'])
def add_to_player_queue():
    """Add track to playback queue."""
    data = request.json
    
    if not data or 'track_id' not in data:
        return jsonify({'error': 'track_id required'}), 400
    
    track_id = data['track_id']
    player.add_to_queue(track_id)
    
    return jsonify({'message': 'Added to queue', 'track_id': track_id})

@app.route('/api/player/queue', methods=['DELETE'])
def clear_player_queue():
    """Clear the playback queue."""
    player.clear_queue()
    return jsonify({'message': 'Queue cleared'})

# ============= DOWNLOAD ENDPOINTS =============

@app.route('/api/download', methods=['POST'])
def add_download():
    """Add URL to download queue."""
    data = request.json
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL required'}), 400
    
    url = data['url']
    queue_id = downloader.add_to_queue(url)
    
    return jsonify({
        'message': 'Added to download queue',
        'queue_id': queue_id,
        'url': url
    })

@app.route('/api/download/queue', methods=['GET'])
def get_download_queue():
    """Get all items in download queue."""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, url, status, added_at FROM download_queue ORDER BY added_at")
    items = cursor.fetchall()
    conn.close()
    
    result = []
    for item in items:
        result.append({
            'id': item[0],
            'url': item[1],
            'status': item[2],
            'added_at': item[3]
        })
    
    return jsonify(result)

@app.route('/api/download/process', methods=['POST'])
def process_downloads():
    """Process all pending downloads in queue."""
    try:
        downloader.process_queue()
        return jsonify({'message': 'Downloads processed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= PLAYLIST ENDPOINTS =============

@app.route('/api/playlists', methods=['GET'])
def get_playlists():
    """Get all playlists."""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, created_at FROM playlists")
    playlists = cursor.fetchall()
    conn.close()
    
    result = []
    for playlist in playlists:
        result.append({
            'id': playlist[0],
            'name': playlist[1],
            'created_at': playlist[2]
        })
    
    return jsonify(result)

@app.route('/api/playlists', methods=['POST'])
def create_playlist():
    """Create new playlist."""
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Playlist name required'}), 400
    
    name = data['name']
    
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO playlists (name) VALUES (?)", (name,))
    playlist_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'id': playlist_id,
        'name': name
    }), 201

@app.route('/api/playlists/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    """Get playlist with all tracks."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, created_at FROM playlists WHERE id=?", (playlist_id,))
    playlist = cursor.fetchone()
    
    if not playlist:
        conn.close()
        return jsonify({'error': 'Playlist not found'}), 404
    
    cursor.execute('''
        SELECT t.id, t.title, t.artist, t.duration, pt.position
        FROM playlist_tracks pt
        JOIN tracks t ON pt.track_id = t.id
        WHERE pt.playlist_id = ?
        ORDER BY pt.position
    ''', (playlist_id,))
    
    tracks = cursor.fetchall()
    conn.close()
    
    track_list = []
    for track in tracks:
        track_list.append({
            'id': track[0],
            'title': track[1],
            'artist': track[2],
            'duration': track[3],
            'position': track[4]
        })
    
    return jsonify({
        'id': playlist[0],
        'name': playlist[1],
        'created_at': playlist[2],
        'tracks': track_list
    })

@app.route('/api/playlists/<int:playlist_id>/tracks', methods=['POST'])
def add_track_to_playlist(playlist_id):
    """Add track to playlist."""
    data = request.json
    
    if not data or 'track_id' not in data:
        return jsonify({'error': 'track_id required'}), 400
    
    track_id = data['track_id']
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM playlists WHERE id=?", (playlist_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Playlist not found'}), 404
    
    cursor.execute("SELECT id FROM tracks WHERE id=?", (track_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Track not found'}), 404
    
    cursor.execute(
        "SELECT MAX(position) FROM playlist_tracks WHERE playlist_id=?",
        (playlist_id,)
    )
    result = cursor.fetchone()
    next_position = (result[0] or 0) + 1
    
    cursor.execute('''
        INSERT INTO playlist_tracks (playlist_id, track_id, position)
        VALUES (?, ?, ?)
    ''', (playlist_id, track_id, next_position))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': 'Track added to playlist',
        'playlist_id': playlist_id,
        'track_id': track_id,
        'position': next_position
    })

@app.route('/api/playlists/<int:playlist_id>/tracks/<int:track_id>', methods=['DELETE'])
def remove_track_from_playlist(playlist_id, track_id):
    """Remove track from playlist."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM playlist_tracks WHERE playlist_id=? AND track_id=?",
        (playlist_id, track_id)
    )
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Track not in playlist'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Track removed from playlist'})

@app.route('/api/playlists/<int:playlist_id>/play', methods=['POST'])
def play_playlist(playlist_id):
    """Load and play a playlist."""
    success = player.load_playlist(playlist_id)
    
    if success:
        info = player.get_current_track_info()
        return jsonify({'status': 'playing', 'track': info})
    else:
        return jsonify({'error': 'Failed to load playlist'}), 400

# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

# ============= RUN SERVER =============

if __name__ == '__main__':
    print("Starting Music Player API server...")
    print("API will be available at: http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  GET  /api/tracks")
    print("  POST /api/download")
    print("  GET  /api/player/status")
    print("  POST /api/player/play")
    print("  GET  /api/playlists")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
