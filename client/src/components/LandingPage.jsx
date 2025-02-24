import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useGoogleLogin } from '@react-oauth/google';
import { Mail } from 'lucide-react';
import useLoadingState from '../hooks/useLoadingState';

const LandingPage = () => {
  const navigate = useNavigate();
  const { loading, error, withLoading } = useLoadingState();

  const login = useGoogleLogin({
    onSuccess: (response) => {
      console.log('Google OAuth Success:', response);
      // Store the access token in localStorage
      localStorage.setItem('user-auth-code', response.access_token);
      // Navigate to dashboard after successful login
      navigate('/dashboard');
    },
    onError: (error) => {
      console.error('Google OAuth Error:', error);
    },
    scope: 'email profile https://www.googleapis.com/auth/gmail.readonly'
  });

  const handleGmailConnect = async () => {
    try {
      await withLoading(async () => {
        login();
      });
    } catch (error) {
      console.error('Gmail connect error:', error);
    }
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