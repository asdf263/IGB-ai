import React, { createContext, useState, useEffect, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as authApi from '../services/authApi';
import * as userApi from '../services/userApi';

export const AuthContext = createContext();

const AUTH_STORAGE_KEY = '@igb_ai:auth';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load auth state from storage on mount
  useEffect(() => {
    loadAuthState();
  }, []);

  const loadAuthState = async () => {
    try {
      // Use Promise.race with timeout to prevent indefinite loading
      const storagePromise = AsyncStorage.getItem(AUTH_STORAGE_KEY);
      const timeoutPromise = new Promise((resolve) => 
        setTimeout(() => resolve(null), 2000)
      );
      
      const storedAuth = await Promise.race([storagePromise, timeoutPromise]);
      
      if (storedAuth) {
        try {
          const authData = JSON.parse(storedAuth);
          setUser(authData);
          setIsAuthenticated(true);
        } catch (parseError) {
          console.warn('Error parsing auth data:', parseError);
        }
      }
    } catch (error) {
      // Silently fail - user will just need to login again
      console.warn('Error loading auth state:', error.message);
    } finally {
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
    // #region agent log
    console.log('[AUTH] AuthContext.signup called', {email, passwordLength: password?.length});
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:64',message:'AuthContext signup entry',data:{email,password_length:password?.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
    // #endregion
    try {
      setError(null);
      setIsLoading(true);
      // #region agent log
      console.log('[AUTH] Calling authApi.signup', {email});
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:68',message:'before authApi.signup call',data:{email},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
      // #endregion
      const result = await authApi.signup(email, password);
      // #region agent log
      console.log('[AUTH] authApi.signup result', {hasUid: !!result?.uid, uid: result?.uid, success: result?.success});
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:70',message:'authApi.signup result received',data:{has_uid:!!result?.uid,success:result?.success,uid:result?.uid},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
      // #endregion
      
      const userData = {
        uid: result.uid,
        email: email,
        profile: {},
        onboarding_complete: false,
      };
      
      console.log('[AUTH] Setting user state', {uid: userData.uid});
      setUser(userData);
      setIsAuthenticated(true);
      await saveAuthState(userData);
      // #region agent log
      console.log('[AUTH] Signup complete, state saved');
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:79',message:'signup success, state updated',data:{uid:userData.uid},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
      // #endregion
      
      return { success: true, user: userData };
    } catch (error) {
      // #region agent log
      console.log('[AUTH] Signup error', {message: error.message, stack: error.stack?.substring(0,200)});
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:82',message:'signup error caught',data:{error_message:error.message,error_stack:error.stack?.substring(0,200)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
      // #endregion
      setError(error.message);
      return { success: false, error: error.message };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (email, password) => {
    // #region agent log
    console.log('[AUTH] AuthContext.login called', {email, passwordLength: password?.length});
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:111',message:'AuthContext login entry',data:{email,password_length:password?.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
    // #endregion
    try {
      setError(null);
      setIsLoading(true);
      // #region agent log
      console.log('[AUTH] Calling authApi.login', {email});
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:115',message:'before authApi.login call',data:{email},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
      // #endregion
      const result = await authApi.login(email, password);
      // #region agent log
      console.log('[AUTH] authApi.login result', {hasUid: !!result?.uid, uid: result?.uid, success: result?.success});
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:117',message:'authApi.login result received',data:{has_uid:!!result?.uid,success:result?.success,uid:result?.uid},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
      // #endregion
      
      const userData = {
        uid: result.uid,
        email: email,
        profile: result.user_profile?.profile || {},
        onboarding_complete: result.user_profile?.onboarding_complete || false,
      };
      
      console.log('[AUTH] Setting user state', {uid: userData.uid});
      setUser(userData);
      setIsAuthenticated(true);
      await saveAuthState(userData);
      // #region agent log
      console.log('[AUTH] Login complete, state saved');
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:125',message:'login success, state updated',data:{uid:userData.uid},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
      // #endregion
      
      return { success: true, user: userData };
    } catch (error) {
      // #region agent log
      console.log('[AUTH] Login error', {message: error.message, stack: error.stack?.substring(0,200)});
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:130',message:'login error caught',data:{error_message:error.message,error_stack:error.stack?.substring(0,200)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
      // #endregion
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
    setError,
  };
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:172',message:'AuthProvider rendering',data:{value_defined:typeof value !== 'undefined',has_isAuthenticated:value.isAuthenticated !== undefined,isAuthenticated:value.isAuthenticated,has_children:!!children},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
  // #endregion

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;

