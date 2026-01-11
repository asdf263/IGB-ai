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
 * Upload chat data and vectorize
 * @param {string} uid - User UID
 * @param {Object} file - File object (from DocumentPicker)
 * @returns {Promise} Upload result with vector_id
 */
export const uploadChatData = async (uid, file) => {
  try {
    const formData = new FormData();
    formData.append('file', {
      uri: file.uri,
      type: file.mimeType || 'application/json',
      name: file.name || 'chat.json',
    });

    const response = await api.post(`/api/users/${uid}/upload-chat`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message || 'Failed to upload chat data');
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

