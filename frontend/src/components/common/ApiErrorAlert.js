import React from 'react';

/**
 * Displays API error messages in a consistent format
 * 
 * @param {Object} props
 * @param {string|Object} props.error - Error message or error object
 * @param {Function} props.onRetry - Optional callback to retry the operation
 * @param {string} props.className - Optional CSS class
 */
const ApiErrorAlert = ({ error, onRetry, className }) => {
  // Extract error message from different error formats
  const getErrorMessage = () => {
    if (!error) return 'Unknown error occurred';
    
    if (typeof error === 'string') return error;
    
    // Handle error objects from axios
    if (error.response) {
      // Server returned an error response
      const status = error.response.status;
      const data = error.response.data;
      
      if (status === 404) return 'The requested resource was not found (404)';
      if (status === 401) return 'Unauthorized access. Please log in and try again (401)';
      if (status === 403) return 'You do not have permission to access this resource (403)';
      if (status === 500) return 'Server encountered an error. Please try again later (500)';
      
      // Try to extract error message from response data
      if (data && data.message) return data.message;
      if (data && data.error) return data.error;
      if (data && typeof data === 'string') return data;
      
      return `Server error (${status})`;
    }
    
    // Network errors
    if (error.code === 'ECONNABORTED') return 'Request timeout. Please try again.';
    if (error.message) return error.message;
    
    return 'An error occurred while communicating with the server';
  };

  const errorMessage = getErrorMessage();
  
  return (
    <div className={`alert alert-danger d-flex align-items-center ${className || ''}`} role="alert">
      <i className="fas fa-exclamation-triangle me-2"></i>
      <div className="flex-grow-1">
        {errorMessage}
      </div>
      {onRetry && (
        <button 
          className="btn btn-sm btn-outline-danger ms-2"
          onClick={onRetry}
        >
          <i className="fas fa-sync-alt me-1"></i> Retry
        </button>
      )}
    </div>
  );
};

export default ApiErrorAlert; 