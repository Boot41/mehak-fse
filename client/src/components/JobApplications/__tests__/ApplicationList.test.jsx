import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, test, expect, beforeAll, afterEach, afterAll } from 'vitest';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import ApplicationList from '../ApplicationList';
import { AuthProvider } from '../../../contexts/AuthContext';

// Mock API response data
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
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Mock AuthContext
const mockAuthContext = {
  user: { username: 'testuser' },
  loading: false,
  error: null,
  login: vi.fn(),
  logout: vi.fn(),
};

// Wrap component with necessary providers
const renderWithProviders = (component) => {
  return render(
    <AuthProvider>{component}</AuthProvider>
  );
};

describe('ApplicationList Component', () => {
  test('renders loading state initially', () => {
    renderWithProviders(<ApplicationList />);
    expect(screen.getByText(/loading applications/i)).toBeInTheDocument();
  });

  test('renders applications table after loading', async () => {
    renderWithProviders(<ApplicationList />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });

    expect(screen.getByText('Tech Corp')).toBeInTheDocument();
    expect(screen.getByText('AI Corp')).toBeInTheDocument();
  });

  test('shows new application form when button is clicked', async () => {
    renderWithProviders(<ApplicationList />);

    await waitFor(() => {
      expect(screen.getByText(/new application/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/new application/i));
    expect(screen.getByLabelText(/applicant name/i)).toBeInTheDocument();
  });

  test('handles API error gracefully', async () => {
    server.use(
      http.get('http://localhost:8001/api/applications/', () => {
        return new HttpResponse(JSON.stringify({ error: 'Failed to fetch applications' }), { status: 500 });
      })
    );

    renderWithProviders(<ApplicationList />);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
