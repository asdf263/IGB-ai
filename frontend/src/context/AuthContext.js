// #region agent log
console.log('[AUTH] AuthContext.js module loading');
// #endregion

import React, { createContext, useState, useEffect, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as authApi from '../services/authApi';
import * as userApi from '../services/userApi';

// #region agent log
console.log('[AUTH] AuthContext imports complete');
// #endregion

export const AuthContext = createContext();

const AUTH_STORAGE_KEY = '@igb_ai:auth';

export const AuthProvider = ({ children }) => {
  // #region agent log
  console.log('[AUTH] AuthProvider rendering');
  // #endregion

  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load auth state from storage on mount
  useEffect(() => {
    // #region agent log
    console.log('[AUTH] useEffect mounting, calling loadAuthState');
    // #endregion
    loadAuthState();
  }, []);

  const loadAuthState = async () => {
    // #region agent log
    console.log('[AUTH] loadAuthState starting');
    // #endregion
    try {
      const storagePromise = AsyncStorage.getItem(AUTH_STORAGE_KEY);
      const timeoutPromise = new Promise((resolve) => 
        setTimeout(() => resolve(null), 2000)
      );
      
      // #region agent log
      console.log('[AUTH] Waiting for AsyncStorage with timeout');
      // #endregion
      
      const storedAuth = await Promise.race([storagePromise, timeoutPromise]);
      
      // #region agent log
      console.log('[AUTH] AsyncStorage result:', storedAuth ? 'has data' : 'no data');
      // #endregion
      
      if (storedAuth) {
        try {
          const authData = JSON.parse(storedAuth);
          setUser(authData);
          setIsAuthenticated(true);
          // #region agent log
          console.log('[AUTH] User restored from storage');
          // #endregion
        } catch (parseError) {
          console.warn('Error parsing auth data:', parseError);
        }
      }
    } catch (error) {
      console.warn('Error loading auth state:', error.message);
    } finally {
      // #region agent log
      console.log('[AUTH] loadAuthState complete, setting isLoading=false');
      // #endregion
      setIsLoading(false);
    }
  };

  const saveAuthState = async (userData) => {
    try {
      await AsyncStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(userData));
    } catch (error) {
      console.error('Error saving auth state:', error);
    }
  };

  const clearAuthState = async () => {
    try {
      await AsyncStorage.removeItem(AUTH_STORAGE_KEY);
    } catch (error) {
      console.error('Error clearing auth state:', error);
    }
  };

  const signup = useCallback(async (email, password) => {
    try {
      setError(null);
      setIsLoading(true);
      
      const result = await authApi.signup(email, password);
      
      const userData = {
        uid: result.uid,
        email: email,
        profile: {},
        onboarding_complete: false,
      };
      
      setUser(userData);
      setIsAuthenticated(true);
      await saveAuthState(userData);
      
      return { success: true, user: userData };
    } catch (error) {
      setError(error.message);
      return { success: false, error: error.message };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (email, password) => {
    try {
      setError(null);
      setIsLoading(true);
      
      const result = await authApi.login(email, password);
      
      const userData = {
        uid: result.uid,
        email: email,
        profile: result.user_profile?.profile || {},
        onboarding_complete: result.user_profile?.onboarding_complete || false,
      };
      
      setUser(userData);
      setIsAuthenticated(true);
      await saveAuthState(userData);
      
      return { success: true, user: userData };
    } catch (error) {
      setError(error.message);
      return { success: false, error: error.message };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      setUser(null);
      setIsAuthenticated(false);
      await clearAuthState();
    } catch (error) {
      console.error('Error logging out:', error);
    }
  }, []);

  const updateProfile = useCallback(async (profileData) => {
    try {
      if (!user?.uid) {
        throw new Error('User not authenticated');
      }
      
      setError(null);
      const result = await userApi.updateProfile(user.uid, profileData);
      
      const updatedUser = {
        ...user,
        profile: result.profile,
      };
      
      setUser(updatedUser);
      await saveAuthState(updatedUser);
      
      return { success: true, profile: result.profile };
    } catch (error) {
      setError(error.message);
      return { success: false, error: error.message };
    }
  }, [user]);

  const refreshUser = useCallback(async () => {
    try {
      if (!user?.uid) {
        return;
      }
      
      const result = await userApi.getUser(user.uid);
      
      const updatedUser = {
        uid: result.metadata.uid,
        email: result.metadata.email,
        profile: result.profile,
        onboarding_complete: result.metadata.onboarding_complete,
      };
      
      setUser(updatedUser);
      await saveAuthState(updatedUser);
    } catch (error) {
      console.error('Error refreshing user:', error);
    }
  }, [user]);

  const completeOnboarding = useCallback(async () => {
    try {
      if (!user?.uid) {
        throw new Error('User not authenticated');
      }
      
      await userApi.completeOnboarding(user.uid);
      
      const updatedUser = {
        ...user,
        onboarding_complete: true,
      };
      
      setUser(updatedUser);
      await saveAuthState(updatedUser);
      
      return { success: true };
    } catch (error) {
      setError(error.message);
      return { success: false, error: error.message };
    }
  }, [user]);

  const value = {
    user,
    isAuthenticated,
    isLoading,
    error,
    signup,
    login,
    logout,
    updateProfile,
    refreshUser,
    completeOnboarding,
    setError,
  };

  // #region agent log
  console.log('[AUTH] AuthProvider returning, isLoading:', isLoading);
  // #endregion

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
