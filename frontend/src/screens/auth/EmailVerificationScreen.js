import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Button, Card, IconButton, Snackbar } from 'react-native-paper';
import { resendConfirmationEmail } from '../../services/authApi';

const EmailVerificationScreen = ({ navigation, route }) => {
  const email = route?.params?.email || '';
  const [resendLoading, setResendLoading] = useState(false);
  const [resendSuccess, setResendSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [showError, setShowError] = useState(false);

  const handleResendEmail = async () => {
    if (!email) {
      setError('No email address provided');
      setShowError(true);
      return;
    }

    setResendLoading(true);
    setResendSuccess(false);
    setError(null);

    try {
      await resendConfirmationEmail(email);
      setResendSuccess(true);
    } catch (err) {
      console.log('[VERIFY] Resend failed:', err.message);
      setError(err.message);
      setShowError(true);
    } finally {
      setResendLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.content}>
          {/* Main Card */}
          <Card style={styles.card}>
            <Card.Content style={styles.cardContent}>
              {/* Email Icon */}
              <View style={styles.iconContainer}>
                <IconButton
                  icon="email-check-outline"
                  iconColor="#6200ee"
                  size={72}
                />
              </View>

              {/* Title */}
              <Text variant="headlineMedium" style={styles.title}>
                Verify Your Email
              </Text>

              {/* Description */}
              <Text variant="bodyLarge" style={styles.description}>
                We've sent a confirmation link to:
              </Text>

              {/* Email Address */}
              <View style={styles.emailContainer}>
                <Text variant="titleMedium" style={styles.emailText}>
                  {email || 'your email address'}
                </Text>
              </View>

              {/* Instructions */}
              <View style={styles.instructionsContainer}>
                <View style={styles.instructionRow}>
                  <IconButton icon="numeric-1-circle" iconColor="#6200ee" size={24} />
                  <Text style={styles.instructionText}>
                    Open your email inbox
                  </Text>
                </View>
                <View style={styles.instructionRow}>
                  <IconButton icon="numeric-2-circle" iconColor="#6200ee" size={24} />
                  <Text style={styles.instructionText}>
                    Find the email from IGB AI
                  </Text>
                </View>
                <View style={styles.instructionRow}>
                  <IconButton icon="numeric-3-circle" iconColor="#6200ee" size={24} />
                  <Text style={styles.instructionText}>
                    Click the confirmation link
                  </Text>
                </View>
              </View>

              {/* Success Message */}
              {resendSuccess && (
                <View style={styles.successMessage}>
                  <IconButton icon="check-circle" iconColor="#4CAF50" size={20} />
                  <Text style={styles.successText}>
                    Email sent! Check your inbox.
                  </Text>
                </View>
              )}
            </Card.Content>
          </Card>

          {/* Resend Button */}
          <Button
            mode="outlined"
            onPress={handleResendEmail}
            style={styles.resendButton}
            loading={resendLoading}
            disabled={resendLoading}
            icon="email-sync"
          >
            {resendSuccess ? 'Email Sent!' : 'Resend Confirmation Email'}
          </Button>

          {/* Hint Text */}
          <Text variant="bodySmall" style={styles.hintText}>
            Didn't receive the email? Check your spam folder.
          </Text>

          {/* Divider */}
          <View style={styles.divider} />

          {/* Login Button */}
          <Text variant="bodyMedium" style={styles.readyText}>
            Already verified your email?
          </Text>
          <Button
            mode="contained"
            onPress={() => navigation.navigate('Login')}
            style={styles.loginButton}
            icon="login"
          >
            Go to Login
          </Button>

          {/* Change Email */}
          <Button
            mode="text"
            onPress={() => navigation.navigate('Signup')}
            style={styles.changeEmailButton}
          >
            Use a different email
          </Button>
        </View>
      </ScrollView>

      <Snackbar
        visible={showError}
        onDismiss={() => setShowError(false)}
        duration={4000}
        action={{
          label: 'Dismiss',
          onPress: () => setShowError(false),
        }}
      >
        {error || 'Something went wrong'}
      </Snackbar>
    </View>
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
  card: {
    marginBottom: 20,
    elevation: 4,
    borderRadius: 12,
  },
  cardContent: {
    alignItems: 'center',
    paddingVertical: 32,
    paddingHorizontal: 24,
  },
  iconContainer: {
    backgroundColor: '#EDE7F6',
    borderRadius: 50,
    marginBottom: 16,
  },
  title: {
    textAlign: 'center',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  description: {
    textAlign: 'center',
    color: '#666',
    marginBottom: 8,
  },
  emailContainer: {
    backgroundColor: '#E8EAF6',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    marginBottom: 24,
  },
  emailText: {
    textAlign: 'center',
    fontWeight: 'bold',
    color: '#3F51B5',
  },
  instructionsContainer: {
    alignSelf: 'stretch',
    marginTop: 8,
  },
  instructionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  instructionText: {
    flex: 1,
    fontSize: 14,
    color: '#555',
  },
  successMessage: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E8F5E9',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginTop: 16,
  },
  successText: {
    color: '#2E7D32',
    fontWeight: '500',
  },
  resendButton: {
    marginBottom: 8,
  },
  hintText: {
    textAlign: 'center',
    color: '#888',
    marginBottom: 24,
  },
  divider: {
    height: 1,
    backgroundColor: '#ddd',
    marginVertical: 16,
  },
  readyText: {
    textAlign: 'center',
    color: '#666',
    marginBottom: 12,
  },
  loginButton: {
    marginBottom: 8,
  },
  changeEmailButton: {
    marginTop: 8,
  },
});

export default EmailVerificationScreen;

