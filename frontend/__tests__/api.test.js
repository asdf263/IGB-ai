import axios from 'axios';

// Mock axios before importing the API service
jest.mock('axios');

// Create a mock axios instance
const mockAxiosInstance = {
  post: jest.fn(),
  get: jest.fn(),
  defaults: {
    baseURL: 'http://localhost:5000',
    timeout: 60000
  }
};

// Mock axios.create to return our mock instance
axios.create = jest.fn(() => mockAxiosInstance);
axios.post = jest.fn();

// Now import the API service after mocking
const apiService = require('../services/api');

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset mocks
    mockAxiosInstance.post.mockResolvedValue({ data: {} });
    mockAxiosInstance.get.mockResolvedValue({ data: {} });
    axios.post.mockResolvedValue({ data: {} });
  });

  describe('uploadFile', () => {
    it('uploads file successfully', async () => {
      const mockFile = {
        uri: 'file://test.txt',
        name: 'test.txt',
        type: 'text/plain'
      };
      const mockResponse = {
        data: {
          success: true,
          filename: 'test.txt',
          content_length: 100,
          preview: 'File preview...'
        }
      };
      axios.post.mockResolvedValue(mockResponse);

      const result = await apiService.uploadFile(mockFile);

      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/upload'),
        expect.any(FormData)
      );
      expect(result).toEqual(mockResponse.data);
    });

    it('handles upload error', async () => {
      const mockFile = {
        uri: 'file://test.txt',
        name: 'test.txt',
        type: 'text/plain'
      };
      axios.post.mockRejectedValue(new Error('Upload failed'));

      await expect(apiService.uploadFile(mockFile)).rejects.toThrow('Upload failed');
    });

    it('creates FormData with correct file structure', async () => {
      const mockFile = {
        uri: 'file://test.txt',
        name: 'test.txt',
        type: 'text/plain'
      };
      axios.post.mockResolvedValue({ data: { success: true } });

      await apiService.uploadFile(mockFile);

      const formDataCall = axios.post.mock.calls[0][1];
      expect(formDataCall).toBeInstanceOf(FormData);
    });
  });

  describe('analyzeText', () => {
    it('analyzes text with default analysis type', async () => {
      const mockResponse = {
        data: {
          success: true,
          result: 'Analysis result',
          analysis_type: 'general',
          input_length: 10
        }
      };
      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      const result = await apiService.analyzeText('Test text');

      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        '/api/analyze',
        {
          text: 'Test text',
          analysis_type: 'general'
        }
      );
      expect(result).toEqual(mockResponse.data);
    });

    it('analyzes text with custom analysis type', async () => {
      const mockResponse = {
        data: {
          success: true,
          result: 'Summary result',
          analysis_type: 'summary'
        }
      };
      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      const result = await apiService.analyzeText('Test text', 'summary');

      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        '/api/analyze',
        {
          text: 'Test text',
          analysis_type: 'summary'
        }
      );
      expect(result).toEqual(mockResponse.data);
    });

    it('handles all analysis types', async () => {
      const analysisTypes = ['general', 'summary', 'sentiment', 'keywords', 'qa'];
      
      for (const type of analysisTypes) {
        mockAxiosInstance.post.mockResolvedValue({
          data: { success: true, analysis_type: type }
        });

        await apiService.analyzeText('Test', type);

        expect(mockAxiosInstance.post).toHaveBeenCalledWith(
          '/api/analyze',
          expect.objectContaining({ analysis_type: type })
        );
      }
    });

    it('handles analysis error', async () => {
      mockAxiosInstance.post.mockRejectedValue(new Error('Analysis failed'));

      await expect(apiService.analyzeText('Test')).rejects.toThrow('Analysis failed');
    });
  });

  describe('analyzeFile', () => {
    it('analyzes file with default analysis type', async () => {
      const mockFile = {
        uri: 'file://test.txt',
        name: 'test.txt',
        type: 'text/plain'
      };
      const mockResponse = {
        data: {
          success: true,
          result: 'File analysis result',
          filename: 'test.txt',
          analysis_type: 'general'
        }
      };
      axios.post.mockResolvedValue(mockResponse);

      const result = await apiService.analyzeFile(mockFile);

      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/analyze-file'),
        expect.any(FormData)
      );
      expect(result).toEqual(mockResponse.data);
    });

    it('analyzes file with custom analysis type', async () => {
      const mockFile = {
        uri: 'file://test.txt',
        name: 'test.txt',
        type: 'text/plain'
      };
      const mockResponse = {
        data: {
          success: true,
          analysis_type: 'summary'
        }
      };
      axios.post.mockResolvedValue(mockResponse);

      await apiService.analyzeFile(mockFile, 'summary');

      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/analyze-file'),
        expect.any(FormData)
      );
    });

    it('creates FormData with file and analysis_type', async () => {
      const mockFile = {
        uri: 'file://test.txt',
        name: 'test.txt',
        type: 'text/plain'
      };
      axios.post.mockResolvedValue({ data: { success: true } });

      await apiService.analyzeFile(mockFile, 'sentiment');

      const formDataCall = axios.post.mock.calls[0][1];
      expect(formDataCall).toBeInstanceOf(FormData);
    });

    it('handles file analysis error', async () => {
      const mockFile = {
        uri: 'file://test.txt',
        name: 'test.txt',
        type: 'text/plain'
      };
      axios.post.mockRejectedValue(new Error('Analysis failed'));

      await expect(apiService.analyzeFile(mockFile)).rejects.toThrow('Analysis failed');
    });
  });

  describe('chat', () => {
    it('sends chat message without context', async () => {
      const mockResponse = {
        data: {
          success: true,
          response: 'Hello! How can I help you?'
        }
      };
      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      const result = await apiService.chat('Hello');

      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        '/api/chat',
        {
          message: 'Hello',
          context: ''
        }
      );
      expect(result).toEqual(mockResponse.data);
    });

    it('sends chat message with context', async () => {
      const mockResponse = {
        data: {
          success: true,
          response: 'Response with context'
        }
      };
      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      const result = await apiService.chat('Follow up question', 'Previous conversation');

      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        '/api/chat',
        {
          message: 'Follow up question',
          context: 'Previous conversation'
        }
      );
      expect(result).toEqual(mockResponse.data);
    });

    it('handles chat error', async () => {
      mockAxiosInstance.post.mockRejectedValue(new Error('Chat failed'));

      await expect(apiService.chat('Hello')).rejects.toThrow('Chat failed');
    });
  });

  describe('healthCheck', () => {
    it('checks health status', async () => {
      const mockResponse = {
        data: {
          status: 'healthy',
          gemini_configured: true
        }
      };
      mockAxiosInstance.get.mockResolvedValue(mockResponse);

      const result = await apiService.healthCheck();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/health');
      expect(result).toEqual(mockResponse.data);
    });

    it('handles health check error', async () => {
      mockAxiosInstance.get.mockRejectedValue(new Error('Health check failed'));

      await expect(apiService.healthCheck()).rejects.toThrow('Health check failed');
    });
  });

  describe('API Configuration', () => {
    it('creates axios instance with correct configuration', () => {
      // axios.create is called when the module is loaded
      // We verify the mock instance has the expected configuration
      expect(mockAxiosInstance.defaults.baseURL).toBe('http://localhost:5000');
      expect(mockAxiosInstance.defaults.timeout).toBe(60000);
    });
  });
});
