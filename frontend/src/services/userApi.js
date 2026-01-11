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

    const response = await api.post(`/api/users/${uid}/upload-chat`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout,
    });
    return response.data;
  } catch (error) {
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

export default api;

