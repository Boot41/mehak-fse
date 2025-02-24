import React from 'react';
import { Navigate } from 'react-router-dom';
import auth from '../services/auth';

const PrivateRoute = ({ children }) => {
  const user = auth.getUser();
  
  if (!user || !user.id) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default PrivateRoute;
