import React, { useState, useContext } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { TextInput, Button, Text, Snackbar } from 'react-native-paper';
import { AuthContext } from '../../context/AuthContext';

const LoginScreen = ({ navigation }) => {
  const { login, isLoading, error, setError } = useContext(AuthContext);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showError, setShowError] = useState(false);

  const handleLogin = async () => {
    // #region agent log
    console.log('[LOGIN] handleLogin called', {email: email.trim(), hasPassword: !!password.trim()});
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'LoginScreen.js:12',message:'handleLogin entry',data:{email:email.trim(),has_password:!!password.trim()},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch((e)=>console.log('[LOG] Fetch error:',e)));
    // #endregion
    if (!email.trim() || !password.trim()) {
      // #region agent log
      console.log('[LOGIN] Validation failed - missing email or password');
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'LoginScreen.js:14',message:'validation failed',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
      // #endregion
      setShowError(true);
      return;
    }

    // #region agent log
    console.log('[LOGIN] Validation passed, calling login function', {email: email.trim()});
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'LoginScreen.js:18',message:'before login call',data:{email:email.trim()},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
    // #endregion
    const result = await login(email.trim(), password);
    // #region agent log
    console.log('[LOGIN] login result received', {success: result?.success, error: result?.error, hasUser: !!result?.user, uid: result?.user?.uid});
    fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'LoginScreen.js:20',message:'after login call',data:{result_success:result?.success,result_error:result?.error,has_user:!!result?.user},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
    // #endregion
    
    if (result.success) {
      // #region agent log
      console.log('[LOGIN] Success! User logged in', {uid: result?.user?.uid});
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'LoginScreen.js:22',message:'login success',data:{uid:result?.user?.uid},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
      // #endregion
      // Navigation will be handled by the navigator based on auth state
    } else {
      // #region agent log
      console.log('[LOGIN] Failed', {error: result?.error});
      fetch('http://127.0.0.1:7242/ingest/c7d0c08b-891b-46e2-8e1f-d3fa2db26cbd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'LoginScreen.js:25',message:'login failed',data:{error:result?.error},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch((e)=>console.log('[LOG] Fetch error:',e));
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
            Welcome Back
          </Text>
          <Text variant="bodyMedium" style={styles.subtitle}>
            Sign in to continue
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
            onPress={() => navigation.navigate('Signup')}
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
        duration={3000}
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
  linkButton: {
    marginTop: 16,
  },
});

export default LoginScreen;

