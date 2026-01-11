import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import OnboardingStep1_Account from '../screens/onboarding/OnboardingStep1_Account';
import OnboardingStep2_Profile from '../screens/onboarding/OnboardingStep2_Profile';
import OnboardingStep3_ChatUpload from '../screens/onboarding/OnboardingStep3_ChatUpload';
import OnboardingStep4_Complete from '../screens/onboarding/OnboardingStep4_Complete';

const Stack = createStackNavigator();

const OnboardingNavigator = () => {
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
        name="OnboardingStep1"
        component={OnboardingStep1_Account}
        options={{ title: 'Create Account', headerLeft: null }}
      />
      <Stack.Screen
        name="OnboardingStep2"
        component={OnboardingStep2_Profile}
        options={{ title: 'Your Profile' }}
      />
      <Stack.Screen
        name="OnboardingStep3"
        component={OnboardingStep3_ChatUpload}
        options={{ title: 'Upload Chat Data' }}
      />
      <Stack.Screen
        name="OnboardingStep4"
        component={OnboardingStep4_Complete}
        options={{ title: 'Welcome!', headerLeft: null }}
      />
    </Stack.Navigator>
  );
};

export default OnboardingNavigator;

