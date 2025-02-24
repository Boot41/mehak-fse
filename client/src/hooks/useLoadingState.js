import { useState, useCallback } from 'react';

/**
 * Hook for managing loading state and error handling in async operations
 * @returns {Object} Loading state management functions and state
 */
const useLoadingState = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Wraps an async operation with loading state and error handling
   * @param {Function} operation - Async operation to execute
   * @param {Object} options - Additional options
   * @param {string} options.errorMessage - Default error message if none provided
   * @returns {Promise} Result of the operation
   */
  const withLoading = useCallback(async (operation, options = {}) => {
    const { errorMessage = 'Operation failed. Please try again.' } = options;

    try {
      setLoading(true);
      setError(null);
      return await operation();
    } catch (err) {
      const message = err.message || errorMessage;
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Clears any existing error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    loading,
    error,
    withLoading,
    clearError,
    setError
  };
};

export default useLoadingState;
