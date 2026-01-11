import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import LoginScreen from '../screens/auth/LoginScreen';
import SignupScreen from '../screens/auth/SignupScreen';
import EmailVerificationScreen from '../screens/auth/EmailVerificationScreen';
import OnboardingStep1_Account from '../screens/onboarding/OnboardingStep1_Account';
import OnboardingStep2_Profile from '../screens/onboarding/OnboardingStep2_Profile';
import OnboardingStep3_ChatUpload from '../screens/onboarding/OnboardingStep3_ChatUpload';
import OnboardingStep4_Complete from '../screens/onboarding/OnboardingStep4_Complete';

const Stack = createStackNavigator();

const AuthNavigator = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: '#E07A5F' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
      }}
    >
      <Stack.Screen
        name="Login"
        component={LoginScreen}
        options={{ title: 'Login' }}
      />
      <Stack.Screen
        name="Signup"
        component={SignupScreen}
        options={{ title: 'Sign Up' }}
      />
      <Stack.Screen
        name="EmailVerification"
        component={EmailVerificationScreen}
        options={{ 
          title: 'Verify Email',
          headerLeft: null, // Prevent going back
        }}
      />
      <Stack.Screen
        name="OnboardingStep1"
        component={OnboardingStep1_Account}
        options={{ title: 'Sign Up' }}
      />
      <Stack.Screen
        name="OnboardingStep2"
        component={OnboardingStep2_Profile}
        options={{ title: 'Your Profile' }}
      />
      <Stack.Screen
        name="OnboardingStep3"
        component={OnboardingStep3_ChatUpload}
        options={{ title: 'Upload Data' }}
      />
      <Stack.Screen
        name="OnboardingStep4"
        component={OnboardingStep4_Complete}
        options={{ title: 'Complete', headerLeft: null }}
      />
    </Stack.Navigator>
  );
};

export default AuthNavigator;
