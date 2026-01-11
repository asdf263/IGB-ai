/**
 * Tests for AuthContext with Supabase integration
 */
import React from 'react';
import { render, waitFor, act } from '@testing-library/react-native';
import { Text, View } from 'react-native';

// Create mock functions
const mockSignup = jest.fn();
const mockLogin = jest.fn();
const mockLogout = jest.fn();
const mockGetSession = jest.fn();
const mockGetUser = jest.fn();
const mockUnsubscribe = jest.fn();
const mockOnAuthStateChange = jest.fn(() => ({ unsubscribe: mockUnsubscribe }));

// Mock the entire authApi module
jest.mock('../src/services/authApi', () => ({
  __esModule: true,
  signup: (...args) => mockSignup(...args),
  login: (...args) => mockLogin(...args),
  logout: (...args) => mockLogout(...args),
  getSession: (...args) => mockGetSession(...args),
  getUser: (...args) => mockGetUser(...args),
  onAuthStateChange: (...args) => mockOnAuthStateChange(...args),
  default: {},
}));

// Import after mocking
import { AuthContext, AuthProvider } from '../src/context/AuthContext';

// Test component to consume context
const TestConsumer = () => {
  const context = React.useContext(AuthContext);
  return (
    <View>
      <Text testID="isAuthenticated">{String(context.isAuthenticated)}</Text>
      <Text testID="isLoading">{String(context.isLoading)}</Text>
      <Text testID="userEmail">{context.user?.email || 'none'}</Text>
      <Text testID="error">{context.error || 'none'}</Text>
    </View>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockGetSession.mockResolvedValue(null);
    mockOnAuthStateChange.mockReturnValue({ unsubscribe: mockUnsubscribe });
  });

  describe('Initial State', () => {
    it('should start with loading state', () => {
      const { getByTestId } = render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      expect(getByTestId('isLoading').children[0]).toBe('true');
    });

    it('should initialize as not authenticated when no session', async () => {
      mockGetSession.mockResolvedValue(null);

      const { getByTestId } = render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(getByTestId('isLoading').children[0]).toBe('false');
        expect(getByTestId('isAuthenticated').children[0]).toBe('false');
      });
    });

    it('should restore session from Supabase', async () => {
      const mockSession = {
        user: {
          id: 'existing-user-123',
          email: 'existing@example.com',
          user_metadata: { name: 'Existing User' },
          email_confirmed_at: '2024-01-01',
          created_at: '2024-01-01',
        },
      };
      mockGetSession.mockResolvedValue(mockSession);

      const { getByTestId } = render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(getByTestId('isAuthenticated').children[0]).toBe('true');
        expect(getByTestId('userEmail').children[0]).toBe('existing@example.com');
      });
    });
  });

  describe('Signup', () => {
    it('should handle successful signup', async () => {
      mockGetSession.mockResolvedValue(null);
      mockSignup.mockResolvedValue({
        uid: 'new-user-123',
        email: 'new@example.com',
        session: { access_token: 'token' },
      });

      let contextValue;
      const { getByTestId } = render(
        <AuthProvider>
          <AuthContext.Consumer>
            {(value) => {
              contextValue = value;
              return <TestConsumer />;
            }}
          </AuthContext.Consumer>
        </AuthProvider>
      );

      await waitFor(() => {
        expect(getByTestId('isLoading').children[0]).toBe('false');
      });

      await act(async () => {
        const result = await contextValue.signup('new@example.com', 'password123', { name: 'New User' });
        expect(result.success).toBe(true);
      });

      await waitFor(() => {
        expect(getByTestId('isAuthenticated').children[0]).toBe('true');
        expect(getByTestId('userEmail').children[0]).toBe('new@example.com');
      });
    });

    it('should handle signup error', async () => {
      mockGetSession.mockResolvedValue(null);
      mockSignup.mockRejectedValue(new Error('Email already exists'));

      let contextValue;
      const { getByTestId } = render(
        <AuthProvider>
          <AuthContext.Consumer>
            {(value) => {
              contextValue = value;
              return <TestConsumer />;
            }}
          </AuthContext.Consumer>
        </AuthProvider>
      );

      await waitFor(() => {
        expect(getByTestId('isLoading').children[0]).toBe('false');
      });

      await act(async () => {
        const result = await contextValue.signup('existing@example.com', 'password123');
        expect(result.success).toBe(false);
        expect(result.error).toBe('Email already exists');
      });

      expect(getByTestId('error').children[0]).toBe('Email already exists');
    });
  });

  describe('Login', () => {
    it('should handle successful login', async () => {
      mockGetSession.mockResolvedValue(null);
      mockLogin.mockResolvedValue({
        uid: 'login-user-123',
        email: 'login@example.com',
        session: { access_token: 'token' },
        user_profile: { profile: { location: 'CA' } },
      });

      let contextValue;
      const { getByTestId } = render(
        <AuthProvider>
          <AuthContext.Consumer>
            {(value) => {
              contextValue = value;
              return <TestConsumer />;
            }}
          </AuthContext.Consumer>
        </AuthProvider>
      );

      await waitFor(() => {
        expect(getByTestId('isLoading').children[0]).toBe('false');
      });

      await act(async () => {
        const result = await contextValue.login('login@example.com', 'password123');
        expect(result.success).toBe(true);
      });

      await waitFor(() => {
        expect(getByTestId('isAuthenticated').children[0]).toBe('true');
        expect(getByTestId('userEmail').children[0]).toBe('login@example.com');
      });
    });

    it('should handle login error', async () => {
      mockGetSession.mockResolvedValue(null);
      mockLogin.mockRejectedValue(new Error('Invalid credentials'));

      let contextValue;
      const { getByTestId } = render(
        <AuthProvider>
          <AuthContext.Consumer>
            {(value) => {
              contextValue = value;
              return <TestConsumer />;
            }}
          </AuthContext.Consumer>
        </AuthProvider>
      );

      await waitFor(() => {
        expect(getByTestId('isLoading').children[0]).toBe('false');
      });

      await act(async () => {
        const result = await contextValue.login('wrong@example.com', 'wrongpass');
        expect(result.success).toBe(false);
        expect(result.error).toBe('Invalid credentials');
      });
    });
  });

  describe('Logout', () => {
    it('should handle logout', async () => {
      const mockSession = {
        user: {
          id: 'user-123',
          email: 'user@example.com',
          user_metadata: {},
        },
      };
      mockGetSession.mockResolvedValue(mockSession);
      mockLogout.mockResolvedValue();

      let contextValue;
      const { getByTestId } = render(
        <AuthProvider>
          <AuthContext.Consumer>
            {(value) => {
              contextValue = value;
              return <TestConsumer />;
            }}
          </AuthContext.Consumer>
        </AuthProvider>
      );

      await waitFor(() => {
        expect(getByTestId('isAuthenticated').children[0]).toBe('true');
      });

      await act(async () => {
        await contextValue.logout();
      });

      await waitFor(() => {
        expect(getByTestId('isAuthenticated').children[0]).toBe('false');
        expect(getByTestId('userEmail').children[0]).toBe('none');
      });
    });

    it('should clear state even if logout API fails', async () => {
      const mockSession = {
        user: {
          id: 'user-123',
          email: 'user@example.com',
          user_metadata: {},
        },
      };
      mockGetSession.mockResolvedValue(mockSession);
      mockLogout.mockRejectedValue(new Error('Network error'));

      let contextValue;
      const { getByTestId } = render(
        <AuthProvider>
          <AuthContext.Consumer>
            {(value) => {
              contextValue = value;
              return <TestConsumer />;
            }}
          </AuthContext.Consumer>
        </AuthProvider>
      );

      await waitFor(() => {
        expect(getByTestId('isAuthenticated').children[0]).toBe('true');
      });

      await act(async () => {
        await contextValue.logout();
      });

      // Should still clear local state
      await waitFor(() => {
        expect(getByTestId('isAuthenticated').children[0]).toBe('false');
      });
    });
  });

  describe('Auth State Change Subscription', () => {
    it('should subscribe to auth changes on mount', async () => {
      mockGetSession.mockResolvedValue(null);

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(mockOnAuthStateChange).toHaveBeenCalled();
      });
    });

    it('should unsubscribe on unmount', async () => {
      mockGetSession.mockResolvedValue(null);

      const { unmount } = render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(mockOnAuthStateChange).toHaveBeenCalled();
      });

      unmount();

      expect(mockUnsubscribe).toHaveBeenCalled();
    });
  });

  describe('Context Value', () => {
    it('should provide all required values', async () => {
      mockGetSession.mockResolvedValue(null);

      let contextValue;
      render(
        <AuthProvider>
          <AuthContext.Consumer>
            {(value) => {
              contextValue = value;
              return <TestConsumer />;
            }}
          </AuthContext.Consumer>
        </AuthProvider>
      );

      await waitFor(() => {
        expect(contextValue).toHaveProperty('user');
        expect(contextValue).toHaveProperty('session');
        expect(contextValue).toHaveProperty('isAuthenticated');
        expect(contextValue).toHaveProperty('isLoading');
        expect(contextValue).toHaveProperty('error');
        expect(contextValue).toHaveProperty('signup');
        expect(contextValue).toHaveProperty('login');
        expect(contextValue).toHaveProperty('logout');
        expect(contextValue).toHaveProperty('setError');
        expect(contextValue).toHaveProperty('updateUserProfile');
      });
    });
  });
});
