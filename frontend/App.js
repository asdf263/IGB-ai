import 'react-native-gesture-handler';
import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { Provider as PaperProvider, DefaultTheme } from 'react-native-paper';
import { AppProvider } from './src/context/AppContext';
import { AuthProvider } from './src/context/AuthContext';
import AppNavigator from './src/navigation/AppNavigator';

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
  fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'App.js:20',message:'Root App component rendering',data:{has_PaperProvider:true,has_AppProvider:true,has_AuthProvider:true},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
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
