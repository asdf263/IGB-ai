import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { IconButton } from 'react-native-paper';

import {
  UploadScreen,
  AnalysisScreen,
  VectorDetailScreen,
  ClusterGraphScreen,
  SyntheticScreen,
} from '../screens';

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

const AppNavigator = () => {
  return (
    <NavigationContainer>
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
    </NavigationContainer>
  );
};

export default AppNavigator;
