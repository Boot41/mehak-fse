import { API_ERROR_TYPES } from './errorTypes';

export const handleApiError = (error) => {
  if (error.response) {
    // The request was made and the server responded with a status code
    const { status, data } = error.response;
    
    let errorType = API_ERROR_TYPES.UNKNOWN;
    let message = data.error || 'An unexpected error occurred';
    let details = data.details || {};
    
    switch (status) {
      case 429:
        errorType = API_ERROR_TYPES.RATE_LIMIT;
        message = 'Too many requests. Please try again later.';
        break;
      case 401:
        errorType = API_ERROR_TYPES.AUTH;
        message = 'Authentication required. Please log in.';
        break;
      case 403:
        errorType = API_ERROR_TYPES.AUTH;
        message = 'You do not have permission to perform this action.';
        break;
      case 422:
        errorType = API_ERROR_TYPES.VALIDATION;
        break;
      case 429:
        errorType = API_ERROR_TYPES.QUOTA;
        message = 'API quota exceeded. Please try again later.';
        break;
    }

    return Promise.reject({
      type: errorType,
      message,
      details,
      status,
    });
  }

  if (error.request) {
    // The request was made but no response was received
    return Promise.reject({
      type: API_ERROR_TYPES.NETWORK,
      message: 'Network error. Please check your connection.',
      details: {},
      status: 0,
    });
  }

  // Something happened in setting up the request
  return Promise.reject({
    type: API_ERROR_TYPES.UNKNOWN,
    message: error.message || 'An unexpected error occurred',
    details: {},
    status: 0,
  });
};
