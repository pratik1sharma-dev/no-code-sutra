import React, { useState, useEffect } from 'react';
import config from '../../config/api';

interface CanvaAuthProps {
  onTokenReceived?: (token: string) => void;
  onAuthError?: (error: string) => void;
}

interface CanvaAuthStatus {
  authenticated: boolean;
  credentials?: any;
}

const CanvaAuth: React.FC<CanvaAuthProps> = ({ onTokenReceived, onAuthError }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [authStatus, setAuthStatus] = useState<CanvaAuthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch(`${config.api.baseUrl}/api/auth/canva/status/default_user`);
      if (response.ok) {
        const data = await response.json();
        setAuthStatus(data);
        setIsAuthenticated(data.authenticated);
      } else {
        console.error('Failed to check Canva auth status');
      }
    } catch (err) {
      console.error('Error checking Canva auth status:', err);
    }
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const handleConnectCanva = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Get authorization URL
      const response = await fetch(config.getApiUrl(config.api.endpoints.canvaAuthUrl));
      if (!response.ok) {
        throw new Error('Failed to get Canva authorization URL');
      }

      const data = await response.json();
      
      // Open OAuth popup
      const popup = window.open(
        data.auth_url,
        'canva_oauth',
        'width=600,height=700,scrollbars=yes,resizable=yes'
      );

      if (!popup) {
        throw new Error('Popup blocked. Please allow popups for this site.');
      }

      // Listen for popup close
      const checkClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkClosed);
          setIsLoading(false);
          // Check auth status after popup closes
          setTimeout(checkAuthStatus, 1000);
        }
      }, 1000);

    } catch (err) {
      setIsLoading(false);
      const errorMessage = err instanceof Error ? err.message : 'Failed to connect to Canva';
      setError(errorMessage);
      onAuthError?.(errorMessage);
    }
  };

  const handleDisconnect = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${config.api.baseUrl}${config.api.endpoints.canvaCallback}?code=${code}&state=${state}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setIsAuthenticated(false);
        setAuthStatus(null);
        onTokenReceived?.('disconnected');
      } else {
        throw new Error('Failed to disconnect Canva');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to disconnect Canva';
      setError(errorMessage);
      onAuthError?.(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReconnect = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Call the reconnect endpoint to clear old credentials and get new auth URL
      const response = await fetch(`${config.api.baseUrl}/api/auth/canva/reconnect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'default_user'
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to initiate Canva reconnection');
      }

      const data = await response.json();
      
      if (data.success && data.auth_url) {
        // Open OAuth popup with new authorization URL
        const popup = window.open(
          data.auth_url,
          'canva_oauth',
          'width=600,height=700,scrollbars=yes,resizable=yes'
        );

        if (!popup) {
          throw new Error('Popup blocked. Please allow popups for this site.');
        }

        // Listen for popup close
        const checkClosed = setInterval(() => {
          if (popup.closed) {
            clearInterval(checkClosed);
            setIsLoading(false);
            // Check auth status after popup closes
            setTimeout(checkAuthStatus, 1000);
          }
        }, 1000);
      } else {
        throw new Error(data.message || 'Failed to get reconnection URL');
      }
    } catch (err) {
      setIsLoading(false);
      const errorMessage = err instanceof Error ? err.message : 'Failed to reconnect to Canva';
      setError(errorMessage);
      onAuthError?.(errorMessage);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Canva Integration</h3>
            <p className="text-sm text-gray-600">Connect to Canva for professional templates</p>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
          isAuthenticated 
            ? 'bg-green-100 text-green-800' 
            : 'bg-gray-100 text-gray-800'
        }`}>
          {isAuthenticated ? 'Connected' : 'Not Connected'}
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {authStatus && isAuthenticated && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-green-600">
            ✅ Canva is connected and ready to use with professional templates!
          </p>
        </div>
      )}

      <div className="space-y-3">
        {!isAuthenticated ? (
          <button
            onClick={handleConnectCanva}
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-2 px-4 rounded-md hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            {isLoading ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Connecting...</span>
              </div>
            ) : (
              <div className="flex items-center justify-center space-x-2">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
                <span>Connect Canva</span>
              </div>
            )}
          </button>
        ) : (
          <div className="space-y-2">
            <button
              onClick={handleReconnect}
              disabled={isLoading}
              className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {isLoading ? 'Reconnecting...' : 'Reconnect Canva'}
            </button>
            <button
              onClick={handleDisconnect}
              disabled={isLoading}
              className="w-full bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              Disconnect Canva
            </button>
          </div>
        )}
      </div>

      <div className="mt-4 text-xs text-gray-500">
        <p>• Access professional Canva templates</p>
        <p>• Create high-quality designs automatically</p>
        <p>• Seamless integration with your workflows</p>
      </div>
    </div>
  );
};

export default CanvaAuth;
