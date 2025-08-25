import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoadingSpinner from './components/ui/LoadingSpinner';
import { ErrorBoundary } from './components/ui/ErrorBoundary';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import WorkflowBuilder from './pages/WorkflowBuilder';
import Login from './pages/Login';
import LandingPage from './pages/LandingPage';
import InstagramAuth from './components/ui/InstagramAuth';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            {/* Landing page as default */}
            <Route path="/" element={<LandingPage />} />
            
            {/* App routes with layout */}
            <Route path="/app" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="workflow/:id?" element={<WorkflowBuilder />} />
            </Route>
            
            {/* Auth routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/auth/instagram/callback" element={<InstagramAuth />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ErrorBoundary>
  );
};

export default App;
