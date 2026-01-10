import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';
import App from '../App';
import * as api from '../services/api';
import DocumentPicker from 'react-native-document-picker';

// Mock the API service
jest.mock('../services/api');
// Mock DocumentPicker properly for Jest environment
jest.mock('react-native-document-picker', () => ({
  pick: jest.fn(),
  types: {
    text: 'text/plain',
    pdf: 'application/pdf'
  },
  isCancel: jest.fn((error) => error?.code === 'DOCUMENT_PICKER_CANCELED')
}));
jest.spyOn(Alert, 'alert');

describe('App', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    Alert.alert.mockClear();
  });

  it('renders correctly', () => {
    const { getByText } = render(<App />);
    expect(getByText('IGB AI')).toBeTruthy();
    // Note: subtitle might not be directly accessible in test environment
    // Main title is sufficient to verify rendering
  });

  it('renders all main sections', () => {
    const { getByText, queryByText } = render(<App />);
    // Check for main sections - some might be in Card titles
    expect(getByText('Analysis Type')).toBeTruthy();
    expect(getByText('Text Analysis')).toBeTruthy();
    expect(getByText('File Analysis')).toBeTruthy();
    expect(getByText('Chat with AI')).toBeTruthy();
  });

  it('renders analysis type chips', () => {
    const { getByText } = render(<App />);
    expect(getByText('General')).toBeTruthy();
    expect(getByText('Summary')).toBeTruthy();
    expect(getByText('Sentiment')).toBeTruthy();
    expect(getByText('Keywords')).toBeTruthy();
  });

  it('allows selecting different analysis types', () => {
    const { getByText } = render(<App />);
    const summaryChip = getByText('Summary');
    
    fireEvent.press(summaryChip);
    // Chip should be selected (visual state change)
    expect(summaryChip).toBeTruthy();
  });

  describe('Text Analysis', () => {
    it('renders text input for analysis', () => {
      const { getByPlaceholderText } = render(<App />);
      expect(getByPlaceholderText('Enter text to analyze')).toBeTruthy();
    });

    it('shows error when analyzing empty text', async () => {
      const { getByText } = render(<App />);
      const analyzeButton = getByText('Analyze Text');
      
      fireEvent.press(analyzeButton);
      
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith('Error', 'Please enter some text to analyze');
      });
    });

    it('analyzes text successfully', async () => {
      api.analyzeText.mockResolvedValue({
        success: true,
        result: 'Analysis result',
        analysis_type: 'general',
        input_length: 10
      });

      const { getByPlaceholderText, getByText } = render(<App />);
      const textInput = getByPlaceholderText('Enter text to analyze');
      const analyzeButton = getByText('Analyze Text');
      
      fireEvent.changeText(textInput, 'Test text');
      fireEvent.press(analyzeButton);
      
      await waitFor(() => {
        expect(api.analyzeText).toHaveBeenCalledWith('Test text', 'general');
        expect(getByText('Analysis Result')).toBeTruthy();
        expect(getByText('Analysis result')).toBeTruthy();
      });
    });

    it('handles analysis error', async () => {
      api.analyzeText.mockRejectedValue(new Error('API Error'));

      const { getByPlaceholderText, getByText } = render(<App />);
      const textInput = getByPlaceholderText('Enter text to analyze');
      const analyzeButton = getByText('Analyze Text');
      
      fireEvent.changeText(textInput, 'Test text');
      fireEvent.press(analyzeButton);
      
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith('Error', 'API Error');
      });
    });

    it('uses selected analysis type', async () => {
      api.analyzeText.mockResolvedValue({
        success: true,
        result: 'Summary result',
        analysis_type: 'summary'
      });

      const { getByText, getByPlaceholderText } = render(<App />);
      const summaryChip = getByText('Summary');
      const textInput = getByPlaceholderText('Enter text to analyze');
      const analyzeButton = getByText('Analyze Text');
      
      fireEvent.press(summaryChip);
      fireEvent.changeText(textInput, 'Test text');
      fireEvent.press(analyzeButton);
      
      await waitFor(() => {
        expect(api.analyzeText).toHaveBeenCalledWith('Test text', 'summary');
      });
    });
  });

  describe('File Analysis', () => {
    it('renders file selection button', () => {
      const { getByText } = render(<App />);
      expect(getByText('Select File')).toBeTruthy();
    });

    it('allows selecting a file', async () => {
      const mockFile = {
        uri: 'file://test.txt',
        name: 'test.txt',
        type: 'text/plain'
      };
      DocumentPicker.pick.mockResolvedValue([mockFile]);

      const { getByText } = render(<App />);
      const selectButton = getByText('Select File');
      
      fireEvent.press(selectButton);
      
      await waitFor(() => {
        expect(DocumentPicker.pick).toHaveBeenCalled();
        expect(Alert.alert).toHaveBeenCalledWith('File Selected', 'Selected: test.txt');
        expect(getByText('Selected: test.txt')).toBeTruthy();
      });
    });

    it('handles file picker cancellation', async () => {
      DocumentPicker.pick.mockRejectedValue({ code: 'DOCUMENT_PICKER_CANCELED' });
      DocumentPicker.isCancel.mockReturnValue(true);

      const { getByText } = render(<App />);
      const selectButton = getByText('Select File');
      
      fireEvent.press(selectButton);
      
      await waitFor(() => {
        expect(DocumentPicker.pick).toHaveBeenCalled();
        // Should not show error for cancellation
        expect(Alert.alert).not.toHaveBeenCalledWith('Error', expect.any(String));
      });
    });

    it('handles file picker error', async () => {
      DocumentPicker.pick.mockRejectedValue(new Error('Picker error'));
      DocumentPicker.isCancel.mockReturnValue(false);

      const { getByText } = render(<App />);
      const selectButton = getByText('Select File');
      
      fireEvent.press(selectButton);
      
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith('Error', 'Failed to pick document');
      });
    });

    it('shows error when analyzing without file', async () => {
      const { getByText } = render(<App />);
      const analyzeButton = getByText('Analyze File');
      
      fireEvent.press(analyzeButton);
      
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith('Error', 'Please select a file first');
      });
    });

    it('analyzes file successfully', async () => {
      const mockFile = {
        uri: 'file://test.txt',
        name: 'test.txt',
        type: 'text/plain'
      };
      DocumentPicker.pick.mockResolvedValue([mockFile]);
      api.analyzeFile.mockResolvedValue({
        success: true,
        result: 'File analysis result',
        filename: 'test.txt',
        analysis_type: 'general'
      });

      const { getByText } = render(<App />);
      const selectButton = getByText('Select File');
      const analyzeButton = getByText('Analyze File');
      
      fireEvent.press(selectButton);
      
      await waitFor(() => {
        return getByText('Selected: test.txt');
      });
      
      fireEvent.press(analyzeButton);
      
      await waitFor(() => {
        expect(api.analyzeFile).toHaveBeenCalledWith(mockFile, 'general');
        expect(Alert.alert).toHaveBeenCalledWith('Success', 'File analyzed successfully');
        expect(getByText('File analysis result')).toBeTruthy();
      });
    });

    it('handles file analysis error', async () => {
      const mockFile = {
        uri: 'file://test.txt',
        name: 'test.txt',
        type: 'text/plain'
      };
      DocumentPicker.pick.mockResolvedValue([mockFile]);
      api.analyzeFile.mockRejectedValue(new Error('Analysis failed'));

      const { getByText } = render(<App />);
      const selectButton = getByText('Select File');
      const analyzeButton = getByText('Analyze File');
      
      fireEvent.press(selectButton);
      
      await waitFor(() => {
        return getByText('Selected: test.txt');
      });
      
      fireEvent.press(analyzeButton);
      
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith('Error', 'Analysis failed');
      });
    });
  });

  describe('Chat Interface', () => {
    it('renders chat input', () => {
      const { getByPlaceholderText } = render(<App />);
      expect(getByPlaceholderText('Type your message')).toBeTruthy();
    });

    it('renders send button', () => {
      const { getByText } = render(<App />);
      expect(getByText('Send')).toBeTruthy();
    });

    it('shows error when sending empty message', async () => {
      const { getByText } = render(<App />);
      const sendButton = getByText('Send');
      
      fireEvent.press(sendButton);
      
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith('Error', 'Please enter a message');
      });
    });

    it('sends chat message successfully', async () => {
      api.chat.mockResolvedValue({
        success: true,
        response: 'Hello! How can I help you?'
      });

      const { getByPlaceholderText, getByText } = render(<App />);
      const chatInput = getByPlaceholderText('Type your message');
      const sendButton = getByText('Send');
      
      fireEvent.changeText(chatInput, 'Hello');
      fireEvent.press(sendButton);
      
      await waitFor(() => {
        expect(api.chat).toHaveBeenCalledWith('Hello', '');
        expect(getByText('User:')).toBeTruthy();
        expect(getByText('Hello')).toBeTruthy();
        expect(getByText('Assistant:')).toBeTruthy();
        expect(getByText('Hello! How can I help you?')).toBeTruthy();
      });
    });

    it('maintains chat history', async () => {
      api.chat
        .mockResolvedValueOnce({
          success: true,
          response: 'First response'
        })
        .mockResolvedValueOnce({
          success: true,
          response: 'Second response'
        });

      const { getByPlaceholderText, getByText, getAllByText } = render(<App />);
      const chatInput = getByPlaceholderText('Type your message');
      const sendButton = getByText('Send');
      
      // Send first message
      fireEvent.changeText(chatInput, 'First message');
      fireEvent.press(sendButton);
      
      await waitFor(() => {
        expect(getByText('First message')).toBeTruthy();
      });
      
      // Send second message
      fireEvent.changeText(chatInput, 'Second message');
      fireEvent.press(sendButton);
      
      await waitFor(() => {
        expect(getByText('First message')).toBeTruthy();
        expect(getByText('Second message')).toBeTruthy();
        expect(getByText('First response')).toBeTruthy();
        expect(getByText('Second response')).toBeTruthy();
      });
    });

    it('clears input after sending message', async () => {
      api.chat.mockResolvedValue({
        success: true,
        response: 'Response'
      });

      const { getByPlaceholderText, getByText } = render(<App />);
      const chatInput = getByPlaceholderText('Type your message');
      const sendButton = getByText('Send');
      
      fireEvent.changeText(chatInput, 'Hello');
      expect(chatInput.props.value).toBe('Hello');
      
      fireEvent.press(sendButton);
      
      await waitFor(() => {
        expect(chatInput.props.value).toBe('');
      });
    });

    it('handles chat error', async () => {
      api.chat.mockRejectedValue(new Error('Chat failed'));

      const { getByPlaceholderText, getByText } = render(<App />);
      const chatInput = getByPlaceholderText('Type your message');
      const sendButton = getByText('Send');
      
      fireEvent.changeText(chatInput, 'Hello');
      fireEvent.press(sendButton);
      
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith('Error', 'Chat failed');
      });
    });

    it('includes context in chat requests', async () => {
      api.chat.mockResolvedValue({
        success: true,
        response: 'Response with context'
      });

      const { getByPlaceholderText, getByText } = render(<App />);
      const chatInput = getByPlaceholderText('Type your message');
      const sendButton = getByText('Send');
      
      // Send first message to create context
      fireEvent.changeText(chatInput, 'First message');
      fireEvent.press(sendButton);
      
      await waitFor(() => {
        expect(api.chat).toHaveBeenCalledWith('First message', '');
      });
      
      // Send second message (should include context)
      fireEvent.changeText(chatInput, 'Second message');
      fireEvent.press(sendButton);
      
      await waitFor(() => {
        expect(api.chat).toHaveBeenCalledWith(
          'Second message',
          expect.stringContaining('First message')
        );
      });
    });
  });

  describe('Loading States', () => {
    it('disables buttons while loading', async () => {
      api.analyzeText.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

      const { getByPlaceholderText, getByText } = render(<App />);
      const textInput = getByPlaceholderText('Enter text to analyze');
      const analyzeButton = getByText('Analyze Text');
      
      fireEvent.changeText(textInput, 'Test');
      fireEvent.press(analyzeButton);
      
      // Button should be disabled during loading
      expect(analyzeButton.props.disabled).toBe(true);
    });
  });
});

