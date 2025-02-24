import api from './api';

class JobApplicationsService {
  async getApplications(params = {}) {
    const response = await api.get('/job_applications/', { params });
    return response.data;
  }

  async updateStatus(id, status) {
    const response = await api.patch(`/job_applications/${id}/`, { status });
    return response.data;
  }

  async processGmailEmails(query, maxResults = 10) {
    const response = await api.post('/job_applications/process_emails/', {
      query,
      max_results: maxResults
    });
    return response.data;
  }
}

export const jobApplicationsService = new JobApplicationsService();
