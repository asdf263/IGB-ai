import React, { useState, useContext } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Card, Button, Text, ProgressBar, Chip, TextInput } from 'react-native-paper';
import DocumentPicker from 'react-native-document-picker';
import { AppContext } from '../context/AppContext';
import { extractFeatures } from '../services/vectorApi';

const UploadScreen = ({ navigation }) => {
  const { setCurrentVector, setFeatureLabels, addVector } = useContext(AppContext);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [jsonText, setJsonText] = useState('');
  const [inputMode, setInputMode] = useState('file');
  const [validationStatus, setValidationStatus] = useState(null);

  const handleFilePick = async () => {
    try {
      const result = await DocumentPicker.pick({
        type: [DocumentPicker.types.allFiles],
        copyTo: 'cachesDirectory',
      });

      const file = result[0];
      if (!file.name.endsWith('.json')) {
        Alert.alert('Invalid File', 'Please select a JSON file');
        return;
      }

      setSelectedFile(file);
      setValidationStatus('valid');
    } catch (err) {
      if (!DocumentPicker.isCancel(err)) {
        Alert.alert('Error', 'Failed to pick document');
      }
    }
  };

  const validateJson = (text) => {
    try {
      const parsed = JSON.parse(text);
      if (!parsed.messages || !Array.isArray(parsed.messages)) {
        setValidationStatus('invalid');
        return null;
      }
      setValidationStatus('valid');
      return parsed;
    } catch {
      setValidationStatus('invalid');
      return null;
    }
  };

  const handleJsonChange = (text) => {
    setJsonText(text);
    if (text.trim()) {
      validateJson(text);
    } else {
      setValidationStatus(null);
    }
  };

  const handleUpload = async () => {
    setUploading(true);
    setProgress(0);

    try {
      let messages;

      if (inputMode === 'file' && selectedFile) {
        const response = await fetch(selectedFile.fileCopyUri || selectedFile.uri);
        const text = await response.text();
        const parsed = JSON.parse(text);
        messages = parsed.messages;
      } else if (inputMode === 'text' && jsonText) {
        const parsed = validateJson(jsonText);
        if (!parsed) {
          Alert.alert('Invalid JSON', 'Please enter valid JSON with messages array');
          setUploading(false);
          return;
        }
        messages = parsed.messages;
      } else {
        Alert.alert('No Input', 'Please select a file or enter JSON');
        setUploading(false);
        return;
      }

      setProgress(0.3);

      const result = await extractFeatures(messages, true);

      setProgress(0.8);

      if (result.success) {
        setCurrentVector(result.vector);
        setFeatureLabels(result.feature_labels);
        addVector({
          id: result.vector_id,
          vector: result.vector,
          labels: result.feature_labels,
          categories: result.categories,
          timestamp: new Date().toISOString()
        });

        setProgress(1);

        Alert.alert(
          'Success',
          `Extracted ${result.feature_count} features`,
          [
            {
              text: 'View Analysis',
              onPress: () => navigation.navigate('Analysis', { 
                vector: result.vector,
                labels: result.feature_labels,
                categories: result.categories
              })
            },
            { text: 'OK' }
          ]
        );
      } else {
        Alert.alert('Error', result.error || 'Failed to extract features');
      }
    } catch (error) {
      Alert.alert('Error', error.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const sampleJson = `{
  "messages": [
    {"sender": "user", "text": "Hello!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Hi there!", "timestamp": 1715234012}
  ]
}`;

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Title title="Upload Chat Log" subtitle="Extract behavior vectors from conversations" />
        <Card.Content>
          <View style={styles.modeSelector}>
            <Chip
              selected={inputMode === 'file'}
              onPress={() => setInputMode('file')}
              style={styles.chip}
            >
              File Upload
            </Chip>
            <Chip
              selected={inputMode === 'text'}
              onPress={() => setInputMode('text')}
              style={styles.chip}
            >
              Paste JSON
            </Chip>
          </View>

          {inputMode === 'file' ? (
            <View style={styles.fileSection}>
              {selectedFile && (
                <View style={styles.fileInfo}>
                  <Text style={styles.fileName}>{selectedFile.name}</Text>
                  <Text style={styles.fileSize}>
                    {(selectedFile.size / 1024).toFixed(2)} KB
                  </Text>
                </View>
              )}
              <Button
                mode="outlined"
                onPress={handleFilePick}
                disabled={uploading}
                icon="file-upload"
                style={styles.button}
              >
                Select JSON File
              </Button>
            </View>
          ) : (
            <View style={styles.textSection}>
              <TextInput
                label="Paste JSON here"
                value={jsonText}
                onChangeText={handleJsonChange}
                multiline
                numberOfLines={8}
                mode="outlined"
                style={styles.jsonInput}
                placeholder={sampleJson}
              />
              {validationStatus && (
                <Chip
                  icon={validationStatus === 'valid' ? 'check' : 'close'}
                  style={[
                    styles.validationChip,
                    { backgroundColor: validationStatus === 'valid' ? '#4CAF50' : '#F44336' }
                  ]}
                >
                  {validationStatus === 'valid' ? 'Valid JSON' : 'Invalid JSON'}
                </Chip>
              )}
            </View>
          )}

          {uploading && (
            <View style={styles.progressSection}>
              <ProgressBar progress={progress} color="#6200ee" style={styles.progressBar} />
              <Text style={styles.progressText}>
                {progress < 0.3 ? 'Reading file...' :
                 progress < 0.8 ? 'Extracting features...' :
                 'Storing vector...'}
              </Text>
            </View>
          )}

          <Button
            mode="contained"
            onPress={handleUpload}
            disabled={uploading || (inputMode === 'file' && !selectedFile) || 
                     (inputMode === 'text' && validationStatus !== 'valid')}
            loading={uploading}
            style={styles.uploadButton}
            icon="cloud-upload"
          >
            Extract Features
          </Button>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Expected Format" />
        <Card.Content>
          <Text style={styles.formatText}>{sampleJson}</Text>
        </Card.Content>
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  card: {
    margin: 10,
    elevation: 4,
  },
  modeSelector: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  chip: {
    marginRight: 8,
  },
  fileSection: {
    marginBottom: 16,
  },
  fileInfo: {
    padding: 12,
    backgroundColor: '#e3f2fd',
    borderRadius: 8,
    marginBottom: 12,
  },
  fileName: {
    fontWeight: 'bold',
    fontSize: 16,
  },
  fileSize: {
    color: '#666',
    marginTop: 4,
  },
  textSection: {
    marginBottom: 16,
  },
  jsonInput: {
    minHeight: 150,
    fontFamily: 'monospace',
  },
  validationChip: {
    marginTop: 8,
    alignSelf: 'flex-start',
  },
  progressSection: {
    marginVertical: 16,
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
  },
  progressText: {
    textAlign: 'center',
    marginTop: 8,
    color: '#666',
  },
  button: {
    marginTop: 8,
  },
  uploadButton: {
    marginTop: 16,
  },
  formatText: {
    fontFamily: 'monospace',
    fontSize: 12,
    backgroundColor: '#f0f0f0',
    padding: 12,
    borderRadius: 8,
  },
});

export default UploadScreen;
