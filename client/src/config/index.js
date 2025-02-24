/**
 * Application configuration
 * This file centralizes all configuration values and provides defaults
 * for development. Production values should be set through environment variables.
 */

const config = {
  // API Configuration
  api: {
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
    authURL: import.meta.env.VITE_AUTH_URL || 'http://localhost:8000/api/token',
    timeout: 10000, // 10 seconds
  },

  // Authentication Configuration
  auth: {
    googleClientId: import.meta.env.VITE_GOOGLE_CLIENT_ID,
    googleRedirectUri: import.meta.env.VITE_GOOGLE_REDIRECT_URI || 'http://localhost:5173/oauth/callback',
    tokenStorageKey: 'authToken',
    refreshTokenStorageKey: 'refreshToken',
  },

  // Feature Flags
  features: {
    enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
    enableErrorReporting: import.meta.env.VITE_ENABLE_ERROR_REPORTING === 'true',
  },

  // Environment
  isDevelopment: import.meta.env.MODE === 'development',
  isProduction: import.meta.env.MODE === 'production',
  isTest: import.meta.env.MODE === 'test',
};

export default config;
