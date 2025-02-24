import { useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { AUTH_ERROR_CODES } from '../utils/errorHandling';

/**
 * Custom hook for handling authentication errors in components
 * @param {Object} options - Configuration options
 * @param {Function} options.onUnauthorized - Callback for unauthorized errors
 * @param {Function} options.onNetworkError - Callback for network errors
 * @param {Function} options.onError - General error callback
 * @returns {Object} Error handling utilities
 */
const useAuthError = (options = {}) => {
  const { error, retryWithBackoff } = useAuth();
  const { onUnauthorized, onNetworkError, onError } = options;

  useEffect(() => {
    if (!error) return;

    // Handle specific error types
    switch (error.code) {
      case AUTH_ERROR_CODES.UNAUTHORIZED:
      case AUTH_ERROR_CODES.TOKEN_EXPIRED:
        onUnauthorized?.(error);
        break;
      case AUTH_ERROR_CODES.NETWORK_ERROR:
        onNetworkError?.(error);
        break;
      default:
        onError?.(error);
    }
  }, [error, onUnauthorized, onNetworkError, onError]);

  /**
   * Executes an operation with automatic retries for network errors
   * @param {Function} operation - Async operation to execute
   * @param {Object} options - Retry options
   * @returns {Promise} Operation result
   */
  const executeWithRetry = async (operation, options = {}) => {
    const { maxRetries = 3, onRetry } = options;

    try {
      return await retryWithBackoff(operation, maxRetries);
    } catch (error) {
      if (error.code === AUTH_ERROR_CODES.NETWORK_ERROR && onRetry) {
        onRetry(error);
      }
      throw error;
    }
  };

  return {
    executeWithRetry,
    hasError: !!error,
    isNetworkError: error?.code === AUTH_ERROR_CODES.NETWORK_ERROR,
    isAuthError: error?.code === AUTH_ERROR_CODES.UNAUTHORIZED || error?.code === AUTH_ERROR_CODES.TOKEN_EXPIRED,
  };
};

export default useAuthError;
