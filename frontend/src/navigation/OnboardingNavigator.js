import React, { useContext } from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { TouchableOpacity } from 'react-native';
import { Text } from 'react-native-paper';
import { AuthContext } from '../context/AuthContext';
import OnboardingStep2_Profile from '../screens/onboarding/OnboardingStep2_Profile';
import OnboardingStep3_ChatUpload from '../screens/onboarding/OnboardingStep3_ChatUpload';
import OnboardingStep4_Complete from '../screens/onboarding/OnboardingStep4_Complete';

const Stack = createStackNavigator();

const OnboardingNavigator = () => {
  const { user, logout } = useContext(AuthContext);
  
  const LogoutButton = () => (
    <TouchableOpacity onPress={logout} style={{ marginLeft: 15 }}>
      <Text style={{ color: '#fff', fontSize: 14 }}>Logout</Text>
    </TouchableOpacity>
  );
  
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#E07A5F',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen
        name="OnboardingStep2"
        component={OnboardingStep2_Profile}
        options={{ 
          title: 'Your Profile', 
          headerLeft: () => <LogoutButton />
        }}
        initialParams={{ uid: user?.uid, email: user?.email }}
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

