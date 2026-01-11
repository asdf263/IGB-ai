import React, { createContext, useState, useEffect, useCallback, useRef } from 'react';
import * as authApi from '../services/authApi';
import { getUser as getUserFromBackend } from '../services/userApi';
import axios from 'axios';
import Constants from 'expo-constants';

const API_BASE_URL = Constants.expoConfig?.extra?.apiUrl || 'http://localhost:5000';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Flag to prevent auto-auth after signup
  const justSignedUp = useRef(false);

  console.log('[AUTH] Rendering, isAuthenticated:', isAuthenticated, 'isLoading:', isLoading);

  useEffect(() => {
    // Initialize auth state from Supabase session
    initializeAuth();

    // Subscribe to auth state changes
    const subscription = authApi.onAuthStateChange((event, session) => {
      console.log('[AUTH] Auth state changed:', event);
      handleAuthStateChange(event, session);
    });

    // Cleanup subscription on unmount
    return () => {
      subscription?.unsubscribe();
    };
  }, []);

  /**
   * Check if user's email is verified
   */
  const isEmailVerified = (supabaseUser) => {
    return supabaseUser?.email_confirmed_at != null;
  };

  /**
   * Sync user to MongoDB if they don't exist (fallback for failed syncs during signup)
   */
  const ensureUserInMongoDB = async (supabaseUser) => {
    const uid = supabaseUser.id;
    const email = supabaseUser.email;
    const supabaseProfile = supabaseUser.user_metadata || {};
    
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:ensureUserInMongoDB',message:'Starting MongoDB sync',data:{uid,email,apiUrl:API_BASE_URL},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H1-H2'})}).catch(()=>{});
    // #endregion
    
    try {
      // Try to fetch user from MongoDB
      const backendUser = await getUserFromBackend(uid);
      console.log('[AUTH] User found in MongoDB:', backendUser?.profile);
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:ensureUserInMongoDB',message:'User found in MongoDB',data:{uid,profile:backendUser?.profile},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H1'})}).catch(()=>{});
      // #endregion
      return backendUser?.profile || supabaseProfile;
    } catch (err) {
      // User doesn't exist in MongoDB - need to sync
      console.log('[AUTH] User not found in MongoDB, syncing...', err.message);
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:ensureUserInMongoDB',message:'User not in MongoDB - attempting sync',data:{uid,errorMsg:err.message,apiUrl:API_BASE_URL},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H1'})}).catch(()=>{});
      // #endregion
      
      try {
        const syncResponse = await axios.post(`${API_BASE_URL}/api/users/sync`, {
          uid,
          email,
          profile: supabaseProfile,
        });
        console.log('[AUTH] User synced to MongoDB:', syncResponse.data);
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:ensureUserInMongoDB',message:'Sync SUCCESS',data:{uid,response:syncResponse.data},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H1'})}).catch(()=>{});
        // #endregion
        return syncResponse.data?.profile || supabaseProfile;
      } catch (syncErr) {
        console.warn('[AUTH] Failed to sync user to MongoDB:', syncErr.message);
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AuthContext.js:ensureUserInMongoDB',message:'Sync FAILED',data:{uid,errorMsg:syncErr.message,errorCode:syncErr.response?.status,apiUrl:API_BASE_URL},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H1-H3'})}).catch(()=>{});
        // #endregion
        // Return Supabase profile as fallback
        return supabaseProfile;
      }
    }
  };

  /**
   * Initialize auth state from existing Supabase session
   */
  const initializeAuth = async () => {
    console.log('[AUTH] Initializing auth state...');
    try {
      const currentSession = await authApi.getSession();
      
      if (currentSession && currentSession.user) {
        const emailVerified = isEmailVerified(currentSession.user);
        console.log('[AUTH] Found existing session for:', currentSession.user?.email, 'verified:', emailVerified);
        
        // Only authenticate if email is verified
        if (emailVerified) {
          // Ensure user exists in MongoDB and get profile
          const profile = await ensureUserInMongoDB(currentSession.user);
          
          const userData = {
            uid: currentSession.user.id,
            email: currentSession.user.email,
            profile: profile,
            emailVerified: true,
            createdAt: currentSession.user.created_at,
          };
          
          setUser(userData);
          setSession(currentSession);
          setIsAuthenticated(true);
        } else {
          console.log('[AUTH] Email not verified, not authenticating');
          // Sign out unverified user
          await authApi.logout();
          setUser(null);
          setSession(null);
          setIsAuthenticated(false);
        }
      } else {
        console.log('[AUTH] No existing session found');
        setUser(null);
        setSession(null);
        setIsAuthenticated(false);
      }
    } catch (err) {
      console.log('[AUTH] Error initializing auth:', err.message);
      setUser(null);
      setSession(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle Supabase auth state changes
   */
  const handleAuthStateChange = (event, newSession) => {
    console.log('[AUTH] Handling auth state change:', event, 'justSignedUp:', justSignedUp.current);
    
    // Skip auto-auth if user just signed up (need email verification)
    if (justSignedUp.current && event === 'SIGNED_IN') {
      console.log('[AUTH] Skipping auto-auth after signup');
      justSignedUp.current = false;
      return;
    }
    
    switch (event) {
      case 'SIGNED_IN':
        if (newSession?.user) {
          const emailVerified = isEmailVerified(newSession.user);
          console.log('[AUTH] SIGNED_IN - email verified:', emailVerified);
          
          // Only authenticate if email is verified
          if (emailVerified) {
            const userData = mapSupabaseUser(newSession.user);
            setUser(userData);
            setSession(newSession);
            setIsAuthenticated(true);
          } else {
            console.log('[AUTH] Email not verified, staying on auth flow');
          }
        }
        break;
      
      case 'SIGNED_OUT':
        setUser(null);
        setSession(null);
        setIsAuthenticated(false);
        break;
      
      case 'TOKEN_REFRESHED':
        console.log('[AUTH] Token refreshed');
        if (newSession?.user && isEmailVerified(newSession.user)) {
          setSession(newSession);
        }
        break;
      
      case 'USER_UPDATED':
        if (newSession?.user && isEmailVerified(newSession.user)) {
          const userData = mapSupabaseUser(newSession.user);
          setUser(userData);
        }
        break;
      
      default:
        console.log('[AUTH] Unhandled auth event:', event);
    }
  };

  /**
   * Map Supabase user object to app user structure
   */
  const mapSupabaseUser = (supabaseUser) => {
    if (!supabaseUser) return null;
    
    return {
      uid: supabaseUser.id,
      email: supabaseUser.email,
      profile: supabaseUser.user_metadata || {},
      emailVerified: supabaseUser.email_confirmed_at != null,
      createdAt: supabaseUser.created_at,
    };
  };

  /**
   * Sign up a new user
   * Does NOT auto-authenticate - user must verify email first
   */
  const signup = useCallback(async (email, password, profileData = {}) => {
    console.log('[AUTH] Signup called for:', email);
    console.log('[AUTH] Profile data:', profileData);
    
    try {
      setError(null);
      
      // Set flag to prevent auto-auth from onAuthStateChange
      justSignedUp.current = true;
      
      const result = await authApi.signup(email, password, profileData);
      console.log('[AUTH] Signup API result:', result);
      
      // Sign out immediately - user needs to verify email first
      // This prevents auto-login after signup
      try {
        await authApi.logout();
      } catch (logoutErr) {
        console.log('[AUTH] Post-signup logout (expected):', logoutErr.message);
      }
      
      // Do NOT set authenticated - user must verify email and login
      console.log('[AUTH] Signup successful, awaiting email verification');
      // Return the uid so caller can upload chat data for this user
      return { success: true, email: email, uid: result.uid };
    } catch (err) {
      console.log('[AUTH] Signup error:', err.message);
      justSignedUp.current = false;
      setError(err.message);
      return { success: false, error: err.message };
    }
  }, []);

  /**
   * Log in an existing user
   * Will fail if email not verified (Supabase default behavior)
   */
  const login = useCallback(async (email, password) => {
    console.log('[AUTH] Login called for:', email);
    
    try {
      setError(null);
      setIsLoading(true);
      
      const result = await authApi.login(email, password);
      console.log('[AUTH] Login API result:', result);
      
      // Check if email is verified
      if (result.user && !isEmailVerified(result.user)) {
        console.log('[AUTH] Login failed - email not verified');
        await authApi.logout();
        throw new Error('Email not confirmed. Please check your inbox and verify your email.');
      }
      
      // Ensure user exists in MongoDB and get profile
      // This handles cases where signup sync failed
      let profile = result.user_profile?.profile || {};
      
      if (result.user && Object.keys(profile).length === 0) {
        console.log('[AUTH] Empty profile from backend, trying to sync...');
        profile = await ensureUserInMongoDB(result.user);
      }
      
      // User state will be updated via onAuthStateChange
      // But we also set it here for immediate feedback
      const userData = {
        uid: result.uid,
        email: result.email,
        profile: profile,
        emailVerified: true,
      };
      
      setUser(userData);
      setSession(result.session);
      setIsAuthenticated(true);
      
      console.log('[AUTH] Login successful with profile:', profile);
      return { success: true, user: userData };
    } catch (err) {
      console.log('[AUTH] Login error:', err.message);
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Log out the current user
   */
  const logout = useCallback(async () => {
    console.log('[AUTH] Logout called');
    
    try {
      await authApi.logout();
      // State will be cleared via onAuthStateChange
      // But we also clear it here for immediate feedback
      setUser(null);
      setSession(null);
      setIsAuthenticated(false);
      console.log('[AUTH] Logout successful');
    } catch (err) {
      console.log('[AUTH] Logout error:', err.message);
      // Still clear local state even if API call fails
      setUser(null);
      setSession(null);
      setIsAuthenticated(false);
    }
  }, []);

  /**
   * Update the user's profile data locally
   * (Used after profile sync with backend)
   */
  const updateUserProfile = useCallback((profileData) => {
    setUser((prevUser) => ({
      ...prevUser,
      profile: { ...prevUser?.profile, ...profileData },
    }));
  }, []);

  const value = {
    user,
    session,
    isAuthenticated,
    isLoading,
    error,
    signup,
    login,
    logout,
    setError,
    updateUserProfile,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
