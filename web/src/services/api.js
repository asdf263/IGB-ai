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

export const extractUserFeatures = async (messages, targetUser = null, store = false) => {
  const response = await api.post('/api/users/features', {
    messages,
    target_user: targetUser,
    store,
  })
  return response.data
}

export const calculateCompatibility = async (messages, user1 = null, user2 = null) => {
  const response = await api.post('/api/users/compatibility', {
    messages,
    user1,
    user2,
  })
  return response.data
}

export const getUserFeatureLabels = async () => {
  const response = await api.get('/api/users/labels')
  return response.data
}

export const saveAnalysis = async (messages, userFeatures = null, compatibility = null, conversationFeatures = null, metadata = null) => {
  const response = await api.post('/api/analyses/save', {
    messages,
    user_features: userFeatures,
    compatibility,
    conversation_features: conversationFeatures,
    metadata,
  })
  return response.data
}

export const listAnalyses = async (limit = 50, offset = 0) => {
  const response = await api.get('/api/analyses', { params: { limit, offset } })
  return response.data
}

export const getAnalysis = async (analysisId) => {
  const response = await api.get(`/api/analyses/${analysisId}`)
  return response.data
}

export const deleteAnalysis = async (analysisId) => {
  const response = await api.delete(`/api/analyses/${analysisId}`)
  return response.data
}

export const getUserHistory = async (username) => {
  const response = await api.get(`/api/analyses/user/${username}`)
  return response.data
}

// Personality Synthesis
export const synthesizePersonality = async (userName, userFeatures, sampleMessages = null) => {
  const response = await api.post('/api/personality/synthesize', {
    user_name: userName,
    user_features: userFeatures,
    sample_messages: sampleMessages,
  })
  return response.data
}

export const chatWithPersona = async (personaId, message, conversationHistory = null) => {
  const response = await api.post('/api/personality/chat', {
    persona_id: personaId,
    message,
    conversation_history: conversationHistory,
  })
  return response.data
}

// Ecosystem
export const listEcosystemPersonas = async () => {
  const response = await api.get('/api/ecosystem/personas')
  return response.data
}

export const getEcosystemPersona = async (personaId) => {
  const response = await api.get(`/api/ecosystem/personas/${personaId}`)
  return response.data
}

export const addPersonaToEcosystem = async (personaId, userName, personality, vector, sourceAnalysisId = null) => {
  const response = await api.post('/api/ecosystem/personas', {
    persona_id: personaId,
    user_name: userName,
    personality,
    vector,
    source_analysis_id: sourceAnalysisId,
  })
  return response.data
}

export const removePersonaFromEcosystem = async (personaId) => {
  const response = await api.delete(`/api/ecosystem/personas/${personaId}`)
  return response.data
}

export const computeEcosystemCompatibility = async (personaId1, personaId2) => {
  const response = await api.post('/api/ecosystem/compatibility', {
    persona_id_1: personaId1,
    persona_id_2: personaId2,
  })
  return response.data
}

export const findBestMatches = async (personaId, topK = 5) => {
  const response = await api.get(`/api/ecosystem/matches/${personaId}`, { params: { top_k: topK } })
  return response.data
}

export const getEcosystemStats = async () => {
  const response = await api.get('/api/ecosystem/stats')
  return response.data
}

export const createPersonasFromAnalysis = async (analysisId) => {
  const response = await api.post(`/api/ecosystem/from-analysis/${analysisId}`)
  return response.data
}

export default api
