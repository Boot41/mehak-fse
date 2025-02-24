import React, { useState, useCallback } from 'react';
import { useApi } from '../../hooks/useApi';
import { STATUS_COLORS, STATUS_OPTIONS } from '../../constants/applicationConstants';
import './styles.css';

const ApplicationRow = ({ application, onUpdate }) => {
  const [expanded, setExpanded] = useState(false);
  const { request, loading } = useApi();

  const handleStatusChange = useCallback(async (newStatus) => {
    try {
      await request(`/applications/${application.id}/`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus }),
      });
      onUpdate();
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  }, [application.id, request, onUpdate]);

  const toggleExpanded = useCallback(() => {
    setExpanded(prev => !prev);
  }, []);

  const formatDate = useCallback((dateString) => {
    return new Date(dateString).toLocaleDateString();
  }, []);

  return (
    <div className="application-row">
      <div className="application-summary">
        <div>{application.applicant_name}</div>
        <div>{application.job_title}</div>
        <div>{application.company_name}</div>
        <div>
          <select
            value={application.status}
            onChange={(e) => handleStatusChange(e.target.value)}
            style={{ backgroundColor: STATUS_COLORS[application.status] }}
            disabled={loading}
            aria-label="Application Status"
          >
            {STATUS_OPTIONS.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <button
          className="view-details-button"
          onClick={toggleExpanded}
          aria-expanded={expanded}
        >
          {expanded ? 'Hide Details' : 'View Details'}
        </button>
      </div>
      {expanded && (
        <div className="application-details">
          <h3>Email Content:</h3>
          <pre>{application.email_content}</pre>
          <div className="details-footer">
            <div>Created: {formatDate(application.created_at)}</div>
            <div>Updated: {formatDate(application.updated_at)}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApplicationRow;
