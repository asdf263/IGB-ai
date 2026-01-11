import 'react-native-url-polyfill/auto';
import { createClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Constants from 'expo-constants';

// Get Supabase credentials from environment (using new key naming convention)
// SUPABASE_KEY is the new publishable key (replaces legacy anon key)
const supabaseUrl = Constants.expoConfig?.extra?.supabaseUrl || process.env.EXPO_PUBLIC_SUPABASE_URL;
const supabaseKey = Constants.expoConfig?.extra?.supabaseKey || process.env.EXPO_PUBLIC_SUPABASE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.warn('[SUPABASE] Missing Supabase credentials. Please set EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_KEY');
}

/**
 * Custom storage adapter for React Native using AsyncStorage
 * Supabase uses this to persist auth sessions
 */
const ExpoSecureStoreAdapter = {
  getItem: async (key) => {
    try {
      const value = await AsyncStorage.getItem(key);
      return value;
    } catch (error) {
      console.error('[SUPABASE] Error reading from storage:', error);
      return null;
    }
  },
  setItem: async (key, value) => {
    try {
      await AsyncStorage.setItem(key, value);
    } catch (error) {
      console.error('[SUPABASE] Error writing to storage:', error);
    }
  },
  removeItem: async (key) => {
    try {
      await AsyncStorage.removeItem(key);
    } catch (error) {
      console.error('[SUPABASE] Error removing from storage:', error);
    }
  },
};

/**
 * Supabase client instance
 * Configured with AsyncStorage for session persistence in React Native
 * Uses new publishable key (SUPABASE_KEY) instead of legacy anon key
 */
export const supabase = createClient(supabaseUrl || '', supabaseKey || '', {
  auth: {
    storage: ExpoSecureStoreAdapter,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false, // Not needed for React Native
  },
});

export default supabase;

