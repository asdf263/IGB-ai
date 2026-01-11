import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { Button, Text, Snackbar, ProgressBar, Card, Chip } from 'react-native-paper';
import * as DocumentPicker from 'expo-document-picker';

const OnboardingStep3_ChatUpload = ({ navigation, route }) => {
  const accountData = route.params?.accountData || {};
  const profileData = route.params?.profileData || {};
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  console.log('[ONBOARD-3] Rendering Step 3 - Chat Upload');
  console.log('[ONBOARD-3] Data received:', { email: accountData.email, name: profileData.name });

  // Determine file type from name or MIME type
  const getFileType = (file) => {
    if (!file) return null;
    const name = file.name?.toLowerCase() || '';
    const mimeType = file.mimeType?.toLowerCase() || '';
    
    if (name.endsWith('.zip') || mimeType.includes('zip')) {
      return 'instagram';
    }
    return 'json';
  };

  const pickFile = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: [
          'application/json',
          'text/plain',
          'application/zip',
          'application/x-zip-compressed',
          'application/octet-stream', // Some devices report ZIP as this
        ],
        copyToCacheDirectory: true,
      });

      if (!result.canceled && result.assets[0]) {
        const file = result.assets[0];
        const fileType = getFileType(file);
        
        // Different size limits based on file type
        const maxSize = fileType === 'instagram' ? 150 * 1024 * 1024 : 50 * 1024 * 1024;
        const maxSizeLabel = fileType === 'instagram' ? '150MB' : '50MB';
        
        if (file.size > maxSize) {
          setErrorMessage(`File size must be less than ${maxSizeLabel}`);
          setShowError(true);
          return;
        }
        
        console.log('[ONBOARD-3] File selected:', file.name, 'Type:', fileType);
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

  const fileType = getFileType(selectedFile);

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.content}>
          <ProgressBar progress={0.75} color="#E07A5F" style={styles.progressBar} />
          
          <Text variant="headlineSmall" style={styles.title}>
            Step 3 of 4: Chat Data
          </Text>
          <Text variant="bodyMedium" style={styles.subtitle}>
            Upload your Instagram data export (ZIP) or chat logs (JSON)
          </Text>

          <Card style={styles.card}>
            <Card.Content>
              {selectedFile ? (
                <View>
                  <View style={styles.fileHeader}>
                    <Text variant="titleMedium" style={styles.fileName}>
                      {selectedFile.name}
                    </Text>
                    <Chip 
                      mode="outlined" 
                      compact
                      style={fileType === 'instagram' ? styles.instagramChip : styles.jsonChip}
                    >
                      {fileType === 'instagram' ? 'Instagram Export' : 'JSON'}
                    </Chip>
                  </View>
                  <Text variant="bodySmall" style={styles.fileSize}>
                    {formatFileSize(selectedFile.size)}
                  </Text>
                </View>
              ) : (
                <View>
                  <Text variant="bodyMedium" style={styles.noFileText}>
                    No file selected
                  </Text>
                  <Text variant="bodySmall" style={styles.helpText}>
                    Supported formats: Instagram data export (.zip) or JSON chat files
                  </Text>
                </View>
              )}
            </Card.Content>
          </Card>

          <Button
            mode="outlined"
            onPress={pickFile}
            style={styles.pickButton}
            icon={fileType === 'instagram' ? 'instagram' : 'file-upload'}
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
  fileHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  fileName: { fontWeight: 'bold', flex: 1, marginRight: 8 },
  fileSize: { color: '#666' },
  noFileText: { color: '#999', textAlign: 'center', marginBottom: 8 },
  helpText: { color: '#999', textAlign: 'center', fontSize: 12 },
  pickButton: { marginBottom: 16 },
  buttonRow: { flexDirection: 'row', marginTop: 8, gap: 12 },
  backButton: { flex: 1 },
  nextButton: { flex: 1 },
  instagramChip: { backgroundColor: '#fce4ec' },
  jsonChip: { backgroundColor: '#e3f2fd' },
});

export default OnboardingStep3_ChatUpload;
