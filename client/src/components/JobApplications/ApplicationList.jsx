import React, { useState, useCallback, useEffect } from 'react';
import { Plus } from 'lucide-react';
import ApplicationRow from './ApplicationRow';
import NewApplicationForm from './NewApplicationForm';
import { mockApplications } from '../../data/mockApplications';

const ApplicationList = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showNewForm, setShowNewForm] = useState(false);

  // Simulate API fetch with mock data
  const fetchApplications = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 800));
      setApplications(mockApplications);
    } catch (error) {
      console.error('Failed to fetch applications:', error);
      setError('Failed to load applications. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchApplications();
  }, [fetchApplications]);

  const handleApplicationSubmit = useCallback(async (newApplication) => {
    try {
      setLoading(true);
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Add new application to the list with a generated ID
      const applicationWithId = {
        ...newApplication,
        id: Date.now(), // Use timestamp as temporary ID
        date: new Date().toISOString().split('T')[0],
        status: 'Applied'
      };
      
      setApplications(prev => [applicationWithId, ...prev]);
      setShowNewForm(false);
    } catch (error) {
      console.error('Failed to add application:', error);
      setError('Failed to add application. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  if (loading && applications.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error}</p>
        <button
          onClick={fetchApplications}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-900">
          Recent Applications ({applications.length})
        </h2>
        <button
          onClick={() => setShowNewForm(true)}
          className="flex items-center px-3 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Application
        </button>
      </div>

      {showNewForm && (
        <NewApplicationForm
          onSubmit={handleApplicationSubmit}
          onCancel={() => setShowNewForm(false)}
          loading={loading}
        />
      )}

      <div className="bg-white shadow-sm rounded-lg divide-y divide-gray-200">
        {applications.map((application) => (
          <ApplicationRow
            key={application.id}
            application={application}
          />
        ))}
        
        {applications.length === 0 && !loading && (
          <div className="text-center py-12 text-gray-500">
            No applications found. Add your first application!
          </div>
        )}
      </div>
    </div>
  );
};

export default ApplicationList;
