import axios from 'axios';
import Constants from 'expo-constants';

const isDev = typeof __DEV__ !== 'undefined' ? __DEV__ : process.env.NODE_ENV === 'development';

const API_BASE_URL = Constants.expoConfig?.extra?.apiUrl || 
  (isDev
    ? 'http://localhost:5000'
    : 'https://your-production-api.com');

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get all users with pagination
 * @param {number} limit - Maximum number of users to return
 * @param {number} skip - Number of users to skip
 * @returns {Promise} List of users
 */
export const getAllUsers = async (limit = 100, skip = 0) => {
  try {
    const response = await api.get(`/api/users?limit=${limit}&skip=${skip}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message || 'Failed to get users');
  }
};

/**
 * Get user data by UID
 * @param {string} uid - User UID
 * @returns {Promise} User data
 */
export const getUser = async (uid) => {
  try {
    const response = await api.get(`/api/users/${uid}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message || 'Failed to get user');
  }
};

/**
 * Update user profile
 * @param {string} uid - User UID
 * @param {Object} profileData - Profile data
 * @returns {Promise} Updated profile
 */
export const updateProfile = async (uid, profileData) => {
  try {
    const response = await api.post(`/api/users/${uid}/profile`, profileData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message || 'Failed to update profile');
  }
};

/**
 * Detect file type from filename or MIME type
 * @param {Object} file - File object
 * @returns {Object} Object with mimeType and isZip flag
 */
const detectFileType = (file) => {
  const name = file.name?.toLowerCase() || '';
  const mimeType = file.mimeType?.toLowerCase() || '';
  
  const isZip = name.endsWith('.zip') || 
                mimeType === 'application/zip' || 
                mimeType === 'application/x-zip-compressed';
  
  return {
    isZip,
    mimeType: isZip ? 'application/zip' : (mimeType || 'application/json'),
    defaultName: isZip ? 'instagram_export.zip' : 'chat.json',
  };
};

/**
 * Upload chat data and vectorize
 * Supports JSON chat files and Instagram ZIP exports
 * @param {string} uid - User UID
 * @param {Object} file - File object (from DocumentPicker)
 * @returns {Promise} Upload result with vector_id
 */
export const uploadChatData = async (uid, file) => {
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'userApi.js:90',message:'uploadChatData entry',data:{uid:uid,fileName:file?.name,fileUri:file?.uri,fileMimeType:file?.mimeType,fileSize:file?.size},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H2'})}).catch(()=>{});
  // #endregion
  
  try {
    const { isZip, mimeType, defaultName } = detectFileType(file);
    
    // Longer timeout for ZIP files (they can be large and require more processing)
    const timeout = isZip ? 300000 : 120000; // 5 minutes for ZIP, 2 minutes for JSON
    
    const formData = new FormData();
    formData.append('file', {
      uri: file.uri,
      type: mimeType,
      name: file.name || defaultName,
    });

    console.log(`[userApi] Uploading ${isZip ? 'Instagram ZIP' : 'JSON'} file: ${file.name}`);
    
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'userApi.js:108',message:'Before API call',data:{endpoint:`/api/users/${uid}/upload-chat`,mimeType:mimeType,isZip:isZip},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H2'})}).catch(()=>{});
    // #endregion

    const response = await api.post(`/api/users/${uid}/upload-chat`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout,
    });
    
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'userApi.js:120',message:'API call success',data:{responseData:response.data,hasVectorId:!!response.data?.vector_id},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H2'})}).catch(()=>{});
    // #endregion
    
    return response.data;
  } catch (error) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'userApi.js:128',message:'API call error',data:{errorMessage:error.message,responseStatus:error.response?.status,responseData:error.response?.data},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H2'})}).catch(()=>{});
    // #endregion
    
    throw new Error(error.response?.data?.detail || error.response?.data?.error || error.message || 'Failed to upload chat data');
  }
};

/**
 * Mark onboarding as complete
 * @param {string} uid - User UID
 * @returns {Promise} Completion result
 */
export const completeOnboarding = async (uid) => {
  try {
    const response = await api.post(`/api/users/${uid}/complete-onboarding`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message || 'Failed to complete onboarding');
  }
};

/**
 * Get compatibility between two users
 * @param {string} uid1 - First user's UID (typically the current user)
 * @param {string} uid2 - Second user's UID (the user being viewed)
 * @returns {Promise} Compatibility data including score, strengths, challenges
 */
export const getUserCompatibility = async (uid1, uid2) => {
  try {
    const response = await api.get(`/api/users/${uid1}/compatibility/${uid2}`);
    return response.data;
  } catch (error) {
    // Return null for specific errors that indicate missing vectors
    if (error.response?.status === 400 || error.response?.status === 404) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Cannot calculate compatibility',
        compatibility: null
      };
    }
    throw new Error(error.response?.data?.detail || error.message || 'Failed to get compatibility');
  }
};

/**
 * Chat with an AI persona simulating a user
 * @param {string} uid - UID of the user to chat with (their AI persona)
 * @param {string} message - The message to send
 * @param {Array} conversationHistory - Previous messages [{role: 'user'|'assistant', content: '...'}]
 * @returns {Promise} Chat response
 */
export const chatWithUser = async (uid, message, conversationHistory = null) => {
  try {
    const response = await api.post(`/api/users/${uid}/chat`, {
      message,
      conversation_history: conversationHistory,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to chat');
  }
};

/**
 * Create or get a persona for a user
 * @param {string} uid - User UID
 * @returns {Promise} Persona data
 */
export const createUserPersona = async (uid) => {
  try {
    const response = await api.post(`/api/users/${uid}/persona`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to create persona');
  }
};

export default api;

