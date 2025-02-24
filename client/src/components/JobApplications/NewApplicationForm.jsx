import React, { useState } from 'react';
import './styles.css';

const INITIAL_FORM_STATE = {
  applicant_name: '',
  job_title: '',
  company_name: '',
  status: 'applied',
  email_content: '',
};

const NewApplicationForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState(INITIAL_FORM_STATE);
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};
    if (!formData.applicant_name.trim()) {
      newErrors.applicant_name = 'Applicant name is required';
    }
    if (!formData.job_title.trim()) {
      newErrors.job_title = 'Job title is required';
    }
    if (!formData.company_name.trim()) {
      newErrors.company_name = 'Company name is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
      setFormData(INITIAL_FORM_STATE);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  return (
    <form className="new-application-form" onSubmit={handleSubmit}>
      <h2>New Job Application</h2>
      
      <div className="form-group">
        <label htmlFor="applicant_name">Applicant Name:</label>
        <input
          type="text"
          id="applicant_name"
          name="applicant_name"
          value={formData.applicant_name}
          onChange={handleChange}
          className={errors.applicant_name ? 'error' : ''}
        />
        {errors.applicant_name && (
          <span className="error-message">{errors.applicant_name}</span>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="job_title">Job Title:</label>
        <input
          type="text"
          id="job_title"
          name="job_title"
          value={formData.job_title}
          onChange={handleChange}
          className={errors.job_title ? 'error' : ''}
        />
        {errors.job_title && (
          <span className="error-message">{errors.job_title}</span>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="company_name">Company Name:</label>
        <input
          type="text"
          id="company_name"
          name="company_name"
          value={formData.company_name}
          onChange={handleChange}
          className={errors.company_name ? 'error' : ''}
        />
        {errors.company_name && (
          <span className="error-message">{errors.company_name}</span>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="status">Status:</label>
        <select
          id="status"
          name="status"
          value={formData.status}
          onChange={handleChange}
        >
          <option value="applied">Applied</option>
          <option value="screening">Screening</option>
          <option value="interviewed">Interviewed</option>
          <option value="offer">Offer</option>
          <option value="accepted">Accepted</option>
          <option value="rejected">Rejected</option>
          <option value="ghosted">Ghosted</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="email_content">Email Content:</label>
        <textarea
          id="email_content"
          name="email_content"
          value={formData.email_content}
          onChange={handleChange}
          rows="4"
        />
      </div>

      <div className="form-actions">
        <button type="submit" className="submit-button">
          Submit
        </button>
        <button type="button" className="cancel-button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
};

export default NewApplicationForm;
