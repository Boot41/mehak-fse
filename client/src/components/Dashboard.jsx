import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, LogOut, RefreshCw } from 'lucide-react';
import ApplicationList from './JobApplications/ApplicationList';
import ErrorAlert from './ErrorAlert';
import useLoadingState from '../hooks/useLoadingState';
import auth from '../services/auth';
import { mockApplications } from '../data/mockApplications';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const { loading: authLoading, error: authError } = useLoadingState();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const user = auth.getUser();
  const token = auth.getToken();

  const fetchApplications = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      setApplications(mockApplications);
    } catch (error) {
      console.error('Error fetching applications:', error);
      setError('Failed to fetch applications. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Check auth only once on mount
  useEffect(() => {
    if (!user?.id || !token) {
      // navigate('/', { replace: true });
      return;
    }
    fetchApplications();
  }, []); // Empty dependency array - only run once on mount

  const handleLogout = () => {
    auth.logout();
    navigate('/', { replace: true });
  };

  const handleRefresh = () => {
    fetchApplications();
  };

  // Don't render anything if not authenticated
  if (!user?.id || !token) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Job Applications</h1>
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="ml-4 p-2 text-gray-400 hover:text-gray-600"
                title="Refresh applications"
              >
                <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
            
            <div className="flex items-center space-x-4">
              {user && (
                <div className="flex items-center space-x-2">
                  <img
                    src={user.picture}
                    alt={user.name}
                    className="w-8 h-8 rounded-full"
                  />
                  <span className="text-sm text-gray-700">{user.name}</span>
                </div>
              )}
              <button
                onClick={handleLogout}
                className="flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && <ErrorAlert message={error} />}
        
        <ApplicationList 
          applications={applications} 
          loading={loading}
          error={error}
        />
      </main>
    </div>
  );
};

export default Dashboard;