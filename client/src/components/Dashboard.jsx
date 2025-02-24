import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Mail, LogOut, RefreshCw } from 'lucide-react';
import { useAuth } from '@contexts/AuthContext';
import ApplicationList from './JobApplications/ApplicationList';
import ErrorAlert from './ErrorAlert';
import useLoadingState from '../hooks/useLoadingState';
import useAuthRedirect from '../hooks/useAuthRedirect';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { loading: authLoading, error: authError, withLoading } = useLoadingState();

  // Redirect to login if not authenticated
  useAuthRedirect(user, '/');

  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('user-auth-code');
    if (!token) {
      navigate('/');
      return;
    }
    fetchEmails();
  }, [navigate]);

  const fetchEmails = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem('user-auth-code');
      
      const response = await axios.get('http://localhost:8000/api/gmail/emails/', {
        headers: { Authorization: `Bearer ${token}` }
      });

      setEmails(response.data);
    } catch (error) {
      console.error('Error fetching emails:', error);
      if (error.response?.status === 401) {
        localStorage.removeItem('user-auth-code');
        navigate('/');
      } else {
        setError('Failed to fetch emails. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = useCallback(async () => {
    await withLoading(
      async () => {
        await logout();
        navigate('/');
      },
      { errorMessage: 'Logout failed. Please try again.' }
    );
  }, [logout, navigate, withLoading]);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Mail className="h-6 w-6 text-indigo-600" />
              <span className="ml-2 text-xl font-semibold text-gray-900">Email Dashboard</span>
            </div>
            <div className="flex items-center space-x-4">
              <button onClick={fetchEmails} className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </button>
              <button onClick={handleLogout} className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border-l-4 border-red-400 p-4">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {emails.map((email) => (
                <li key={email.id} className="px-6 py-4 hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-indigo-600 truncate">{email.subject}</p>
                    <p className="text-sm text-gray-500">{email.from}</p>
                    <p className="mt-1 text-sm text-gray-500">{new Date(email.date).toLocaleString()}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;