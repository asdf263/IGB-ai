import { supabase } from './supabase';
import axios from 'axios';
import Constants from 'expo-constants';

const API_BASE_URL = Constants.expoConfig?.extra?.apiUrl || 'http://localhost:5000';

console.log('[AUTH API] Base URL:', API_BASE_URL);

// Axios instance for backend API calls (profile sync, etc.)
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

/**
 * Sign up a new user with Supabase authentication
 * @param {string} email - User email
 * @param {string} password - User password
 * @param {Object} profile - Optional profile data to sync with backend
 * @returns {Promise<Object>} - Signup result with user data
 */
export const signup = async (email, password, profile = {}) => {
  console.log('[AUTH API] Signup request:', { email, profile });
  
  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          // Store basic profile info in Supabase user metadata
          ...profile,
        },
      },
    });

    if (error) {
      console.log('[AUTH API] Supabase signup error:', error.message);
      throw new Error(error.message);
    }

    console.log('[AUTH API] Supabase signup success:', data.user?.id);

    // Sync profile data with backend
    if (data.user) {
      try {
        await syncProfileToBackend(data.user.id, email, profile);
      } catch (syncError) {
        console.warn('[AUTH API] Profile sync warning:', syncError.message);
        // Don't fail signup if backend sync fails
      }
    }

    return {
      uid: data.user?.id,
      email: data.user?.email,
      session: data.session,
      user: data.user,
    };
  } catch (error) {
    console.log('[AUTH API] Signup error:', error.message);
    throw new Error(error.message || 'Signup failed');
  }
};

/**
 * Log in a user with Supabase authentication
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise<Object>} - Login result with user data
 */
export const login = async (email, password) => {
  console.log('[AUTH API] Login request:', { email });
  
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      console.log('[AUTH API] Supabase login error:', error.message);
      throw new Error(error.message);
    }

    console.log('[AUTH API] Supabase login success:', data.user?.id);

    // Fetch profile from backend
    let userProfile = {};
    try {
      const profileResponse = await api.get(`/api/users/${data.user.id}`);
      userProfile = profileResponse.data?.profile || {};
    } catch (profileError) {
      console.warn('[AUTH API] Could not fetch profile from backend:', profileError.message);
    }

    return {
      uid: data.user?.id,
      email: data.user?.email,
      session: data.session,
      user: data.user,
      user_profile: { profile: userProfile },
    };
  } catch (error) {
    console.log('[AUTH API] Login error:', error.message);
    throw new Error(error.message || 'Login failed');
  }
};

/**
 * Log out the current user
 * @returns {Promise<void>}
 */
export const logout = async () => {
  console.log('[AUTH API] Logout request');
  
  try {
    const { error } = await supabase.auth.signOut();
    
    if (error) {
      console.log('[AUTH API] Supabase logout error:', error.message);
      throw new Error(error.message);
    }

    console.log('[AUTH API] Logout successful');
  } catch (error) {
    console.log('[AUTH API] Logout error:', error.message);
    throw new Error(error.message || 'Logout failed');
  }
};

/**
 * Get the current session
 * @returns {Promise<Object|null>} - Current session or null
 */
export const getSession = async () => {
  console.log('[AUTH API] Getting session');
  
  try {
    const { data, error } = await supabase.auth.getSession();
    
    if (error) {
      console.log('[AUTH API] Get session error:', error.message);
      return null;
    }

    console.log('[AUTH API] Session:', data.session ? 'exists' : 'none');
    return data.session;
  } catch (error) {
    console.log('[AUTH API] Get session error:', error.message);
    return null;
  }
};

/**
 * Get the current user
 * @returns {Promise<Object|null>} - Current user or null
 */
export const getUser = async () => {
  console.log('[AUTH API] Getting user');
  
  try {
    const { data, error } = await supabase.auth.getUser();
    
    if (error) {
      console.log('[AUTH API] Get user error:', error.message);
      return null;
    }

    return data.user;
  } catch (error) {
    console.log('[AUTH API] Get user error:', error.message);
    return null;
  }
};

/**
 * Sync user profile to backend after Supabase auth
 * @param {string} uid - User ID from Supabase
 * @param {string} email - User email
 * @param {Object} profile - Profile data
 */
const syncProfileToBackend = async (uid, email, profile) => {
  console.log('[AUTH API] Syncing profile to backend for:', uid);
  
  try {
    // Create or update user in backend
    const response = await api.post('/api/users/sync', {
      uid,
      email,
      profile,
    });
    console.log('[AUTH API] Profile sync response:', response.data);
    return response.data;
  } catch (error) {
    // If sync endpoint doesn't exist, try legacy signup endpoint
    console.log('[AUTH API] Sync failed, trying legacy approach');
    throw error;
  }
};

/**
 * Subscribe to auth state changes
 * @param {Function} callback - Callback function (event, session) => void
 * @returns {Object} - Subscription object with unsubscribe method
 */
export const onAuthStateChange = (callback) => {
  const { data: { subscription } } = supabase.auth.onAuthStateChange(callback);
  return subscription;
};

/**
 * Resend confirmation email to user
 * @param {string} email - User email address
 * @returns {Promise<void>}
 */
export const resendConfirmationEmail = async (email) => {
  console.log('[AUTH API] Resending confirmation email to:', email);
  
  try {
    const { error } = await supabase.auth.resend({
      type: 'signup',
      email: email,
    });

    if (error) {
      console.log('[AUTH API] Resend confirmation error:', error.message);
      throw new Error(error.message);
    }

    console.log('[AUTH API] Confirmation email resent successfully');
  } catch (error) {
    console.log('[AUTH API] Resend error:', error.message);
    throw new Error(error.message || 'Failed to resend confirmation email');
  }
};

/**
 * Send password reset email
 * @param {string} email - User email address
 * @returns {Promise<void>}
 */
export const resetPassword = async (email) => {
  console.log('[AUTH API] Sending password reset email to:', email);
  
  try {
    const { error } = await supabase.auth.resetPasswordForEmail(email);

    if (error) {
      console.log('[AUTH API] Password reset error:', error.message);
      throw new Error(error.message);
    }

    console.log('[AUTH API] Password reset email sent successfully');
  } catch (error) {
    console.log('[AUTH API] Reset error:', error.message);
    throw new Error(error.message || 'Failed to send password reset email');
  }
};

export default api;
