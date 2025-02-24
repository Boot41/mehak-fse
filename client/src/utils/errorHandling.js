/**
 * Custom error class for authentication-related errors
 */
export class AuthError extends Error {
  constructor(message, code, originalError = null) {
    super(message);
    this.name = 'AuthError';
    this.code = code;
    this.originalError = originalError;
  }
}

/**
 * Error codes for authentication-related errors
 */
export const AUTH_ERROR_CODES = {
  NETWORK_ERROR: 'network_error',
  INVALID_CREDENTIALS: 'invalid_credentials',
  TOKEN_EXPIRED: 'token_expired',
  GOOGLE_AUTH_FAILED: 'google_auth_failed',
  UNAUTHORIZED: 'unauthorized',
  SERVER_ERROR: 'server_error',
  UNKNOWN_ERROR: 'unknown_error',
};

/**
 * Maps HTTP status codes to user-friendly error messages
 */
const HTTP_ERROR_MESSAGES = {
  400: 'Invalid request. Please check your input.',
  401: 'Your session has expired. Please log in again.',
  403: 'You do not have permission to perform this action.',
  404: 'Resource not found.',
  429: 'Too many attempts. Please try again later.',
  500: 'Server error. Please try again later.',
  502: 'Service temporarily unavailable. Please try again later.',
  503: 'Service unavailable. Please try again later.',
  504: 'Server timeout. Please try again later.',
};

/**
 * Handles API errors and returns appropriate error messages
 * @param {Error} error - The error object from the API call
 * @param {Object} options - Additional options for error handling
 * @returns {AuthError} Standardized auth error object
 */
export const handleAuthError = (error, options = {}) => {
  const { context = 'operation' } = options;

  // Handle network errors
  if (!error.response) {
    return new AuthError(
      'Unable to connect to the server. Please check your internet connection.',
      AUTH_ERROR_CODES.NETWORK_ERROR,
      error
    );
  }

  // Handle API response errors
  const { status, data } = error.response;
  let errorMessage = data?.detail || data?.message || HTTP_ERROR_MESSAGES[status] || 'An unexpected error occurred';
  let errorCode = AUTH_ERROR_CODES.UNKNOWN_ERROR;

  // Map specific error scenarios
  switch (status) {
    case 400:
      if (data?.non_field_errors?.includes('Invalid credentials')) {
        errorCode = AUTH_ERROR_CODES.INVALID_CREDENTIALS;
        errorMessage = 'Invalid username or password. Please try again.';
      }
      break;
    case 401:
      errorCode = AUTH_ERROR_CODES.UNAUTHORIZED;
      if (data?.code === 'token_not_valid') {
        errorCode = AUTH_ERROR_CODES.TOKEN_EXPIRED;
        errorMessage = 'Your session has expired. Please log in again.';
      }
      break;
    case 403:
      errorCode = AUTH_ERROR_CODES.UNAUTHORIZED;
      break;
    case 500:
      errorCode = AUTH_ERROR_CODES.SERVER_ERROR;
      break;
  }

  // Add context to the error message if provided
  const contextualMessage = `Failed to ${context}: ${errorMessage}`;
  
  return new AuthError(contextualMessage, errorCode, error);
};

/**
 * Validates user credentials before making API calls
 * @param {Object} credentials - User credentials object
 * @throws {AuthError} If validation fails
 */
export const validateCredentials = (credentials) => {
  const { username, password } = credentials;
  
  if (!username || !password) {
    throw new AuthError(
      'Username and password are required.',
      AUTH_ERROR_CODES.INVALID_CREDENTIALS
    );
  }

  if (password.length < 8) {
    throw new AuthError(
      'Password must be at least 8 characters long.',
      AUTH_ERROR_CODES.INVALID_CREDENTIALS
    );
  }
};
