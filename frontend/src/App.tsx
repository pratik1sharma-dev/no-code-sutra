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
              <Route path="workflows" element={<Workflows />} />
              <Route path="workflow/:id?" element={<WorkflowBuilder />} />
              <Route path="schedules" element={<Schedules />} />
            </Route>
            
            {/* Auth routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/auth/instagram/callback" element={<InstagramAuthCallback />} />
            <Route path="/auth/canva/callback" element={<CanvaAuthCallback />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ErrorBoundary>
  );
};

export default App;
