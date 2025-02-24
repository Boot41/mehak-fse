import React, { useState, useEffect, useCallback } from 'react';
import { useApi } from '../../hooks/useApi';
import ApplicationRow from './ApplicationRow';
import NewApplicationForm from './NewApplicationForm';
import './styles.css';

const ApplicationList = () => {
  const [applications, setApplications] = useState([]);
  const { request, loading, error } = useApi();
  const [showForm, setShowForm] = useState(false);

  const fetchApplications = useCallback(async () => {
    try {
      const data = await request('/applications/');
      setApplications(data.results || []);
    } catch (error) {
      console.error('Failed to fetch applications:', error);
    }
  }, [request]);

  useEffect(() => {
    fetchApplications();
  }, [fetchApplications]);

  const handleApplicationSubmit = useCallback(async (newApplication) => {
    try {
      await request('/applications/', {
        method: 'POST',
        body: JSON.stringify(newApplication),
      });
      await fetchApplications();
      setShowForm(false);
    } catch (error) {
      console.error('Failed to create application:', error);
    }
  }, [request, fetchApplications]);

  const toggleForm = useCallback(() => {
    setShowForm(prev => !prev);
  }, []);

  if (loading && !applications.length) {
    return <div className="loading" role="status">Loading applications...</div>;
  }

  if (error && !applications.length) {
    return (
      <div className="error" role="alert">
        Error: {error}
      </div>
    );
  }

  return (
    <div className="applications-container">
      <div className="header">
        <h1>Job Applications</h1>
        <button
          className="new-application-button"
          onClick={toggleForm}
          aria-label="Create New Application"
        >
          New Application
        </button>
      </div>

      {showForm && (
        <NewApplicationForm
          onSubmit={handleApplicationSubmit}
          onCancel={toggleForm}
        />
      )}

      {applications.length > 0 ? (
        <div className="applications-table" role="table">
          <div className="table-header" role="row">
            <div role="columnheader">Applicant Name</div>
            <div role="columnheader">Job Title</div>
            <div role="columnheader">Company</div>
            <div role="columnheader">Status</div>
            <div role="columnheader">Actions</div>
          </div>
          {applications.map((application) => (
            <ApplicationRow
              key={application.id}
              application={application}
              onUpdate={fetchApplications}
            />
          ))}
        </div>
      ) : (
        <div className="no-applications" role="status">
          No job applications found. Create one to get started!
        </div>
      )}
    </div>
  );
};

export default ApplicationList;
