import React, { useState, useContext } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { TextInput, Button, Text, Snackbar, ProgressBar } from 'react-native-paper';
import { AuthContext } from '../../context/AuthContext';

const OnboardingStep1_Account = ({ navigation, route }) => {
  const { signup, isLoading, error, setError } = useContext(AuthContext);
  const [email, setEmail] = useState(route.params?.email || '');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showError, setShowError] = useState(false);
  const [validationError, setValidationError] = useState('');

  const validateForm = () => {
    if (!email.trim() || !password.trim() || !confirmPassword.trim()) {
      setValidationError('Please fill in all fields');
      return false;
    }

    if (password !== confirmPassword) {
      setValidationError('Passwords do not match');
      return false;
    }

    if (password.length < 6) {
      setValidationError('Password must be at least 6 characters');
      return false;
    }

    setValidationError('');
    return true;
  };

  const handleNext = async () => {
    if (!validateForm()) {
      setShowError(true);
      return;
    }

    // If user is already signed up, just proceed
    if (route.params?.uid) {
      navigation.navigate('OnboardingStep2', {
        uid: route.params.uid,
        email: email.trim(),
      });
      return;
    }

    // Otherwise, sign up first
    const result = await signup(email.trim(), password);
    
    if (result.success) {
      navigation.navigate('OnboardingStep2', {
        uid: result.user.uid,
        email: email.trim(),
      });
    } else {
      setShowError(true);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.content}>
          <ProgressBar progress={0.25} color="#6200ee" style={styles.progressBar} />
          
          <Text variant="headlineSmall" style={styles.title}>
            Step 1 of 4: Create Your Account
          </Text>
          <Text variant="bodyMedium" style={styles.subtitle}>
            Let's start by creating your account
          </Text>

          <TextInput
            label="Email or Username"
            value={email}
            onChangeText={setEmail}
            mode="outlined"
            style={styles.input}
            autoCapitalize="none"
            keyboardType="email-address"
            disabled={isLoading}
          />

          <TextInput
            label="Password"
            value={password}
            onChangeText={setPassword}
            mode="outlined"
            style={styles.input}
            secureTextEntry
            disabled={isLoading}
          />

          <TextInput
            label="Confirm Password"
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            mode="outlined"
            style={styles.input}
            secureTextEntry
            disabled={isLoading}
          />

          <Button
            mode="contained"
            onPress={handleNext}
            style={styles.button}
            loading={isLoading}
            disabled={isLoading}
          >
            Next
          </Button>
        </View>
      </ScrollView>

      <Snackbar
        visible={showError}
        onDismiss={() => setShowError(false)}
        duration={3000}
      >
        {validationError || error || 'Please check your input'}
      </Snackbar>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContent: {
    flexGrow: 1,
    padding: 20,
  },
  content: {
    width: '100%',
    maxWidth: 400,
    alignSelf: 'center',
    marginTop: 40,
  },
  progressBar: {
    marginBottom: 24,
    height: 4,
    borderRadius: 2,
  },
  title: {
    textAlign: 'center',
    marginBottom: 8,
    fontWeight: 'bold',
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 32,
    color: '#666',
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 8,
    paddingVertical: 4,
  },
});

export default OnboardingStep1_Account;

