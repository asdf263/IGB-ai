import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const extractFeatures = async (messages, store = false) => {
  const response = await api.post('/api/features/extract', { messages, store })
  return response.data
}

export const generateSynthetic = async (vectors, nSynthetic = 10, method = 'smote', store = false) => {
  const response = await api.post('/api/features/synthetic-generate', {
    vectors,
    n_synthetic: nSynthetic,
    method,
    store,
  })
  return response.data
}

export const listVectors = async () => {
  const response = await api.get('/api/vectors/list')
  return response.data
}

export const getVector = async (vectorId) => {
  const response = await api.get(`/api/vectors/${vectorId}`)
  return response.data
}

export const deleteVector = async (vectorId) => {
  const response = await api.delete(`/api/vectors/${vectorId}`)
  return response.data
}

export const clusterVectors = async (options = {}) => {
  const response = await api.post('/api/vectors/cluster', {
    vectors: options.vectors,
    cluster_method: options.clusterMethod || 'kmeans',
    reduce_method: options.reduceMethod || 'pca',
    n_clusters: options.nClusters || 5,
  })
  return response.data
}

export const getVisualizationGraph = async () => {
  const response = await api.get('/api/visualization/graph')
  return response.data
}

export const getHeatmap = async (options = {}) => {
  const response = await api.post('/api/visualization/heatmap', options)
  return response.data
}

export const getRadarData = async (options = {}) => {
  const response = await api.post('/api/visualization/radar', options)
  return response.data
}

export const searchVectors = async (queryVector, topK = 5, threshold = 0.0) => {
  const response = await api.post('/api/vectors/search', {
    query_vector: queryVector,
    top_k: topK,
    threshold,
  })
  return response.data
}

export const getFeatureLabels = async () => {
  const response = await api.get('/api/features/labels')
  return response.data
}

export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

export default api
