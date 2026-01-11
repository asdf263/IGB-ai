import React, { useState, useContext } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { Button, Text, Snackbar, ProgressBar, Card, ActivityIndicator } from 'react-native-paper';
import * as DocumentPicker from 'expo-document-picker';
import { AuthContext } from '../../context/AuthContext';
import * as userApi from '../../services/userApi';

const OnboardingStep3_ChatUpload = ({ navigation, route }) => {
  const { user } = useContext(AuthContext);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [vectorId, setVectorId] = useState(null);

  const uid = route.params?.uid || user?.uid;

  const pickFile = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/json', 'text/plain'],
        copyToCacheDirectory: true,
      });

      if (!result.canceled && result.assets[0]) {
        const file = result.assets[0];
        
        // Validate file size (max 50MB)
        if (file.size > 50 * 1024 * 1024) {
          setErrorMessage('File size must be less than 50MB');
          setShowError(true);
          return;
        }

        // Validate file type
        const validExtensions = ['.json', '.txt'];
        const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
        
        if (!validExtensions.includes(fileExtension)) {
          setErrorMessage('Please select a JSON or TXT file');
          setShowError(true);
          return;
        }

        setSelectedFile(file);
        setErrorMessage('');
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

  const handleUploadAndVectorize = async () => {
    if (!selectedFile) {
      setErrorMessage('Please select a file first');
      setShowError(true);
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setErrorMessage('');

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const result = await userApi.uploadChatData(uid, selectedFile);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      setVectorId(result.vector_id);

      // Wait a moment to show completion
      setTimeout(() => {
        navigation.navigate('OnboardingStep4', {
          uid,
          vectorId: result.vector_id,
        });
      }, 500);
    } catch (error) {
      setErrorMessage(error.message || 'Failed to upload and vectorize chat data');
      setShowError(true);
      setUploadProgress(0);
    } finally {
      setIsUploading(false);
    }
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
            Step 3 of 4: Upload Chat Data
          </Text>
          <Text variant="bodyMedium" style={styles.subtitle}>
            Upload your chat logs to create your behavior vector
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
                  No file selected
                </Text>
              )}
            </Card.Content>
          </Card>

          <Button
            mode="outlined"
            onPress={pickFile}
            style={styles.pickButton}
            icon="file-upload"
            disabled={isUploading}
          >
            {selectedFile ? 'Change File' : 'Select File'}
          </Button>

          {isUploading && (
            <View style={styles.uploadContainer}>
              <ActivityIndicator size="small" style={styles.loader} />
              <Text variant="bodySmall" style={styles.uploadText}>
                Uploading and processing... {Math.round(uploadProgress)}%
              </Text>
              <ProgressBar progress={uploadProgress / 100} color="#6200ee" style={styles.uploadProgress} />
            </View>
          )}

          {vectorId && (
            <Card style={[styles.card, styles.successCard]}>
              <Card.Content>
                <Text variant="bodyMedium" style={styles.successText}>
                  ✓ Chat data processed and vectorized successfully!
                </Text>
              </Card.Content>
            </Card>
          )}

          <View style={styles.buttonRow}>
            <Button
              mode="outlined"
              onPress={() => navigation.goBack()}
              style={styles.backButton}
              disabled={isUploading}
            >
              Back
            </Button>
            <Button
              mode="contained"
              onPress={handleUploadAndVectorize}
              style={styles.nextButton}
              loading={isUploading}
              disabled={isUploading || !selectedFile || vectorId !== null}
            >
              {vectorId ? 'Continue' : 'Upload & Vectorize'}
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
    marginTop: 20,
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
  card: {
    marginBottom: 16,
  },
  successCard: {
    backgroundColor: '#e8f5e9',
    marginTop: 16,
  },
  fileName: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  fileSize: {
    color: '#666',
  },
  noFileText: {
    color: '#999',
    textAlign: 'center',
  },
  pickButton: {
    marginBottom: 16,
  },
  uploadContainer: {
    marginTop: 16,
    marginBottom: 16,
  },
  loader: {
    marginBottom: 8,
  },
  uploadText: {
    textAlign: 'center',
    marginBottom: 8,
    color: '#666',
  },
  uploadProgress: {
    height: 4,
    borderRadius: 2,
  },
  successText: {
    color: '#2e7d32',
    textAlign: 'center',
  },
  buttonRow: {
    flexDirection: 'row',
    marginTop: 8,
    gap: 12,
  },
  backButton: {
    flex: 1,
  },
  nextButton: {
    flex: 1,
  },
});

export default OnboardingStep3_ChatUpload;

