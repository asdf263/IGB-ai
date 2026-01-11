import React, { useState, useContext, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Button, Text, ProgressBar, Card, Avatar, ActivityIndicator } from 'react-native-paper';
import { AuthContext } from '../../context/AuthContext';
import { uploadChatData } from '../../services/userApi';
import { formatLocationDisplay, formatHeightDisplay } from '../../constants/profileOptions';

const OnboardingStep4_Complete = ({ navigation, route }) => {
  const { signup } = useContext(AuthContext);
  
  const accountData = route.params?.accountData || {};
  const profileData = route.params?.profileData || {};
  const chatFile = route.params?.chatFile || null;
  
  const [currentStep, setCurrentStep] = useState('creating'); // creating, uploading, complete
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState(null);
  const [userId, setUserId] = useState(null);

  console.log('[ONBOARD-4] Rendering Step 4 - Complete');
  console.log('[ONBOARD-4] Account:', accountData.email);
  console.log('[ONBOARD-4] Profile:', profileData);
  console.log('[ONBOARD-4] Chat file:', chatFile?.name || 'none');

  const createAccountAndUpload = async () => {
    console.log('[ONBOARD-4] Creating account...');
    setCurrentStep('creating');
    setError(null);

    try {
      // Step 1: Create account
      const result = await signup(accountData.email, accountData.password, profileData);
      
      console.log('[ONBOARD-4] Signup result:', result);
      
      if (!result.success) {
        console.log('[ONBOARD-4] Signup failed:', result.error);
        setError(result.error || 'Failed to create account');
        return;
      }

      const uid = result.user?.uid;
      setUserId(uid);
      console.log('[ONBOARD-4] Account created successfully! UID:', uid);

      // Step 2: Upload chat file if provided
      if (chatFile && uid) {
        setCurrentStep('uploading');
        console.log('[ONBOARD-4] Uploading chat file...');
        
        try {
          const uploadResult = await uploadChatData(uid, chatFile);
          console.log('[ONBOARD-4] Chat upload result:', uploadResult);
          
          if (uploadResult.success || uploadResult.vector_id) {
            console.log('[ONBOARD-4] Chat file uploaded successfully!');
          } else {
            console.warn('[ONBOARD-4] Chat upload returned without success flag');
          }
        } catch (uploadError) {
          console.warn('[ONBOARD-4] Chat upload error (non-fatal):', uploadError.message);
          // Don't fail the whole process if chat upload fails
          // The user can re-upload later
        }
      }

      // Step 3: Complete!
      setCurrentStep('complete');
      setIsComplete(true);
      
      // Navigate to email verification screen after short delay
      setTimeout(() => {
        navigation.replace('EmailVerification', { 
          email: accountData.email,
          fromOnboarding: true,
        });
      }, 2000);
      
    } catch (err) {
      console.log('[ONBOARD-4] Error:', err.message);
      setError(err.message || 'Failed to create account');
    }
  };

  // Auto-create account when screen loads
  useEffect(() => {
    if (!isComplete && currentStep === 'creating' && !error) {
      createAccountAndUpload();
    }
  }, []);

  const handleRetry = () => {
    setError(null);
    setCurrentStep('creating');
    createAccountAndUpload();
  };

  // Loading states
  if (currentStep === 'creating' && !error) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#6200ee" />
        <Text variant="titleMedium" style={styles.loadingText}>
          Creating your account...
        </Text>
        <Text variant="bodySmall" style={styles.subText}>
          Setting up your profile
        </Text>
      </View>
    );
  }

  if (currentStep === 'uploading' && !error) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#6200ee" />
        <Text variant="titleMedium" style={styles.loadingText}>
          Processing your chat data...
        </Text>
        <Text variant="bodySmall" style={styles.subText}>
          Creating your behavior vector
        </Text>
        <View style={styles.fileInfo}>
          <Text variant="bodySmall" style={styles.fileName}>
            {chatFile?.name}
          </Text>
        </View>
      </View>
    );
  }

  // Error state
  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Avatar.Icon size={80} icon="alert-circle" style={styles.errorIcon} />
        <Text variant="titleMedium" style={styles.errorTitle}>
          Account Creation Failed
        </Text>
        <Text variant="bodyMedium" style={styles.errorText}>
          {error}
        </Text>
        <Button mode="contained" onPress={handleRetry} style={styles.retryButton}>
          Try Again
        </Button>
        <Button mode="text" onPress={() => navigation.navigate('OnboardingStep1')}>
          Start Over
        </Button>
      </View>
    );
  }

  // Success state - briefly shown before navigating to email verification
  return (
    <ScrollView contentContainerStyle={styles.scrollContent}>
      <View style={styles.content}>
        <ProgressBar progress={1.0} color="#4caf50" style={styles.progressBar} />
        
        <View style={styles.iconContainer}>
          <Avatar.Icon size={80} icon="check-circle" style={styles.successIcon} />
        </View>

        <Text variant="headlineSmall" style={styles.title}>
          Account Created!
        </Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          Just one more step - verify your email
        </Text>

        <Card style={styles.summaryCard}>
          <Card.Content>
            <Text variant="titleMedium" style={styles.cardTitle}>
              Account Summary
            </Text>
            
            <View style={styles.row}>
              <Text variant="bodySmall" style={styles.label}>Email:</Text>
              <Text variant="bodyMedium">{accountData.email}</Text>
            </View>

            {profileData.name && (
              <View style={styles.row}>
                <Text variant="bodySmall" style={styles.label}>Name:</Text>
                <Text variant="bodyMedium">{profileData.name}</Text>
              </View>
            )}

            {profileData.instagram_handle && (
              <View style={styles.row}>
                <Text variant="bodySmall" style={styles.label}>Instagram:</Text>
                <Text variant="bodyMedium">@{profileData.instagram_handle}</Text>
              </View>
            )}

            {(profileData.city || profileData.state) && (
              <View style={styles.row}>
                <Text variant="bodySmall" style={styles.label}>Location:</Text>
                <Text variant="bodyMedium">{formatLocationDisplay(profileData.city, profileData.state)}</Text>
              </View>
            )}

            {profileData.ethnicity && (
              <View style={styles.row}>
                <Text variant="bodySmall" style={styles.label}>Ethnicity:</Text>
                <Text variant="bodyMedium">{profileData.ethnicity}</Text>
              </View>
            )}

            {profileData.height && (
              <View style={styles.row}>
                <Text variant="bodySmall" style={styles.label}>Height:</Text>
                <Text variant="bodyMedium">{formatHeightDisplay(profileData.height)}</Text>
              </View>
            )}

            {chatFile && (
              <View style={styles.row}>
                <Text variant="bodySmall" style={styles.label}>Chat Data:</Text>
                <View style={styles.chatFileStatus}>
                  <Avatar.Icon size={20} icon="check" style={styles.checkIcon} />
                  <Text variant="bodyMedium" style={styles.uploadedText}>Uploaded</Text>
                </View>
              </View>
            )}
          </Card.Content>
        </Card>

        <View style={styles.redirectContainer}>
          <ActivityIndicator size="small" color="#6200ee" />
          <Text variant="bodySmall" style={styles.redirectText}>
            Redirecting to email verification...
          </Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  scrollContent: { flexGrow: 1, padding: 20, backgroundColor: '#f5f5f5' },
  content: { width: '100%', maxWidth: 400, alignSelf: 'center', marginTop: 40 },
  progressBar: { marginBottom: 24, height: 4, borderRadius: 2 },
  iconContainer: { alignItems: 'center', marginBottom: 24 },
  successIcon: { backgroundColor: '#4caf50' },
  errorIcon: { backgroundColor: '#f44336' },
  checkIcon: { backgroundColor: '#4caf50' },
  title: { textAlign: 'center', marginBottom: 8, fontWeight: 'bold' },
  subtitle: { textAlign: 'center', marginBottom: 32, color: '#666' },
  loadingText: { marginTop: 16, color: '#333', fontWeight: '600' },
  subText: { marginTop: 8, color: '#666' },
  fileInfo: { 
    marginTop: 16, 
    padding: 12, 
    backgroundColor: '#e8e8e8', 
    borderRadius: 8,
  },
  fileName: { color: '#666' },
  errorTitle: { marginTop: 16, color: '#f44336', fontWeight: 'bold' },
  errorText: { marginTop: 8, color: '#666', textAlign: 'center' },
  retryButton: { marginTop: 24 },
  summaryCard: { marginBottom: 24, backgroundColor: '#e8f5e9' },
  cardTitle: { fontWeight: 'bold', marginBottom: 16 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  label: { color: '#666', fontWeight: '500' },
  chatFileStatus: { flexDirection: 'row', alignItems: 'center' },
  uploadedText: { marginLeft: 4, color: '#4caf50', fontWeight: '500' },
  redirectContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
  },
  redirectText: {
    marginLeft: 12,
    color: '#666',
  },
});

export default OnboardingStep4_Complete;
