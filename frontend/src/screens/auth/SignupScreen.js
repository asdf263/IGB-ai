import React, { useState, useContext } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { TextInput, Button, Text, Snackbar } from 'react-native-paper';
import { AuthContext } from '../../context/AuthContext';

const SignupScreen = ({ navigation }) => {
  const { signup, isLoading, error, setError } = useContext(AuthContext);
  const [email, setEmail] = useState('');
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

  const handleSignup = async () => {
    // #region agent log
    console.log('[SIGNUP] handleSignup called', {email: email.trim(), passwordLength: password.length});
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'SignupScreen.js:34',message:'handleSignup entry',data:{email:email.trim(),password_length:password.length,has_confirm:!!confirmPassword},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
    // #endregion
    if (!validateForm()) {
      // #region agent log
      console.log('[SIGNUP] Validation failed', {validationError});
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'SignupScreen.js:36',message:'validation failed',data:{validationError},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
      // #endregion
      setShowError(true);
      return;
    }

    // #region agent log
    console.log('[SIGNUP] Validation passed, calling signup function', {email: email.trim()});
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'SignupScreen.js:40',message:'before signup call',data:{email:email.trim(),password_length:password.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
    // #endregion
    const result = await signup(email.trim(), password);
    // #region agent log
    console.log('[SIGNUP] signup result received', {success: result?.success, error: result?.error, hasUser: !!result?.user, uid: result?.user?.uid});
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'SignupScreen.js:42',message:'after signup call',data:{result_success:result?.success,result_error:result?.error,has_user:!!result?.user},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
    // #endregion
    
    if (result.success) {
      // #region agent log
      console.log('[SIGNUP] Success! User created', {uid: result?.user?.uid});
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'SignupScreen.js:44',message:'signup success',data:{uid:result?.user?.uid},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
      // #endregion
      // Navigation will be handled by the navigator
    } else {
      // #region agent log
      console.log('[SIGNUP] Failed', {error: result?.error});
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'SignupScreen.js:47',message:'signup failed',data:{error:result?.error},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
      // #endregion
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
          <Text variant="headlineMedium" style={styles.title}>
            Create Account
          </Text>
          <Text variant="bodyMedium" style={styles.subtitle}>
            Sign up to get started
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
            onPress={handleSignup}
            style={styles.button}
            loading={isLoading}
            disabled={isLoading}
          >
            Sign Up
          </Button>

          <Button
            mode="text"
            onPress={() => navigation.navigate('Login')}
            style={styles.linkButton}
            disabled={isLoading}
          >
            Already have an account? Login
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
  linkButton: {
    marginTop: 16,
  },
});

export default SignupScreen;

