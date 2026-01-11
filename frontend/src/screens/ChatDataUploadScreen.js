import React, { useState, useContext } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Button, Text, Card, Chip, ActivityIndicator, Snackbar } from 'react-native-paper';
import * as DocumentPicker from 'expo-document-picker';
import { AuthContext } from '../context/AuthContext';
import { uploadChatData, getUser } from '../services/userApi';

/**
 * ChatDataUploadScreen - Allows users to upload/re-upload their chat data
 * after account creation. Useful for:
 * - Users who skipped upload during onboarding
 * - Users who want to update their data
 * - Retrying failed uploads
 */
const ChatDataUploadScreen = ({ navigation }) => {
  const { user } = useContext(AuthContext);
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [existingVector, setExistingVector] = useState(null);
  const [checkingVector, setCheckingVector] = useState(true);
  const [snackbar, setSnackbar] = useState({ visible: false, message: '' });

  // Check if user already has a vector on mount
  React.useEffect(() => {
    checkExistingVector();
  }, []);

  const checkExistingVector = async () => {
    if (!user?.uid) return;
    
    try {
      const userData = await getUser(user.uid);
      if (userData?.vector_id) {
        setExistingVector(userData.vector_id);
      }
    } catch (err) {
      console.log('[UPLOAD] Could not check existing vector:', err.message);
    } finally {
      setCheckingVector(false);
    }
  };

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
          'application/octet-stream',
        ],
        copyToCacheDirectory: true,
      });

      if (!result.canceled && result.assets[0]) {
        const file = result.assets[0];
        const fileType = getFileType(file);
        
        // Size limits
        const maxSize = fileType === 'instagram' ? 150 * 1024 * 1024 : 50 * 1024 * 1024;
        const maxSizeLabel = fileType === 'instagram' ? '150MB' : '50MB';
        
        if (file.size > maxSize) {
          setSnackbar({ visible: true, message: `File size must be less than ${maxSizeLabel}` });
          return;
        }
        
        console.log('[UPLOAD] File selected:', file.name, 'Type:', fileType);
        setSelectedFile(file);
        setUploadResult(null); // Clear previous result
      }
    } catch (error) {
      setSnackbar({ visible: true, message: 'Failed to pick file' });
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const handleUpload = async () => {
    if (!selectedFile || !user?.uid) {
      setSnackbar({ visible: true, message: 'No file selected or user not logged in' });
      return;
    }

    // Confirm if replacing existing data
    if (existingVector) {
      Alert.alert(
        'Replace Existing Data?',
        'You already have chat data uploaded. Uploading new data will replace your existing behavior analysis.',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Replace', style: 'destructive', onPress: performUpload },
        ]
      );
    } else {
      performUpload();
    }
  };

  const performUpload = async () => {
    setUploading(true);
    setUploadResult(null);

    try {
      console.log('[UPLOAD] Starting upload for user:', user.uid);
      const result = await uploadChatData(user.uid, selectedFile);
      
      console.log('[UPLOAD] Upload result:', result);
      
      setUploadResult({
        success: true,
        vectorId: result.vector_id,
        messageCount: result.message_count,
        featureCount: result.feature_count,
      });
      
      setExistingVector(result.vector_id);
      setSnackbar({ visible: true, message: 'Chat data uploaded successfully!' });
      
    } catch (error) {
      console.error('[UPLOAD] Upload error:', error);
      setUploadResult({
        success: false,
        error: error.message || 'Upload failed',
      });
      setSnackbar({ visible: true, message: error.message || 'Upload failed' });
    } finally {
      setUploading(false);
    }
  };

  const fileType = getFileType(selectedFile);

  if (checkingVector) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#E07A5F" />
        <Text style={styles.loadingText}>Checking your data...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Header */}
        <Text variant="headlineSmall" style={styles.title}>
          Upload Chat Data
        </Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          Upload your Instagram data export to analyze your communication style
        </Text>

        {/* Current Status */}
        {existingVector && (
          <Card style={styles.statusCard}>
            <Card.Content>
              <View style={styles.statusRow}>
                <Text style={styles.statusIcon}>✅</Text>
                <View style={styles.statusTextContainer}>
                  <Text variant="titleMedium" style={styles.statusTitle}>
                    Data Already Uploaded
                  </Text>
                  <Text variant="bodySmall" style={styles.statusSubtext}>
                    Vector ID: {existingVector.slice(0, 20)}...
                  </Text>
                </View>
              </View>
            </Card.Content>
          </Card>
        )}

        {/* File Selection */}
        <Card style={styles.card}>
          <Card.Title title="Select File" />
          <Card.Content>
            {selectedFile ? (
              <View>
                <View style={styles.fileHeader}>
                  <Text variant="titleMedium" style={styles.fileName} numberOfLines={1}>
                    {selectedFile.name}
                  </Text>
                  <Chip 
                    mode="outlined" 
                    compact
                    style={fileType === 'instagram' ? styles.instagramChip : styles.jsonChip}
                  >
                    {fileType === 'instagram' ? 'Instagram' : 'JSON'}
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
                  Supported: Instagram data export (.zip) or JSON chat files
                </Text>
              </View>
            )}
          </Card.Content>
        </Card>

        {/* File Picker Button */}
        <Button
          mode="outlined"
          onPress={pickFile}
          style={styles.pickButton}
          icon={fileType === 'instagram' ? 'instagram' : 'file-upload'}
          disabled={uploading}
        >
          {selectedFile ? 'Change File' : 'Select File'}
        </Button>

        {/* Upload Button */}
        <Button
          mode="contained"
          onPress={handleUpload}
          style={styles.uploadButton}
          disabled={!selectedFile || uploading}
          loading={uploading}
          icon="cloud-upload"
        >
          {uploading ? 'Uploading...' : (existingVector ? 'Replace Data' : 'Upload & Analyze')}
        </Button>

        {/* Upload Progress / Result */}
        {uploading && (
          <Card style={styles.progressCard}>
            <Card.Content>
              <ActivityIndicator size="small" color="#E07A5F" />
              <Text style={styles.progressText}>
                Processing your chat data... This may take a minute.
              </Text>
            </Card.Content>
          </Card>
        )}

        {uploadResult && (
          <Card style={[styles.resultCard, uploadResult.success ? styles.successCard : styles.errorCard]}>
            <Card.Content>
              {uploadResult.success ? (
                <View>
                  <Text variant="titleMedium" style={styles.successTitle}>
                    ✅ Upload Successful!
                  </Text>
                  <Text variant="bodySmall" style={styles.resultDetail}>
                    Messages processed: {uploadResult.messageCount}
                  </Text>
                  <Text variant="bodySmall" style={styles.resultDetail}>
                    Features extracted: {uploadResult.featureCount}
                  </Text>
                </View>
              ) : (
                <View>
                  <Text variant="titleMedium" style={styles.errorTitle}>
                    ❌ Upload Failed
                  </Text>
                  <Text variant="bodySmall" style={styles.resultDetail}>
                    {uploadResult.error}
                  </Text>
                </View>
              )}
            </Card.Content>
          </Card>
        )}

        {/* Instructions */}
        <Card style={styles.instructionsCard}>
          <Card.Title title="How to get your Instagram data" />
          <Card.Content>
            <Text variant="bodySmall" style={styles.instruction}>
              1. Open Instagram → Settings → Account Center
            </Text>
            <Text variant="bodySmall" style={styles.instruction}>
              2. Go to "Your information and permissions"
            </Text>
            <Text variant="bodySmall" style={styles.instruction}>
              3. Select "Download your information"
            </Text>
            <Text variant="bodySmall" style={styles.instruction}>
              4. Choose "Messages" and download as ZIP
            </Text>
            <Text variant="bodySmall" style={styles.instruction}>
              5. Upload the ZIP file here
            </Text>
          </Card.Content>
        </Card>
      </View>

      <Snackbar
        visible={snackbar.visible}
        onDismiss={() => setSnackbar({ visible: false, message: '' })}
        duration={3000}
      >
        {snackbar.message}
      </Snackbar>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 12,
    color: '#666',
  },
  content: {
    padding: 16,
  },
  title: {
    textAlign: 'center',
    marginBottom: 8,
    fontWeight: 'bold',
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 24,
    color: '#666',
  },
  statusCard: {
    marginBottom: 16,
    backgroundColor: '#e8f5e9',
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  statusTextContainer: {
    flex: 1,
  },
  statusTitle: {
    fontWeight: 'bold',
    color: '#2e7d32',
  },
  statusSubtext: {
    color: '#666',
    marginTop: 2,
  },
  card: {
    marginBottom: 16,
  },
  fileHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  fileName: {
    fontWeight: 'bold',
    flex: 1,
    marginRight: 8,
  },
  fileSize: {
    color: '#666',
  },
  noFileText: {
    color: '#999',
    textAlign: 'center',
    marginBottom: 8,
  },
  helpText: {
    color: '#999',
    textAlign: 'center',
    fontSize: 12,
  },
  instagramChip: {
    backgroundColor: '#fce4ec',
  },
  jsonChip: {
    backgroundColor: '#e3f2fd',
  },
  pickButton: {
    marginBottom: 12,
  },
  uploadButton: {
    marginBottom: 16,
    backgroundColor: '#E07A5F',
  },
  progressCard: {
    marginBottom: 16,
    backgroundColor: '#fff3e0',
  },
  progressText: {
    textAlign: 'center',
    marginTop: 8,
    color: '#e65100',
  },
  resultCard: {
    marginBottom: 16,
  },
  successCard: {
    backgroundColor: '#e8f5e9',
  },
  errorCard: {
    backgroundColor: '#ffebee',
  },
  successTitle: {
    color: '#2e7d32',
    marginBottom: 8,
  },
  errorTitle: {
    color: '#c62828',
    marginBottom: 8,
  },
  resultDetail: {
    color: '#666',
    marginTop: 2,
  },
  instructionsCard: {
    marginTop: 8,
    backgroundColor: '#f5f5f5',
  },
  instruction: {
    color: '#666',
    marginBottom: 6,
    paddingLeft: 8,
  },
});

export default ChatDataUploadScreen;

