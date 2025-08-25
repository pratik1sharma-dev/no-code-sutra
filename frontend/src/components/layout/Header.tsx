import React, { useState, useEffect } from 'react';
import { Bell, Search, User, Settings, LogOut, Instagram } from 'lucide-react';
import InstagramAuth from '../ui/InstagramAuth';

const Header: React.FC = () => {
  const [showInstagramAuth, setShowInstagramAuth] = useState(false);
  const [isInstagramConnected, setIsInstagramConnected] = useState(false);
  const [instagramAccount, setInstagramAccount] = useState<any>(null);

  // Check Instagram connection status
  useEffect(() => {
    const checkInstagramStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/auth/instagram/status/default_user');
        if (response.ok) {
          const data = await response.json();
          setIsInstagramConnected(data.authenticated);
          if (data.credentials) {
            setInstagramAccount(data.credentials);
          }
        }
      } catch (error) {
        console.error('Failed to check Instagram status:', error);
      }
    };

    checkInstagramStatus();
  }, []);

  return (
    <header className="bg-white border-b border-secondary-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-secondary-400" />
            <input
              type="text"
              placeholder="Search workflows, templates..."
              className="w-full pl-10 pr-4 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Integrations */}
          <button 
            onClick={() => setShowInstagramAuth(true)}
            className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
              isInstagramConnected 
                ? 'text-green-600 hover:text-green-700 hover:bg-green-50' 
                : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50'
            }`}
            title="Manage Integrations"
          >
            <Instagram className={`h-5 w-5 ${isInstagramConnected ? 'text-green-600' : ''}`} />
            <span className="text-sm font-medium hidden sm:inline">
              Integrations
            </span>
            {isInstagramConnected && (
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            )}
          </button>

          {/* Notifications */}
          <button className="relative p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50 rounded-md transition-colors">
            <Bell className="h-5 w-5" />
            <span className="absolute top-1 right-1 h-2 w-2 bg-danger-500 rounded-full"></span>
          </button>

          {/* User Menu */}
          <div className="relative">
            <button className="flex items-center space-x-2 p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50 rounded-md transition-colors">
              <div className="h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center">
                <User className="h-4 w-4 text-primary-600" />
              </div>
              <span className="text-sm font-medium">John Doe</span>
            </button>
          </div>
        </div>

        {/* Integrations Modal */}
        {showInstagramAuth && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Integrations</h2>
                <button
                  onClick={() => setShowInstagramAuth(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="p-6 space-y-4">
                {/* Instagram Integration */}
                <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${isInstagramConnected ? 'bg-green-100' : 'bg-gray-100'}`}>
                      <Instagram className={`h-5 w-5 ${isInstagramConnected ? 'text-green-600' : 'text-gray-600'}`} />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">Instagram</h3>
                      <p className="text-sm text-gray-500">Auto-post content to Instagram</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {isInstagramConnected ? (
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-green-600 font-medium">Connected</span>
                        <button
                          onClick={() => {
                            // This will open the Instagram auth flow for reconnection
                            window.open('http://localhost:8000/api/auth/instagram/url', '_blank', 'width=600,height=700');
                          }}
                          className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                        >
                          Reconnect
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => {
                          // This will open the Instagram auth flow
                          window.open('http://localhost:8000/api/auth/instagram/url', '_blank', 'width=600,height=700');
                        }}
                        className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                      >
                        Connect
                      </button>
                    )}
                  </div>
                </div>

                {/* Future Integrations */}
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-gray-700">Coming Soon</h4>
                  
                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg opacity-50">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 rounded-lg bg-gray-100">
                        <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-900">Twitter/X</h3>
                        <p className="text-sm text-gray-500">Post to Twitter/X</p>
                      </div>
                    </div>
                    <span className="text-sm text-gray-400">Soon</span>
                  </div>

                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg opacity-50">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 rounded-lg bg-gray-100">
                        <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-900">LinkedIn</h3>
                        <p className="text-sm text-gray-500">Share to LinkedIn</p>
                      </div>
                    </div>
                    <span className="text-sm text-gray-400">Soon</span>
                  </div>

                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg opacity-50">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 rounded-lg bg-gray-100">
                        <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-900">Email</h3>
                        <p className="text-sm text-gray-500">Send email campaigns</p>
                      </div>
                    </div>
                    <span className="text-sm text-gray-400">Soon</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header; 