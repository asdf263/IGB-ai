import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { Provider as PaperProvider, DefaultTheme } from 'react-native-paper';
import { AppProvider } from './context/AppContext';
import { AuthProvider } from './context/AuthContext';
import AppNavigator from './navigation/AppNavigator';

const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#E07A5F',
    accent: '#81B29A',
    background: '#FAF9F7',
    surface: '#ffffff',
    error: '#D32F2F',
  },
};

export default function App() {
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
