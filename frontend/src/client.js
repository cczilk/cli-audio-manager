import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const trackAPI = {
  getAll: () => api.get('/tracks'),
  getOne: (id) => api.get(`/tracks/${id}`),
  delete: (id) => api.delete(`/tracks/${id}`),
};

export const playerAPI = {
  play: (trackId) => api.post('/player/play', { track_id: trackId }),
  pause: () => api.post('/player/pause'),
  stop: () => api.post('/player/stop'),
  next: () => api.post('/player/next'),
  previous: () => api.post('/player/previous'),
  setVolume: (volume) => api.post('/player/volume', { volume }),
  getStatus: () => api.get('/player/status'),
};

export const downloadAPI = {
  addToQueue: (url) => api.post('/download', { url }),
  getQueue: () => api.get('/download/queue'),
  processQueue: () => api.post('/download/process'),
};

export const playlistAPI = {
  getAll: () => api.get('/playlists'),
  getOne: (id) => api.get(`/playlists/${id}`),
  create: (name) => api.post('/playlists', { name }),
  addTrack: (playlistId, trackId) => 
    api.post(`/playlists/${playlistId}/tracks`, { track_id: trackId }),
  play: (playlistId) => api.post(`/playlists/${playlistId}/play`),
};

export default api;