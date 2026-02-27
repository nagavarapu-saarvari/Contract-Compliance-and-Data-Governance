import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Health check
  health: () => api.get('/health'),

  // PDF processing
  processPdf: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/process-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Python compliance check
  checkCompliance: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/check-compliance', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Get all rules
  getRules: () => api.get('/rules'),
};

export default api;
