import React, { useState } from 'react';
import { StyleSheet, View, ScrollView, Alert } from 'react-native';
import { Provider as PaperProvider, Appbar, Card, Button, TextInput, Text, ActivityIndicator, Chip } from 'react-native-paper';
import DocumentPicker from 'react-native-document-picker';
import { StatusBar } from 'expo-status-bar';
import { analyzeText, analyzeFile, uploadFile, chat } from './services/api';

export default function App() {
  const [text, setText] = useState('');
  const [analysisResult, setAnalysisResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysisType, setAnalysisType] = useState('general');
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  const analysisTypes = [
    { label: 'General', value: 'general' },
    { label: 'Summary', value: 'summary' },
    { label: 'Sentiment', value: 'sentiment' },
    { label: 'Keywords', value: 'keywords' },
  ];

  const handleFilePick = async () => {
    try {
      const result = await DocumentPicker.pick({
        type: [DocumentPicker.types.text, DocumentPicker.types.pdf],
        copyTo: 'cachesDirectory',
      });
      
      setSelectedFile(result[0]);
      Alert.alert('File Selected', `Selected: ${result[0].name}`);
    } catch (err) {
      if (DocumentPicker.isCancel(err)) {
        // User cancelled
      } else {
        Alert.alert('Error', 'Failed to pick document');
      }
    }
  };

  const handleAnalyzeText = async () => {
    if (!text.trim()) {
      Alert.alert('Error', 'Please enter some text to analyze');
      return;
    }

    setLoading(true);
    try {
      const result = await analyzeText(text, analysisType);
      setAnalysisResult(result.result);
    } catch (error) {
      Alert.alert('Error', error.message || 'Failed to analyze text');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeFile = async () => {
    if (!selectedFile) {
      Alert.alert('Error', 'Please select a file first');
      return;
    }

    setLoading(true);
    try {
      const result = await analyzeFile(selectedFile, analysisType);
      setAnalysisResult(result.result);
      Alert.alert('Success', 'File analyzed successfully');
    } catch (error) {
      Alert.alert('Error', error.message || 'Failed to analyze file');
    } finally {
      setLoading(false);
    }
  };

  const handleChat = async () => {
    if (!chatMessage.trim()) {
      Alert.alert('Error', 'Please enter a message');
      return;
    }

    setLoading(true);
    try {
      const context = chatHistory.map(msg => `${msg.role}: ${msg.content}`).join('\n');
      const result = await chat(chatMessage, context);
      
      const newHistory = [
        ...chatHistory,
        { role: 'User', content: chatMessage },
        { role: 'Assistant', content: result.response }
      ];
      
      setChatHistory(newHistory);
      setChatMessage('');
    } catch (error) {
      Alert.alert('Error', error.message || 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  return (
    <PaperProvider>
      <StatusBar style="auto" />
      <Appbar.Header>
        <Appbar.Content title="IGB AI" subtitle="Text Analysis & Chat" />
      </Appbar.Header>
      
      <ScrollView style={styles.container}>
        {/* Analysis Type Selection */}
        <Card style={styles.card}>
          <Card.Title title="Analysis Type" />
          <Card.Content>
            <View style={styles.chipContainer}>
              {analysisTypes.map((type) => (
                <Chip
                  key={type.value}
                  selected={analysisType === type.value}
                  onPress={() => setAnalysisType(type.value)}
                  style={styles.chip}
                >
                  {type.label}
                </Chip>
              ))}
            </View>
          </Card.Content>
        </Card>

        {/* Text Analysis */}
        <Card style={styles.card}>
          <Card.Title title="Text Analysis" />
          <Card.Content>
            <TextInput
              label="Enter text to analyze"
              value={text}
              onChangeText={setText}
              multiline
              numberOfLines={6}
              mode="outlined"
              style={styles.input}
            />
            <Button
              mode="contained"
              onPress={handleAnalyzeText}
              disabled={loading}
              style={styles.button}
            >
              Analyze Text
            </Button>
          </Card.Content>
        </Card>

        {/* File Upload */}
        <Card style={styles.card}>
          <Card.Title title="File Analysis" />
          <Card.Content>
            {selectedFile && (
              <Text style={styles.fileInfo}>Selected: {selectedFile.name}</Text>
            )}
            <Button
              mode="outlined"
              onPress={handleFilePick}
              disabled={loading}
              style={styles.button}
            >
              Select File
            </Button>
            <Button
              mode="contained"
              onPress={handleAnalyzeFile}
              disabled={loading || !selectedFile}
              style={styles.button}
            >
              Analyze File
            </Button>
          </Card.Content>
        </Card>

        {/* Chat Interface */}
        <Card style={styles.card}>
          <Card.Title title="Chat with AI" />
          <Card.Content>
            <ScrollView style={styles.chatHistory} nestedScrollEnabled>
              {chatHistory.map((msg, index) => (
                <View key={index} style={styles.chatMessage}>
                  <Text style={styles.chatRole}>{msg.role}:</Text>
                  <Text style={styles.chatContent}>{msg.content}</Text>
                </View>
              ))}
            </ScrollView>
            <TextInput
              label="Type your message"
              value={chatMessage}
              onChangeText={setChatMessage}
              multiline
              mode="outlined"
              style={styles.input}
            />
            <Button
              mode="contained"
              onPress={handleChat}
              disabled={loading}
              style={styles.button}
            >
              Send
            </Button>
          </Card.Content>
        </Card>

        {/* Results */}
        {analysisResult && (
          <Card style={styles.card}>
            <Card.Title title="Analysis Result" />
            <Card.Content>
              <Text style={styles.resultText}>{analysisResult}</Text>
            </Card.Content>
          </Card>
        )}

        {loading && (
          <View style={styles.loading}>
            <ActivityIndicator size="large" />
          </View>
        )}
      </ScrollView>
    </PaperProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  card: {
    margin: 10,
    elevation: 4,
  },
  input: {
    marginBottom: 10,
  },
  button: {
    marginTop: 10,
  },
  chipContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  chip: {
    margin: 4,
  },
  fileInfo: {
    marginBottom: 10,
    padding: 10,
    backgroundColor: '#e3f2fd',
    borderRadius: 4,
  },
  chatHistory: {
    maxHeight: 200,
    marginBottom: 10,
    padding: 10,
    backgroundColor: '#fafafa',
    borderRadius: 4,
  },
  chatMessage: {
    marginBottom: 10,
  },
  chatRole: {
    fontWeight: 'bold',
    fontSize: 12,
    color: '#666',
  },
  chatContent: {
    marginTop: 4,
    fontSize: 14,
  },
  resultText: {
    fontSize: 14,
    lineHeight: 20,
  },
  loading: {
    padding: 20,
    alignItems: 'center',
  },
});

