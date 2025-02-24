import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import PrivateRoute from './components/PrivateRoute';
import ErrorBoundary from './components/ErrorBoundary';
import auth from './services/auth';

// Guard component to prevent authenticated users from accessing public routes
const PublicRoute = ({ children }) => {
  const user = auth.getUser();
  const token = auth.getToken();

  if (user?.id && token) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

const App = () => {
  const GOOGLE_CLIENT_ID = "726611225914-ahgg2o6ub87k9iake8mf8jqgbnu1bg3v.apps.googleusercontent.com";

  return (
    <ErrorBoundary>
      <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
        <Routes>
          <Route 
            path="/" 
            element={
              <PublicRoute>
                <LandingPage />
              </PublicRoute>
            } 
          />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </GoogleOAuthProvider>
    </ErrorBoundary>
  );
};

export default App;