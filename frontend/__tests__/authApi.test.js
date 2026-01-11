/**
 * Tests for Supabase Authentication API
 */

// Mock Supabase before importing
const mockSupabaseAuth = {
  signUp: jest.fn(),
  signInWithPassword: jest.fn(),
  signOut: jest.fn(),
  getSession: jest.fn(),
  getUser: jest.fn(),
  onAuthStateChange: jest.fn(() => ({
    data: { subscription: { unsubscribe: jest.fn() } }
  })),
};

const mockSupabase = {
  auth: mockSupabaseAuth,
};

jest.mock('../src/services/supabase', () => ({
  supabase: mockSupabase,
}));

// Mock axios for backend API calls
jest.mock('axios');
const axios = require('axios');
const mockAxiosInstance = {
  post: jest.fn(),
  get: jest.fn(),
};
axios.create = jest.fn(() => mockAxiosInstance);

// Import after mocking
const authApi = require('../src/services/authApi');

describe('Auth API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockAxiosInstance.post.mockResolvedValue({ data: {} });
    mockAxiosInstance.get.mockResolvedValue({ data: {} });
  });

  describe('signup', () => {
    const mockUser = {
      id: 'test-user-id-123',
      email: 'test@example.com',
      user_metadata: { name: 'Test User' },
    };

    const mockSession = {
      access_token: 'test-access-token',
      refresh_token: 'test-refresh-token',
    };

    it('should sign up a new user successfully', async () => {
      mockSupabaseAuth.signUp.mockResolvedValue({
        data: { user: mockUser, session: mockSession },
        error: null,
      });

      const result = await authApi.signup('test@example.com', 'password123', { name: 'Test User' });

      expect(mockSupabaseAuth.signUp).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
        options: {
          data: { name: 'Test User' },
        },
      });
      expect(result.uid).toBe('test-user-id-123');
      expect(result.email).toBe('test@example.com');
      expect(result.session).toBe(mockSession);
    });

    it('should handle signup error from Supabase', async () => {
      mockSupabaseAuth.signUp.mockResolvedValue({
        data: { user: null, session: null },
        error: { message: 'Email already registered' },
      });

      await expect(authApi.signup('test@example.com', 'password123')).rejects.toThrow('Email already registered');
    });

    it('should signup with empty profile', async () => {
      mockSupabaseAuth.signUp.mockResolvedValue({
        data: { user: mockUser, session: mockSession },
        error: null,
      });

      await authApi.signup('test@example.com', 'password123');

      expect(mockSupabaseAuth.signUp).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
        options: {
          data: {},
        },
      });
    });

    it('should attempt to sync profile to backend after signup', async () => {
      mockSupabaseAuth.signUp.mockResolvedValue({
        data: { user: mockUser, session: mockSession },
        error: null,
      });

      await authApi.signup('test@example.com', 'password123', { location: 'California' });

      // Should attempt to sync with backend (may fail gracefully)
      expect(mockAxiosInstance.post).toHaveBeenCalled();
    });
  });

  describe('login', () => {
    const mockUser = {
      id: 'test-user-id-456',
      email: 'login@example.com',
    };

    const mockSession = {
      access_token: 'login-access-token',
      refresh_token: 'login-refresh-token',
    };

    it('should log in user successfully', async () => {
      mockSupabaseAuth.signInWithPassword.mockResolvedValue({
        data: { user: mockUser, session: mockSession },
        error: null,
      });

      const result = await authApi.login('login@example.com', 'password123');

      expect(mockSupabaseAuth.signInWithPassword).toHaveBeenCalledWith({
        email: 'login@example.com',
        password: 'password123',
      });
      expect(result.uid).toBe('test-user-id-456');
      expect(result.email).toBe('login@example.com');
      expect(result.session).toBe(mockSession);
    });

    it('should handle invalid credentials', async () => {
      mockSupabaseAuth.signInWithPassword.mockResolvedValue({
        data: { user: null, session: null },
        error: { message: 'Invalid login credentials' },
      });

      await expect(authApi.login('wrong@example.com', 'wrongpass')).rejects.toThrow('Invalid login credentials');
    });

    it('should fetch profile from backend after login', async () => {
      mockSupabaseAuth.signInWithPassword.mockResolvedValue({
        data: { user: mockUser, session: mockSession },
        error: null,
      });
      mockAxiosInstance.get.mockResolvedValue({
        data: { profile: { location: 'New York' } },
      });

      const result = await authApi.login('login@example.com', 'password123');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/users/test-user-id-456');
      expect(result.user_profile.profile).toEqual({ location: 'New York' });
    });
  });

  describe('logout', () => {
    it('should log out user successfully', async () => {
      mockSupabaseAuth.signOut.mockResolvedValue({ error: null });

      await authApi.logout();

      expect(mockSupabaseAuth.signOut).toHaveBeenCalled();
    });

    it('should handle logout error', async () => {
      mockSupabaseAuth.signOut.mockResolvedValue({
        error: { message: 'Logout failed' },
      });

      await expect(authApi.logout()).rejects.toThrow('Logout failed');
    });
  });

  describe('getSession', () => {
    it('should return current session', async () => {
      const mockSession = {
        access_token: 'current-token',
        user: { id: 'user-123' },
      };
      mockSupabaseAuth.getSession.mockResolvedValue({
        data: { session: mockSession },
        error: null,
      });

      const session = await authApi.getSession();

      expect(mockSupabaseAuth.getSession).toHaveBeenCalled();
      expect(session).toBe(mockSession);
    });

    it('should return null when no session exists', async () => {
      mockSupabaseAuth.getSession.mockResolvedValue({
        data: { session: null },
        error: null,
      });

      const session = await authApi.getSession();

      expect(session).toBeNull();
    });

    it('should return null on error', async () => {
      mockSupabaseAuth.getSession.mockResolvedValue({
        data: { session: null },
        error: { message: 'Session error' },
      });

      const session = await authApi.getSession();

      expect(session).toBeNull();
    });
  });

  describe('getUser', () => {
    it('should return current user', async () => {
      const mockUser = { id: 'user-789', email: 'user@example.com' };
      mockSupabaseAuth.getUser.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      });

      const user = await authApi.getUser();

      expect(mockSupabaseAuth.getUser).toHaveBeenCalled();
      expect(user).toBe(mockUser);
    });

    it('should return null when no user', async () => {
      mockSupabaseAuth.getUser.mockResolvedValue({
        data: { user: null },
        error: null,
      });

      const user = await authApi.getUser();

      expect(user).toBeNull();
    });
  });

  describe('onAuthStateChange', () => {
    it('should subscribe to auth state changes', () => {
      const callback = jest.fn();
      
      const subscription = authApi.onAuthStateChange(callback);

      expect(mockSupabaseAuth.onAuthStateChange).toHaveBeenCalledWith(callback);
      expect(subscription).toBeDefined();
    });
  });
});

