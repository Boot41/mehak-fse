import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, test, expect, beforeAll, afterEach, afterAll, beforeEach, vi } from 'vitest';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import ApplicationRow from '../ApplicationRow';

const mockApplication = {
  id: 1,
  applicant_name: 'John Doe',
  job_title: 'Software Engineer',
  company_name: 'Tech Corp',
  status: 'applied',
  email_content: 'Test application email content',
  created_at: '2025-02-24T04:08:03.563600Z',
  updated_at: '2025-02-24T04:08:03.563792Z'
};

const server = setupServer(
  http.patch('http://localhost:8001/api/applications/1/', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ ...mockApplication, ...body });
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('ApplicationRow Component', () => {
  const mockOnUpdate = vi.fn();

  beforeEach(() => {
    mockOnUpdate.mockClear();
  });

  test('renders application information correctly', () => {
    render(
      <ApplicationRow
        application={mockApplication}
        onUpdate={mockOnUpdate}
      />
    );

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Software Engineer')).toBeInTheDocument();
    expect(screen.getByText('Tech Corp')).toBeInTheDocument();
    expect(screen.getByRole('combobox')).toHaveValue('applied');
  });

  test('expands to show email content when View Details is clicked', () => {
    render(
      <ApplicationRow
        application={mockApplication}
        onUpdate={mockOnUpdate}
      />
    );

    // Email content should not be visible initially
    expect(screen.queryByText('Test application email content')).not.toBeInTheDocument();

    // Click View Details button
    fireEvent.click(screen.getByText('View Details'));

    // Email content should now be visible
    expect(screen.getByText('Test application email content')).toBeInTheDocument();

    // Click again to hide details
    fireEvent.click(screen.getByText('Hide Details'));

    // Email content should be hidden again
    expect(screen.queryByText('Test application email content')).not.toBeInTheDocument();
  });

  test('updates status when status is changed', async () => {
    render(
      <ApplicationRow
        application={mockApplication}
        onUpdate={mockOnUpdate}
      />
    );

    const statusSelect = screen.getByRole('combobox');
    fireEvent.change(statusSelect, { target: { value: 'screening' } });

    await waitFor(() => {
      expect(mockOnUpdate).toHaveBeenCalled();
    });
  });

  test('handles status update error gracefully', async () => {
    server.use(
      http.patch('http://localhost:8001/api/applications/1/', () => {
        return new HttpResponse(JSON.stringify({ error: 'Failed to update status' }), { status: 500 });
      })
    );

    render(
      <ApplicationRow
        application={mockApplication}
        onUpdate={mockOnUpdate}
      />
    );

    const statusSelect = screen.getByRole('combobox');
    fireEvent.change(statusSelect, { target: { value: 'screening' } });

    await waitFor(() => {
      expect(mockOnUpdate).not.toHaveBeenCalled();
    });
  });
});
