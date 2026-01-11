import React, { useState, useContext } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { TextInput, Button, Text, Snackbar, Card, IconButton } from 'react-native-paper';
import { AuthContext } from '../../context/AuthContext';
import { resendConfirmationEmail } from '../../services/authApi';

const LoginScreen = ({ navigation }) => {
  const { login, isLoading, error, setError } = useContext(AuthContext);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showError, setShowError] = useState(false);
  const [showEmailNotConfirmed, setShowEmailNotConfirmed] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [resendSuccess, setResendSuccess] = useState(false);

  console.log('[LOGIN] Rendering LoginScreen');

  const handleLogin = async () => {
    console.log('[LOGIN] Login button pressed');
    if (!email.trim() || !password.trim()) {
      console.log('[LOGIN] Validation failed - empty fields');
      setShowError(true);
      return;
    }

    console.log('[LOGIN] Calling login API for:', email.trim());
    const result = await login(email.trim(), password);
    
    if (!result.success) {
      console.log('[LOGIN] Login failed:', result.error);
      
      // Check if error is about email not confirmed
      const errorLower = (result.error || '').toLowerCase();
      if (errorLower.includes('email not confirmed') || 
          errorLower.includes('confirm your email') ||
          errorLower.includes('email confirmation')) {
        setShowEmailNotConfirmed(true);
      } else {
        setShowError(true);
      }
    } else {
      console.log('[LOGIN] Login successful!');
    }
  };

  const handleResendConfirmation = async () => {
    setResendLoading(true);
    setResendSuccess(false);
    
    try {
      await resendConfirmationEmail(email.trim());
      setResendSuccess(true);
    } catch (err) {
      console.log('[LOGIN] Resend failed:', err.message);
      setError(err.message);
      setShowError(true);
    } finally {
      setResendLoading(false);
    }
  };

  const handleBackToLogin = () => {
    setShowEmailNotConfirmed(false);
    setResendSuccess(false);
    setError(null);
  };

  // Email not confirmed screen
  if (showEmailNotConfirmed) {
    return (
      <View style={styles.container}>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.content}>
            <Card style={styles.confirmationCard}>
              <Card.Content style={styles.confirmationContent}>
                <IconButton
                  icon="email-alert"
                  iconColor="#FF9800"
                  size={64}
                  style={styles.emailIcon}
                />
                <Text variant="headlineSmall" style={styles.confirmationTitle}>
                  Email Not Verified
                </Text>
                <Text variant="bodyMedium" style={styles.confirmationText}>
                  Please check your inbox and click the confirmation link we sent to:
                </Text>
                <Text variant="bodyLarge" style={styles.emailText}>
                  {email}
                </Text>
                
                {resendSuccess ? (
                  <View style={styles.successMessage}>
                    <IconButton icon="check-circle" iconColor="#4CAF50" size={24} />
                    <Text style={styles.successText}>
                      Confirmation email sent! Check your inbox.
                    </Text>
                  </View>
                ) : (
                  <Text variant="bodyMedium" style={styles.confirmationSubtext}>
                    Didn't receive the email? Check your spam folder or request a new one.
                  </Text>
                )}
              </Card.Content>
            </Card>

            <Button
              mode="contained"
              onPress={handleResendConfirmation}
              style={styles.button}
              loading={resendLoading}
              disabled={resendLoading || resendSuccess}
              icon="email-sync"
            >
              {resendSuccess ? 'Email Sent!' : 'Resend Confirmation Email'}
            </Button>

            <Button
              mode="outlined"
              onPress={handleBackToLogin}
              style={styles.outlineButton}
              icon="arrow-left"
            >
              Back to Login
            </Button>
          </View>
        </ScrollView>

        <Snackbar
          visible={showError}
          onDismiss={() => setShowError(false)}
          duration={4000}
        >
          {error || 'Failed to resend confirmation email'}
        </Snackbar>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.content}>
          <Text variant="headlineMedium" style={styles.title}>
            Welcome Back
          </Text>
          <Text variant="bodyMedium" style={styles.subtitle}>
            Sign in with your email
          </Text>

          <TextInput
            label="Email"
            value={email}
            onChangeText={setEmail}
            mode="outlined"
            style={styles.input}
            autoCapitalize="none"
            keyboardType="email-address"
            disabled={isLoading}
            left={<TextInput.Icon icon="email" />}
          />

          <TextInput
            label="Password"
            value={password}
            onChangeText={setPassword}
            mode="outlined"
            style={styles.input}
            secureTextEntry
            disabled={isLoading}
            left={<TextInput.Icon icon="lock" />}
          />

          <Button
            mode="contained"
            onPress={handleLogin}
            style={styles.button}
            loading={isLoading}
            disabled={isLoading}
          >
            Login
          </Button>

          <Button
            mode="text"
            onPress={() => navigation.navigate('OnboardingStep1')}
            style={styles.linkButton}
            disabled={isLoading}
          >
            Don't have an account? Sign up
          </Button>
        </View>
      </ScrollView>

      <Snackbar
        visible={showError}
        onDismiss={() => setShowError(false)}
        duration={4000}
      >
        {error || 'Please fill in all fields'}
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
    justifyContent: 'center',
    padding: 20,
  },
  content: {
    width: '100%',
    maxWidth: 400,
    alignSelf: 'center',
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
  outlineButton: {
    marginTop: 12,
    paddingVertical: 4,
  },
  linkButton: {
    marginTop: 16,
  },
  // Email not confirmed screen styles
  confirmationCard: {
    marginBottom: 24,
    elevation: 4,
  },
  confirmationContent: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  emailIcon: {
    marginBottom: 8,
  },
  confirmationTitle: {
    textAlign: 'center',
    marginBottom: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  confirmationText: {
    textAlign: 'center',
    color: '#666',
    marginBottom: 8,
  },
  emailText: {
    textAlign: 'center',
    fontWeight: 'bold',
    color: '#6200ee',
    marginBottom: 16,
  },
  confirmationSubtext: {
    textAlign: 'center',
    color: '#666',
    paddingHorizontal: 16,
  },
  successMessage: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#E8F5E9',
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
  },
  successText: {
    color: '#2E7D32',
    marginLeft: 4,
  },
});

export default LoginScreen;
