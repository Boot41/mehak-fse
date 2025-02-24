import { useState, useCallback } from 'react';
import { jobApplicationsService } from '@services';

export const useJobApplications = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
    current: 1,
  });

  // Clear error state
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Fetch job applications with filters and pagination
  const fetchApplications = useCallback(async ({
    page = 1,
    pageSize = 10,
    search = '',
    status = [],
    dateRange = '',
    dateFrom = '',
    dateTo = '',
  } = {}) => {
    setLoading(true);
    setError(null);
    try {
      const data = await jobApplicationsService.getApplications({
        page,
        pageSize,
        search,
        status: status.join(','),
        dateRange,
        dateFrom,
        dateTo,
      });
      setApplications(data.results);
      setPagination({
        count: data.count,
        next: data.next,
        previous: data.previous,
        current: page,
      });
    } catch (err) {
      setError({
        type: err.type || 'UNKNOWN',
        message: err.message || 'Failed to fetch job applications',
      });
    } finally {
      setLoading(false);
    }
  }, []);

  // Update job application status
  const updateApplicationStatus = useCallback(async (id, status) => {
    setError(null);
    try {
      const updatedApplication = await jobApplicationsService.updateStatus(id, status);
      setApplications(prevApplications =>
        prevApplications.map(app =>
          app.id === id ? { ...app, status: updatedApplication.status } : app
        )
      );
      return updatedApplication;
    } catch (err) {
      setError({
        type: err.type || 'UNKNOWN',
        message: err.message || 'Failed to update application status',
      });
      throw err;
    }
  }, []);

  // Process Gmail emails
  const processEmails = useCallback(async (query, maxResults = 10) => {
    setError(null);
    try {
      const result = await jobApplicationsService.processGmailEmails(query, maxResults);
      // Refresh the applications list after processing emails
      await fetchApplications();
      return result;
    } catch (err) {
      setError({
        type: err.type || 'UNKNOWN',
        message: err.message || 'Failed to process emails',
      });
      throw err;
    }
  }, [fetchApplications]);

  return {
    applications,
    loading,
    error,
    pagination,
    clearError,
    fetchApplications,
    updateApplicationStatus,
    processEmails,
  };
};
