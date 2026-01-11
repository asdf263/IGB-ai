import React, { useContext } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { IconButton } from 'react-native-paper';
import { AuthContext } from '../context/AuthContext';
import AuthNavigator from './AuthNavigator';

// #region agent log - debug import fix
console.log('[DEBUG-H1] About to import screens');
// #endregion

// Import screens directly (they use export default)
const AnalysisScreen = require('../screens/AnalysisScreen').default;
const VectorDetailScreen = require('../screens/VectorDetailScreen').default;
const ProfileScreen = require('../screens/ProfileScreen').default;
const BrowseUsersScreen = require('../screens/BrowseUsersScreen').default;
const ChatWithUserScreen = require('../screens/ChatWithUserScreen').default;
const ChatDataUploadScreen = require('../screens/ChatDataUploadScreen').default;

// #region agent log - debug import validation
console.log('[DEBUG-H1] AnalysisScreen type:', typeof AnalysisScreen);
console.log('[DEBUG-H1] VectorDetailScreen type:', typeof VectorDetailScreen);
console.log('[DEBUG-H1] ProfileScreen type:', typeof ProfileScreen);
console.log('[DEBUG-H1] BrowseUsersScreen type:', typeof BrowseUsersScreen);
// #endregion

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

const TabIcon = ({ name, color, size }) => (
  <IconButton icon={name} iconColor={color} size={size} />
);

const MainTabs = () => (
  <Tab.Navigator
    screenOptions={{
      tabBarActiveTintColor: '#E07A5F',
      tabBarInactiveTintColor: '#999',
      headerShown: false,
    }}
  >
    <Tab.Screen
      name="Browse"
      component={BrowseUsersScreen}
      options={{
        tabBarLabel: 'Browse',
        tabBarIcon: ({ color, size }) => <TabIcon name="account-search" color={color} size={size} />,
      }}
    />
    <Tab.Screen
      name="Profile"
      component={ProfileScreen}
      options={{
        tabBarLabel: 'Profile',
        tabBarIcon: ({ color, size }) => <TabIcon name="account" color={color} size={size} />,
      }}
    />
  </Tab.Navigator>
);

const MainAppNavigator = () => (
  <Stack.Navigator
    screenOptions={{
      headerStyle: { backgroundColor: '#E07A5F' },
      headerTintColor: '#fff',
      headerTitleStyle: { fontWeight: 'bold' },
    }}
  >
    <Stack.Screen name="Main" component={MainTabs} options={{ title: 'IGB AI' }} />
    <Stack.Screen name="Analysis" component={AnalysisScreen} options={{ title: 'Analysis' }} />
    <Stack.Screen name="VectorDetail" component={VectorDetailScreen} options={{ title: 'Vector Details' }} />
    <Stack.Screen name="UserProfile" component={ProfileScreen} options={{ title: 'User Profile' }} />
    <Stack.Screen name="ChatWithUser" component={ChatWithUserScreen} options={{ title: 'AI Chat' }} />
    <Stack.Screen name="ChatDataUpload" component={ChatDataUploadScreen} options={{ title: 'Upload Chat Data' }} />
  </Stack.Navigator>
);

const AppNavigator = () => {
  const { isAuthenticated, isLoading } = useContext(AuthContext) || {};

  console.log('[NAV] AppNavigator render - isAuthenticated:', isAuthenticated, 'isLoading:', isLoading);

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#E07A5F" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      {isAuthenticated ? <MainAppNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
};

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
});

export default AppNavigator;
