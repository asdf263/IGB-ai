import axios from 'axios';

const API_BASE_URL = __DEV__ 
  ? 'http://localhost:5000'  // For iOS simulator, use localhost
  : 'https://your-production-api.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for large file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Upload a file to the backend
 * @param {Object} file - File object from document picker
 * @returns {Promise} Upload response
 */
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', {
    uri: file.uri,
    type: file.type || 'text/plain',
    name: file.name,
  });

  const response = await api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Analyze text using Gemini
 * @param {string} text - Text to analyze
 * @param {string} analysisType - Type of analysis (general, summary, sentiment, keywords, qa)
 * @returns {Promise} Analysis result
 */
export const analyzeText = async (text, analysisType = 'general') => {
  const response = await api.post('/api/analyze', {
    text,
    analysis_type: analysisType,
  });

  return response.data;
};

/**
 * Analyze uploaded file
 * @param {Object} file - File object from document picker
 * @param {string} analysisType - Type of analysis
 * @returns {Promise} Analysis result
 */
export const analyzeFile = async (file, analysisType = 'general') => {
  const formData = new FormData();
  formData.append('file', {
    uri: file.uri,
    type: file.type || 'text/plain',
    name: file.name,
  });
  formData.append('analysis_type', analysisType);

  const response = await api.post('/api/analyze-file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Chat with Gemini
 * @param {string} message - User message
 * @param {string} context - Conversation context
 * @returns {Promise} Chat response
 */
export const chat = async (message, context = '') => {
  const response = await api.post('/api/chat', {
    message,
    context,
  });

  return response.data;
};

/**
 * Health check
 * @returns {Promise} Health status
 */
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;

