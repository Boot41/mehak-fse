import axios from 'axios';

const API_URL = 'http://localhost:8000/api';
const TOKEN_KEY = 'user-auth-code';
const USER_KEY = 'user_data';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add interceptor to include auth token in requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

const auth = {
  // Store access token
  setToken: (token) => {
    localStorage.setItem(TOKEN_KEY, token);
  },

  // Get current auth token
  getToken: () => {
    return localStorage.getItem(TOKEN_KEY);
  },

  // Store user data
  setUser: (userData) => {
    localStorage.setItem(USER_KEY, JSON.stringify(userData));
  },

  // Get current user data
  getUser: () => {
    const userData = localStorage.getItem(USER_KEY);
    return userData ? JSON.parse(userData) : null;
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem(TOKEN_KEY);
  },

  // Clear auth data
  logout: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(user_data);
    delete api.defaults.headers.common['Authorization'];
  },

  // Get user profile using the access token
  getUserProfile: async () => {
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token) {
        throw new Error('No authentication token found');
      }

      // Use Google's userinfo endpoint to get user details
      const response = await axios.get('https://www.googleapis.com/oauth2/v3/userinfo', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      const userData = {
        id: response.data.sub,
        email: response.data.email,
        name: response.data.name,
        picture: response.data.picture
      };

      // Store user data
      localStorage.setItem(USER_KEY, JSON.stringify(userData));

      return userData;
    } catch (error) {
      console.error('Failed to get user profile:', error);
      auth.logout(); // Clear invalid auth state
      throw error;
    }
  }
};

export default auth;

// Export the configured axios instance
export { api };
