// #region agent log
console.log('[NAV] AppNavigator.js module loading');
// #endregion

import React, { useContext } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { IconButton } from 'react-native-paper';
import { AuthContext } from '../context/AuthContext';
import AuthNavigator from './AuthNavigator';
import OnboardingNavigator from './OnboardingNavigator';

// #region agent log
console.log('[NAV] AppNavigator imports complete');
// #endregion

// Lazy load screens - only import when needed
const createLazyScreen = (importFn) => {
  let Component = null;
  return (props) => {
    if (!Component) {
      Component = importFn();
    }
    return <Component {...props} />;
  };
};

// Lazy screen factories
const UploadScreen = createLazyScreen(() => require('../screens/UploadScreen').UploadScreen);
const AnalysisScreen = createLazyScreen(() => require('../screens/AnalysisScreen').AnalysisScreen);
const VectorDetailScreen = createLazyScreen(() => require('../screens/VectorDetailScreen').VectorDetailScreen);
const ClusterGraphScreen = createLazyScreen(() => require('../screens/ClusterGraphScreen').ClusterGraphScreen);
const SyntheticScreen = createLazyScreen(() => require('../screens/SyntheticScreen').SyntheticScreen);

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

const TabIcon = ({ name, color, size }) => (
  <IconButton icon={name} iconColor={color} size={size} />
);

const MainTabs = () => {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#6200ee',
        tabBarInactiveTintColor: '#999',
        headerShown: false,
      }}
      lazy={true}
    >
      <Tab.Screen
        name="Upload"
        component={UploadScreen}
        options={{
          tabBarLabel: 'Upload',
          tabBarIcon: ({ color, size }) => (
            <TabIcon name="cloud-upload" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen
        name="Clusters"
        component={ClusterGraphScreen}
        options={{
          tabBarLabel: 'Clusters',
          tabBarIcon: ({ color, size }) => (
            <TabIcon name="graph" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen
        name="Synthetic"
        component={SyntheticScreen}
        options={{
          tabBarLabel: 'Synthetic',
          tabBarIcon: ({ color, size }) => (
            <TabIcon name="creation" color={color} size={size} />
          ),
        }}
      />
    </Tab.Navigator>
  );
};

const MainAppNavigator = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#6200ee',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen
        name="Main"
        component={MainTabs}
        options={{ title: 'IGB AI - Behavior Vectors' }}
      />
      <Stack.Screen
        name="Analysis"
        component={AnalysisScreen}
        options={{ title: 'Analysis Results' }}
      />
      <Stack.Screen
        name="VectorDetail"
        component={VectorDetailScreen}
        options={{ title: 'Vector Details' }}
      />
      <Stack.Screen
        name="ClusterGraph"
        component={ClusterGraphScreen}
        options={{ title: 'Cluster Visualization' }}
      />
    </Stack.Navigator>
  );
};

const AppNavigator = () => {
  // #region agent log
  console.log('[NAV] AppNavigator function called');
  // #endregion
  
  const contextValue = useContext(AuthContext);
  const { isAuthenticated, isLoading, user } = contextValue || {};

  // #region agent log
  console.log('[NAV] Auth state:', { isAuthenticated, isLoading, hasUser: !!user });
  // #endregion

  if (isLoading) {
    // #region agent log
    console.log('[NAV] Showing loading indicator because isLoading=true');
    // #endregion
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#6200ee" />
      </View>
    );
  }

  // #region agent log
  console.log('[NAV] Rendering NavigationContainer, isAuthenticated:', isAuthenticated);
  // #endregion

  return (
    <NavigationContainer>
      {!isAuthenticated ? (
        <AuthNavigator />
      ) : !user?.onboarding_complete ? (
        <OnboardingNavigator />
      ) : (
        <MainAppNavigator />
      )}
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
