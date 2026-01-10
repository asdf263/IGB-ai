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
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.js:20',message:'uploadFile entry',data:{file_name:file?.name,file_type:file?.type,has_uri:!!file?.uri},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
  // #endregion
  const formData = new FormData();
  formData.append('file', {
    uri: file.uri,
    type: file.type || 'text/plain',
    name: file.name,
  });
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.js:27',message:'FormData created, before request',data:{formData_keys:Array.from(formData.keys())},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
  // #endregion

  // Use axios directly for FormData - axios will automatically set Content-Type with boundary
  try {
    const response = await axios.post(`${API_BASE_URL}/api/upload`, formData);
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.js:32',message:'uploadFile success',data:{status:response.status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
    // #endregion
    return response.data;
  } catch (error) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.js:36',message:'uploadFile error',data:{error:error.message,status:error.response?.status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
    // #endregion
    throw error;
  }
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
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.js:55',message:'analyzeFile entry',data:{file_name:file?.name,analysis_type:analysisType},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
  // #endregion
  const formData = new FormData();
  formData.append('file', {
    uri: file.uri,
    type: file.type || 'text/plain',
    name: file.name,
  });
  formData.append('analysis_type', analysisType);
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.js:63',message:'FormData created for analyze, before request',data:{formData_keys:Array.from(formData.keys())},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
  // #endregion

  // Use axios directly for FormData - axios will automatically set Content-Type with boundary
  try {
    const response = await axios.post(`${API_BASE_URL}/api/analyze-file`, formData);
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.js:67',message:'analyzeFile success',data:{status:response.status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
    // #endregion
    return response.data;
  } catch (error) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.js:71',message:'analyzeFile error',data:{error:error.message,status:error.response?.status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
    // #endregion
    throw error;
  }
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

