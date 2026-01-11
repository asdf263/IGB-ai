import axios from 'axios';
import Constants from 'expo-constants';

const isDev = typeof __DEV__ !== 'undefined' ? __DEV__ : process.env.NODE_ENV === 'development';

const API_BASE_URL = Constants.expoConfig?.extra?.apiUrl || 
  (isDev
    ? 'http://localhost:5000'
    : 'https://your-production-api.com');

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Sign up a new user
 * @param {string} email - User email/username
 * @param {string} password - User password
 * @returns {Promise} Signup result with uid
 */
export const signup = async (email, password) => {
  try {
    const response = await api.post('/api/users/signup', {
      email,
      password,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.response?.data?.error || error.message || 'Signup failed');
  }
};

/**
 * Log in a user
 * @param {string} email - User email/username
 * @param {string} password - User password
 * @returns {Promise} Login result with uid and user profile
 */
export const login = async (email, password) => {
  try {
    const response = await api.post('/api/users/login', {
      email,
      password,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.response?.data?.error || error.message || 'Login failed');
  }
};

export default api;
