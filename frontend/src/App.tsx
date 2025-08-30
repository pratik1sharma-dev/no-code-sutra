import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoadingSpinner from './components/ui/LoadingSpinner';
import { ErrorBoundary } from './components/ui/ErrorBoundary';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import WorkflowBuilder from './pages/WorkflowBuilder';
import Workflows from './pages/Workflows';
import Schedules from './pages/Schedules';
import Login from './pages/Login';
import LandingPage from './pages/LandingPage';
import InstagramAuth from './components/ui/InstagramAuth';
import InstagramAuthCallback from './components/ui/InstagramAuthCallback';
import CanvaAuthCallback from './components/ui/CanvaAuthCallback';
import ProtectedRoute from './components/auth/ProtectedRoute';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            {/* Landing page as default */}
            <Route path="/" element={<LandingPage />} />
            
            {/* Protected routes */}
            <Route path="/app" element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }>
              <Route index element={<Dashboard />} />
              <Route path="workflows" element={<Workflows />} />
              <Route path="workflow" element={<WorkflowBuilder />} />
              <Route path="workflow/new" element={<WorkflowBuilder />} />
              <Route path="workflow-builder" element={<WorkflowBuilder />} />
              <Route path="schedules" element={<Schedules />} />
            </Route>
            
            {/* Dashboard route for login redirect */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }>
              <Route index element={<Dashboard />} />
            </Route>
            <Route path="/login" element={<Login />} />
            <Route path="/auth/instagram/callback" element={<InstagramAuthCallback />} />
            <Route path="/auth/canva/callback" element={<CanvaAuthCallback />} />
            
            {/* Catch-all route for 404s - redirect to landing page */}
            <Route path="*" element={<LandingPage />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ErrorBoundary>
  );
};

export default App;
