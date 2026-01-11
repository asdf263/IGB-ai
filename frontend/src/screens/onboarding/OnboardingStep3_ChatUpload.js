import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { Button, Text, Snackbar, ProgressBar, Card } from 'react-native-paper';
import * as DocumentPicker from 'expo-document-picker';

const OnboardingStep3_ChatUpload = ({ navigation, route }) => {
  const accountData = route.params?.accountData || {};
  const profileData = route.params?.profileData || {};
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  console.log('[ONBOARD-3] Rendering Step 3 - Chat Upload');
  console.log('[ONBOARD-3] Data received:', { email: accountData.email, name: profileData.name });

  const pickFile = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/json', 'text/plain'],
        copyToCacheDirectory: true,
      });

      if (!result.canceled && result.assets[0]) {
        const file = result.assets[0];
        if (file.size > 50 * 1024 * 1024) {
          setErrorMessage('File size must be less than 50MB');
          setShowError(true);
          return;
        }
        console.log('[ONBOARD-3] File selected:', file.name);
        setSelectedFile(file);
      }
    } catch (error) {
      setErrorMessage('Failed to pick file');
      setShowError(true);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const handleNext = () => {
    console.log('[ONBOARD-3] Proceeding to Step 4 (account creation)');
    navigation.navigate('OnboardingStep4', {
      accountData,
      profileData,
      chatFile: selectedFile,
    });
  };

  const handleBack = () => {
    navigation.goBack();
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.content}>
          <ProgressBar progress={0.75} color="#6200ee" style={styles.progressBar} />
          
          <Text variant="headlineSmall" style={styles.title}>
            Step 3 of 4: Chat Data
          </Text>
          <Text variant="bodyMedium" style={styles.subtitle}>
            Upload your chat logs to create your behavior vector (required)
          </Text>

          <Card style={styles.card}>
            <Card.Content>
              {selectedFile ? (
                <View>
                  <Text variant="titleMedium" style={styles.fileName}>
                    {selectedFile.name}
                  </Text>
                  <Text variant="bodySmall" style={styles.fileSize}>
                    {formatFileSize(selectedFile.size)}
                  </Text>
                </View>
              ) : (
                <Text variant="bodyMedium" style={styles.noFileText}>
                  No file selected - please upload a chat file to continue
                </Text>
              )}
            </Card.Content>
          </Card>

          <Button
            mode="outlined"
            onPress={pickFile}
            style={styles.pickButton}
            icon="file-upload"
          >
            {selectedFile ? 'Change File' : 'Select File'}
          </Button>

          <View style={styles.buttonRow}>
            <Button mode="outlined" onPress={handleBack} style={styles.backButton}>
              Back
            </Button>
            <Button 
              mode="contained" 
              onPress={handleNext} 
              style={styles.nextButton}
              disabled={!selectedFile}
            >
              Next
            </Button>
          </View>
        </View>
      </ScrollView>

      <Snackbar
        visible={showError}
        onDismiss={() => setShowError(false)}
        duration={3000}
      >
        {errorMessage}
      </Snackbar>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  scrollContent: { flexGrow: 1, padding: 20 },
  content: { width: '100%', maxWidth: 400, alignSelf: 'center', marginTop: 20 },
  progressBar: { marginBottom: 24, height: 4, borderRadius: 2 },
  title: { textAlign: 'center', marginBottom: 8, fontWeight: 'bold' },
  subtitle: { textAlign: 'center', marginBottom: 32, color: '#666' },
  card: { marginBottom: 16 },
  fileName: { fontWeight: 'bold', marginBottom: 4 },
  fileSize: { color: '#666' },
  noFileText: { color: '#999', textAlign: 'center' },
  pickButton: { marginBottom: 16 },
  buttonRow: { flexDirection: 'row', marginTop: 8, gap: 12 },
  backButton: { flex: 1 },
  nextButton: { flex: 1 },
});

export default OnboardingStep3_ChatUpload;
