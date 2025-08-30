import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Zap, 
  Clock, 
  Users, 
  TrendingUp, 
  Instagram, 
  Palette,
  Workflow,
  Play,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import InstagramAuth from '../components/ui/InstagramAuth';
import CanvaAuth from '../components/ui/CanvaAuth';
import config from '../config/api';

const Dashboard: React.FC = () => {
  const [showInstagramAuth, setShowInstagramAuth] = useState(false);
  const [isInstagramConnected, setIsInstagramConnected] = useState(false);
  const [showCanvaAuth, setShowCanvaAuth] = useState(false);
  const [isCanvaConnected, setIsCanvaConnected] = useState(false);

  // Check Instagram connection status
  useEffect(() => {
    const checkInstagramStatus = async () => {
      try {
        const response = await fetch(`${config.api.baseUrl}/api/auth/instagram/status/default_user`);
        if (response.ok) {
          const data = await response.json();
          setIsInstagramConnected(data.authenticated);
        }
      } catch (error) {
        console.error('Failed to check Instagram status:', error);
        // Don't block UI on API errors
        setIsInstagramConnected(false);
      }
    };

    checkInstagramStatus();
  }, []);

  // Check Canva connection status
  useEffect(() => {
    const checkCanvaStatus = async () => {
      try {
        const response = await fetch(`${config.api.baseUrl}/api/auth/canva/status/default_user`);
        if (response.ok) {
          const data = await response.json();
          setIsCanvaConnected(data.authenticated);
        }
      } catch (error) {
        console.error('Failed to check Canva status:', error);
        // Don't block UI on API errors
        setIsCanvaConnected(false);
      }
    };

    checkCanvaStatus();
  }, []);


  
  const stats = [
    {
      name: 'Total Workflows',
      value: '24',
      change: '+12%',
      changeType: 'positive',
      icon: Workflow,
    },
    {
      name: 'Active Executions',
      value: '8',
      change: '+3',
      changeType: 'positive',
      icon: Play,
    },
    {
      name: 'Success Rate',
      value: '94.2%',
      change: '+2.1%',
      changeType: 'positive',
      icon: CheckCircle,
    },
    {
      name: 'Failed Executions',
      value: '3',
      change: '-1',
      changeType: 'negative',
      icon: AlertCircle,
    },
  ];

  const recentWorkflows = [
    {
      id: '1',
      name: 'Lead Qualification',
      status: 'completed',
      lastRun: '2 hours ago',
      successRate: '98%',
    },
    {
      id: '2',
      name: 'Content Generation',
      status: 'running',
      lastRun: '5 minutes ago',
      successRate: '95%',
    },
    {
      id: '3',
      name: 'Email Campaign',
      status: 'failed',
      lastRun: '1 hour ago',
      successRate: '87%',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-cormorant font-semibold text-secondary-900">
          Dashboard
        </h1>
        <p className="text-secondary-600 mt-2">
          Welcome back! Here's what's happening with your workflows.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card">
              <div className="card-content">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-secondary-600">
                      {stat.name}
                    </p>
                    <p className="text-2xl font-semibold text-secondary-900">
                      {stat.value}
                    </p>
                  </div>
                  <div className="p-2 bg-primary-50 rounded-lg">
                    <Icon className="h-6 w-6 text-primary-600" />
                  </div>
                </div>
                <div className="mt-4 flex items-center">
                  <TrendingUp className={`h-4 w-4 ${
                    stat.changeType === 'positive' ? 'text-success-500' : 'text-danger-500'
                  }`} />
                  <span className={`ml-1 text-sm font-medium ${
                    stat.changeType === 'positive' ? 'text-success-600' : 'text-danger-600'
                  }`}>
                    {stat.change}
                  </span>
                  <span className="ml-2 text-sm text-secondary-500">
                    from last month
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Integrations */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Integrations</h2>
          <p className="card-description">
            Connect your accounts for automated workflows
          </p>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Instagram */}
            <div 
              className={`flex items-center justify-between p-4 border rounded-lg transition-colors ${
                isInstagramConnected 
                  ? 'border-green-200 bg-green-50' 
                  : 'border-secondary-200 hover:bg-secondary-50 cursor-pointer'
              }`}
              onClick={!isInstagramConnected ? () => setShowInstagramAuth(true) : undefined}
            >
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${
                  isInstagramConnected ? 'bg-green-100' : 'bg-pink-50'
                }`}>
                  <Instagram className={`h-5 w-5 ${
                    isInstagramConnected ? 'text-green-600' : 'text-pink-600'
                  }`} />
                </div>
                <div>
                  <h3 className="font-medium text-secondary-900">Instagram</h3>
                  <p className="text-sm text-secondary-500">Auto-post content</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {isInstagramConnected ? (
                  <>
                    <span className="text-sm text-green-600 font-medium">Connected</span>
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowInstagramAuth(true);
                      }}
                      className="text-xs text-blue-600 hover:text-blue-700 font-medium ml-2"
                    >
                      Reconnect
                    </button>
                  </>
                ) : (
                  <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                    Connect
                  </button>
                )}
              </div>
            </div>

            {/* Canva */}
            <div 
              className={`flex items-center justify-between p-4 border rounded-lg transition-colors ${
                isCanvaConnected 
                  ? 'border-green-200 bg-green-50' 
                  : 'border-secondary-200 hover:bg-secondary-50 cursor-pointer'
              }`}
              onClick={!isCanvaConnected ? () => setShowCanvaAuth(true) : undefined}
            >
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${
                  isCanvaConnected ? 'bg-green-100' : 'bg-blue-50'
                }`}>
                  <svg className={`h-5 w-5 ${
                    isCanvaConnected ? 'text-green-600' : 'text-blue-600'
                  }`} fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium text-secondary-900">Canva</h3>
                  <p className="text-sm text-secondary-500">Professional templates</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {isCanvaConnected ? (
                  <>
                    <span className="text-sm text-green-600 font-medium">Connected</span>
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowCanvaAuth(true);
                      }}
                      className="text-xs text-blue-600 hover:text-blue-700 font-medium ml-2"
                    >
                      Reconnect
                    </button>
                  </>
                ) : (
                  <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                    Connect
                  </button>
                )}
              </div>
            </div>

            {/* Twitter/X - Coming Soon */}
            <div className="flex items-center justify-between p-4 border border-secondary-200 rounded-lg opacity-50">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-50 rounded-lg">
                  <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium text-secondary-900">Twitter/X</h3>
                  <p className="text-sm text-secondary-500">Post to Twitter/X</p>
                </div>
              </div>
              <span className="text-sm text-secondary-400">Soon</span>
            </div>

            {/* LinkedIn - Coming Soon */}
            <div className="flex items-center justify-between p-4 border border-secondary-200 rounded-lg opacity-50">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-50 rounded-lg">
                  <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium text-secondary-900">LinkedIn</h3>
                  <p className="text-sm text-secondary-500">Share to LinkedIn</p>
                </div>
              </div>
              <span className="text-sm text-secondary-400">Soon</span>
            </div>

            {/* Email - Coming Soon */}
            <div className="flex items-center justify-between p-4 border border-secondary-200 rounded-lg opacity-50">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-50 rounded-lg">
                  <svg className="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium text-secondary-900">Email</h3>
                  <p className="text-sm text-secondary-500">Send campaigns</p>
                </div>
              </div>
              <span className="text-sm text-secondary-400">Soon</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Workflows */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recent Workflows</h2>
          <p className="card-description">
            Your most recently executed workflows
          </p>
        </div>
        <div className="card-content">
          <div className="space-y-4">
            {recentWorkflows.map((workflow) => (
              <div
                key={workflow.id}
                className="flex items-center justify-between p-4 border border-secondary-200 rounded-lg hover:bg-secondary-50 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <div className="p-2 bg-primary-50 rounded-lg">
                    <Workflow className="h-5 w-5 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-secondary-900">
                      {workflow.name}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-secondary-500">
                      <span className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {workflow.lastRun}
                      </span>
                      <span className="flex items-center">
                        <CheckCircle className="h-4 w-4 mr-1" />
                        {workflow.successRate} success rate
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    workflow.status === 'completed'
                      ? 'bg-success-100 text-success-800'
                      : workflow.status === 'running'
                      ? 'bg-primary-100 text-primary-800'
                      : 'bg-danger-100 text-danger-800'
                  }`}>
                    {workflow.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Instagram Auth Modal */}
      {showInstagramAuth && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Connect Instagram</h2>
              <button
                onClick={() => setShowInstagramAuth(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-6">
              <InstagramAuth onTokenReceived={() => setShowInstagramAuth(false)} />
            </div>
          </div>
        </div>
      )}

      {/* Canva Auth Modal */}
      {showCanvaAuth && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Connect Canva</h2>
              <button
                onClick={() => setShowCanvaAuth(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-6">
              <CanvaAuth onTokenReceived={() => setShowCanvaAuth(false)} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard; 