import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Hook for handling authentication-based redirects
 * @param {Object} user - Current user object
 * @param {string} redirectPath - Path to redirect to if condition is met
 * @param {boolean} redirectIfAuthenticated - If true, redirects when user is authenticated; if false, redirects when not authenticated
 */
const useAuthRedirect = (user, redirectPath, redirectIfAuthenticated = false) => {
  const navigate = useNavigate();

  useEffect(() => {
    const shouldRedirect = redirectIfAuthenticated ? user : !user;
    if (shouldRedirect) {
      navigate(redirectPath);
    }
  }, [user, navigate, redirectPath, redirectIfAuthenticated]);
};

export default useAuthRedirect;
