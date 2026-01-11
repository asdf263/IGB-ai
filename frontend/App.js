// #region agent log
console.log('[APP] App.js module loading');
// #endregion

import 'react-native-gesture-handler';

// #region agent log
console.log('[APP] gesture-handler imported');
// #endregion

import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { Provider as PaperProvider, DefaultTheme } from 'react-native-paper';
import { AppProvider } from './src/context/AppContext';
import { AuthProvider } from './src/context/AuthContext';
import AppNavigator from './src/navigation/AppNavigator';

// #region agent log
console.log('[APP] All imports complete');
// #endregion

const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#6200ee',
    accent: '#03dac4',
    background: '#f5f5f5',
    surface: '#ffffff',
    error: '#B00020',
  },
};

export default function App() {
  // #region agent log
  console.log('[APP] App function rendering');
  // #endregion
  
  return (
    <PaperProvider theme={theme}>
      <AuthProvider>
        <AppProvider>
          <StatusBar style="light" />
          <AppNavigator />
        </AppProvider>
      </AuthProvider>
    </PaperProvider>
  );
}
