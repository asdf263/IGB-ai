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
  // #region agent log
  console.log('[API] signup called', {email, baseURL: api.defaults.baseURL, url: '/api/users/signup'});
  fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'authApi.js:25',message:'signup API call entry',data:{email,password_length:password?.length,baseURL:api.defaults.baseURL},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
  // #endregion
  try {
    // #region agent log
    console.log('[API] Making POST request to /api/users/signup', {email});
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'authApi.js:27',message:'before axios post',data:{url:'/api/users/signup'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
    // #endregion
    const response = await api.post('/api/users/signup', {
      email,
      password,
    });
    // #region agent log
    console.log('[API] signup response received', {status: response.status, success: response.data?.success, uid: response.data?.uid});
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'authApi.js:32',message:'axios response received',data:{status:response.status,has_data:!!response.data,success:response.data?.success},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
    // #endregion
    return response.data;
  } catch (error) {
    // #region agent log
    console.log('[API] signup error', {message: error.message, status: error.response?.status, code: error.code, responseData: error.response?.data});
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'authApi.js:35',message:'signup API error',data:{error_message:error.message,error_response:error.response?.data,status:error.response?.status,code:error.code},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
    // #endregion
    throw new Error(error.response?.data?.error || error.message || 'Signup failed');
  }
};

/**
 * Log in a user
 * @param {string} email - User email/username
 * @param {string} password - User password
 * @returns {Promise} Login result with uid and user profile
 */
export const login = async (email, password) => {
  // #region agent log
  console.log('[API] login called', {email, baseURL: api.defaults.baseURL, url: '/api/users/login'});
  fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'authApi.js:55',message:'login API call entry',data:{email,password_length:password?.length,baseURL:api.defaults.baseURL},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
  // #endregion
  try {
    // #region agent log
    console.log('[API] Making POST request to /api/users/login', {email});
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'authApi.js:57',message:'before axios post login',data:{url:'/api/users/login'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
    // #endregion
    const response = await api.post('/api/users/login', {
      email,
      password,
    });
    // #region agent log
    console.log('[API] login response received', {status: response.status, success: response.data?.success, uid: response.data?.uid});
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'authApi.js:62',message:'axios login response received',data:{status:response.status,has_data:!!response.data,success:response.data?.success},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
    // #endregion
    return response.data;
  } catch (error) {
    // #region agent log
    console.log('[API] login error', {message: error.message, status: error.response?.status, code: error.code, responseData: error.response?.data});
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'authApi.js:65',message:'login API error',data:{error_message:error.message,error_response:error.response?.data,status:error.response?.status,code:error.code},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
    // #endregion
    throw new Error(error.response?.data?.error || error.message || 'Login failed');
  }
};

export default api;

