import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, test, expect, vi, beforeAll, afterEach, afterAll } from 'vitest';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../Dashboard';
import { AuthProvider } from '../../contexts/AuthContext';

const mockApplications = {
  count: 2,
  next: null,
  previous: null,
  results: [
    {
      id: 1,
      applicant_name: 'John Doe',
      job_title: 'Software Engineer',
      company_name: 'Tech Corp',
      status: 'applied',
      email_content: 'Test application 1',
      created_at: '2025-02-24T04:08:03.563600Z',
      updated_at: '2025-02-24T04:08:03.563792Z'
    },
    {
      id: 2,
      applicant_name: 'Jane Smith',
      job_title: 'Data Scientist',
      company_name: 'AI Corp',
      status: 'screening',
      email_content: 'Test application 2',
      created_at: '2025-02-24T04:09:03.563600Z',
      updated_at: '2025-02-24T04:09:03.563792Z'
    }
  ]
};

// Set up MSW server to intercept API requests
const server = setupServer(
  http.get('http://localhost:8001/api/applications/', () => {
    return HttpResponse.json(mockApplications);
  }),
  http.post('http://localhost:8001/api/applications/', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ ...body, id: 3 }, { status: 201 });
  }),
  http.patch('http://localhost:8001/api/applications/:id/', ({ params }) => {
    const { id } = params;
    const updatedApplication = {
      ...mockApplications.results.find(app => app.id === parseInt(id)),
      status: 'interviewed'
    };
    mockApplications.results = mockApplications.results.map(app => 
      app.id === parseInt(id) ? updatedApplication : app
    );
    return HttpResponse.json(updatedApplication);
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Mock AuthContext
vi.mock('../../contexts/AuthContext', () => ({
  AuthProvider: ({ children }) => children,
  useAuth: () => ({
    user: { username: 'testuser', email: 'test@example.com' },
    loading: false,
    error: null,
    logout: vi.fn()
  })
}));

// Wrapper component for tests
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      {children}
    </AuthProvider>
  </BrowserRouter>
);

describe('Dashboard Component', () => {
  test('renders dashboard with job applications', async () => {
    render(<Dashboard />, { wrapper: TestWrapper });

    // Should show loading initially
    expect(screen.getByText(/loading applications/i)).toBeInTheDocument();

    // Wait for applications to load
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });

    // Should show application details
    expect(screen.getByText('Tech Corp')).toBeInTheDocument();
    expect(screen.getByText('AI Corp')).toBeInTheDocument();
  });

  test('handles error state', async () => {
    server.use(
      http.get('http://localhost:8001/api/applications/', () => {
        return new HttpResponse(JSON.stringify({ error: 'Failed to fetch data' }), { status: 500 });
      })
    );

    render(<Dashboard />, { wrapper: TestWrapper });

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  test('creates new application', async () => {
    render(<Dashboard />, { wrapper: TestWrapper });

    // Wait for applications to load
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Click new application button
    const newButton = screen.getByRole('button', { name: /new application/i });
    fireEvent.click(newButton);

    // Form should be visible
    expect(screen.getByLabelText(/applicant name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/job title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/company/i)).toBeInTheDocument();
  });

  test('updates application status', async () => {
    render(<Dashboard />, { wrapper: TestWrapper });

    // Wait for applications to load
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Find and change status select
    const statusSelects = screen.getAllByRole('combobox');
    fireEvent.change(statusSelects[0], { target: { value: 'interviewed' } });

    // Wait for the API call to complete and the component to re-render
    await waitFor(() => {
      expect(screen.getAllByRole('combobox')[0]).toHaveValue('interviewed');
    }, { timeout: 2000 });
  });

  test('shows application details', async () => {
    render(<Dashboard />, { wrapper: TestWrapper });

    // Wait for applications to load
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Click view details button
    const detailsButtons = screen.getAllByRole('button', { name: /view details/i });
    fireEvent.click(detailsButtons[0]);

    // Should show email content
    expect(screen.getByText('Test application 1')).toBeInTheDocument();
  });
});
