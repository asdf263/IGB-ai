import axios from 'axios';

const API_BASE_URL = __DEV__
  ? 'http://localhost:5000'
  : 'https://your-production-api.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Extract features from chat messages
 * @param {Array} messages - Array of message objects
 * @param {boolean} store - Whether to store the vector
 * @returns {Promise} Extraction result
 */
export const extractFeatures = async (messages, store = false) => {
  try {
    const response = await api.post('/api/features/extract', {
      messages,
      store,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message);
  }
};

/**
 * Generate synthetic vectors
 * @param {Array} vectors - Source vectors
 * @param {number} nSynthetic - Number to generate
 * @param {string} method - Generation method
 * @param {boolean} store - Whether to store results
 * @returns {Promise} Generation result
 */
export const generateSynthetic = async (vectors, nSynthetic = 10, method = 'smote', store = false) => {
  try {
    const response = await api.post('/api/features/synthetic-generate', {
      vectors,
      n_synthetic: nSynthetic,
      method,
      store,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message);
  }
};

/**
 * List all stored vectors
 * @returns {Promise} List of vectors
 */
export const listVectors = async () => {
  try {
    const response = await api.get('/api/vectors/list');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message);
  }
};

/**
 * Get a specific vector by ID
 * @param {string} vectorId - Vector ID
 * @returns {Promise} Vector data
 */
export const getVector = async (vectorId) => {
  try {
    const response = await api.get(`/api/vectors/${vectorId}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message);
  }
};

/**
 * Delete a vector by ID
 * @param {string} vectorId - Vector ID
 * @returns {Promise} Deletion result
 */
export const deleteVector = async (vectorId) => {
  try {
    const response = await api.delete(`/api/vectors/${vectorId}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message);
  }
};

/**
 * Cluster vectors
 * @param {Object} options - Clustering options
 * @returns {Promise} Clustering result
 */
export const clusterVectors = async (options = {}) => {
  try {
    const response = await api.post('/api/vectors/cluster', {
      vectors: options.vectors,
      cluster_method: options.clusterMethod || 'kmeans',
      reduce_method: options.reduceMethod || 'pca',
      n_clusters: options.nClusters || 5,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message);
  }
};

/**
 * Get visualization graph data
 * @returns {Promise} Graph data
 */
export const getVisualizationGraph = async () => {
  try {
    const response = await api.get('/api/visualization/graph');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message);
  }
};

/**
 * Get heatmap data
 * @param {Object} options - Heatmap options
 * @returns {Promise} Heatmap data
 */
export const getHeatmap = async (options = {}) => {
  try {
    const response = await api.post('/api/visualization/heatmap', options);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message);
  }
};

/**
 * Get radar chart data
 * @param {Object} options - Radar options
 * @returns {Promise} Radar data
 */
export const getRadarData = async (options = {}) => {
  try {
    const response = await api.post('/api/visualization/radar', options);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message);
  }
};

/**
 * Search for similar vectors
 * @param {Array} queryVector - Query vector
 * @param {number} topK - Number of results
 * @param {number} threshold - Similarity threshold
 * @returns {Promise} Search results
 */
export const searchVectors = async (queryVector, topK = 5, threshold = 0.0) => {
  try {
    const response = await api.post('/api/vectors/search', {
      query_vector: queryVector,
      top_k: topK,
      threshold,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message);
  }
};

/**
 * Get feature labels
 * @returns {Promise} Feature labels
 */
export const getFeatureLabels = async () => {
  try {
    const response = await api.get('/api/features/labels');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message);
  }
};

/**
 * Health check
 * @returns {Promise} Health status
 */
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message);
  }
};

export default api;
