import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { 
  BrowserRouter,
  UNSAFE_NavigationContext,
  createRoutesFromChildren,
  matchRoutes,
} from 'react-router-dom';
import { 
  UNSAFE_DataRouterContext,
  UNSAFE_DataRouterStateContext,
} from 'react-router';
import App from './App';
import './index.css';

// Enable React Router v7 features
const router = {
  basename: '/',
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true
  }
};

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter {...router}>
      <App />
    </BrowserRouter>
  </StrictMode>
);