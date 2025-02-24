import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGoogleLogin } from '@react-oauth/google';
import { Mail } from 'lucide-react';
import useLoadingState from '../hooks/useLoadingState';
import auth from '../services/auth';

const LandingPage = () => {
  const navigate = useNavigate();
  const { loading, error, setError } = useLoadingState();

  // Only check once on mount
  useEffect(() => {
    const storedUser = auth.getUser();
    const token = auth.getToken();
    // Only redirect if we have both user data and token
    if (storedUser?.id && token) {
      navigate('/dashboard', { replace: true });
    }
  }, []); // Empty dependency array - only run once on mount

  const login = useGoogleLogin({
    onSuccess: async (response) => {
      try {
        // Store the access token
        auth.setToken(response.access_token);
        
        // Get user profile using the stored token
        await auth.getUserProfile();
        
        // Navigate to dashboard after successful login
        navigate('/dashboard', { replace: true });
      } catch (error) {
        console.error('Failed to complete login:', error);
        setError('Failed to complete login. Please try again.');
        auth.logout();
      }
    },
    onError: (error) => {
      console.error('Google OAuth Error:', error);
      setError('Failed to connect with Google. Please try again.');
    },
    scope: 'email profile https://www.googleapis.com/auth/gmail.readonly'
  });

  const handleGmailConnect = () => {
    setError(null);
    login();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex flex-col items-center justify-center p-4">
      <div className="max-w-3xl w-full text-center space-y-8">
        {/* Hero Section */}
        <div className="space-y-6">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight">
            Welcome to AI Job Tracker
          </h1>
          <p className="text-xl md:text-2xl text-gray-600">
            Smartly manage your job applications
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 my-12">
          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-lg text-gray-800 mb-2">Smart Tracking</h3>
            <p className="text-gray-600">Automatically organize your job applications</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-lg text-gray-800 mb-2">AI Insights</h3>
            <p className="text-gray-600">Get intelligent suggestions and analytics</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-lg text-gray-800 mb-2">Email Integration</h3>
            <p className="text-gray-600">Seamlessly connect with your Gmail account</p>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="text-red-600 bg-red-50 p-3 rounded-lg">
            {error}
          </div>
        )}

        {/* CTA Button */}
        <button
          onClick={handleGmailConnect}
          disabled={loading}
          className={`
            flex items-center justify-center gap-2 px-6 py-3 
            bg-white text-gray-800 rounded-lg shadow-md 
            hover:shadow-lg transition-shadow duration-200
            border border-gray-200 mx-auto
            ${loading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <Mail className="w-5 h-5" />
          <span>{loading ? 'Connecting...' : 'Connect with Gmail'}</span>
        </button>
      </div>
    </div>
  );
};

export default LandingPage;