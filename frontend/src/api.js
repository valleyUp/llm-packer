const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json();
}

export const api = {
  checkModelSize: (data) => request('/check-size', { method: 'POST', body: JSON.stringify(data) }),
  startDownload: (data) => request('/download/start', { method: 'POST', body: JSON.stringify(data) }),
  getTaskStatus: (id) => request(`/download/progress/${id}`),
  cancelTask: (id) => request(`/download/cancel/${id}`, { method: 'POST' }),
  archiveModel: (data) => request('/archive', { method: 'POST', body: JSON.stringify(data) }),
  healthCheck: () => request('/health'),
};
