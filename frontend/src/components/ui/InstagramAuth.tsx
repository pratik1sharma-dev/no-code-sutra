import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

interface InstagramAuthProps {
  onTokenReceived?: (token: string) => void;
}

const InstagramAuth: React.FC<InstagramAuthProps> = ({ onTokenReceived }) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [tokenData, setTokenData] = useState<any>(null);
  const [authUrl, setAuthUrl] = useState<string | null>(null);

  const initiateAuth = async () => {
    try {
      setStatus('loading');
      setMessage('Getting authorization URL...');
      
      const response = await fetch('http://localhost:8000/api/auth/instagram/url');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setAuthUrl(data.auth_url);
      
      // Open the auth URL in a new window
      window.open(data.auth_url, '_blank', 'width=600,height=700');
      
      setStatus('idle');
      setMessage('Authorization window opened. Complete the authentication and return here.');
    } catch (error) {
      console.error('Auth initiation error:', error);
      setStatus('error');
      setMessage(error instanceof Error ? error.message : 'Failed to get authorization URL');
    }
  };

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const error = searchParams.get('error');
        const success = searchParams.get('success');

        if (error) {
          setStatus('error');
          setMessage(`Authentication failed: ${error}`);
          return;
        }

        if (success === 'true') {
          setStatus('success');
          setMessage('Instagram authentication successful! Credentials have been automatically saved to the database.');
          
          // Call the callback if provided (for modal usage)
          if (onTokenReceived) {
            onTokenReceived('success');
          } else {
            // Close the window after a short delay (for callback route usage)
            setTimeout(() => {
              window.close();
              // If window.close() doesn't work, redirect to main app
              navigate('/app');
            }, 3000);
          }
          
          // Refresh the page to update connection status
          setTimeout(() => {
            window.location.reload();
          }, 1000);
          return;
        }

        if (!code) {
          // If no code, this might be the initial modal view
          return;
        }

        setStatus('loading');
        setMessage('Completing authentication...');

        // Call backend to complete OAuth flow
        const response = await fetch(`http://localhost:8000/api/auth/instagram/callback?code=${code}&state=${state || ''}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.success) {
          setStatus('success');
          setMessage('Instagram authentication successful!');
          setTokenData(data.token_data);
          
          // Store the access token (you might want to store this securely)
          localStorage.setItem('instagram_access_token', data.token_data.access_token);
          
          // Show success message about automatic storage
          if (data.credentials_saved) {
            setMessage('Instagram authentication successful! Credentials have been automatically saved to the database.');
          }
          
          // Call the callback if provided (for modal usage)
          if (onTokenReceived) {
            onTokenReceived(data.token_data.access_token);
          } else {
            // Close the window after a short delay (for callback route usage)
            setTimeout(() => {
              window.close();
              // If window.close() doesn't work, redirect to main app
              navigate('/app');
            }, 3000);
          }
        } else {
          throw new Error(data.message || 'Authentication failed');
        }
      } catch (error) {
        console.error('Instagram auth error:', error);
        setStatus('error');
        
        // Provide more helpful error messages
        let errorMessage = 'Authentication failed';
        if (error instanceof Error) {
          if (error.message.includes('400') || error.message.includes('Bad Request')) {
            errorMessage = 'Authorization code has expired or already been used. Please try again with a fresh authorization.';
          } else if (error.message.includes('401') || error.message.includes('Unauthorized')) {
            errorMessage = 'Invalid credentials. Please check your Facebook app settings.';
          } else if (error.message.includes('403') || error.message.includes('Forbidden')) {
            errorMessage = 'Access denied. Please check your app permissions.';
          } else {
            errorMessage = error.message;
          }
        }
        setMessage(errorMessage);
      }
    };

    handleCallback();
  }, [searchParams, navigate, onTokenReceived]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Instagram Authentication
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Completing your Instagram connection...
          </p>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          {status === 'idle' && (
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Connect Instagram Account
              </h3>
              <p className="text-sm text-gray-600 mb-6">
                Connect your Instagram Business Account to enable automatic posting.
              </p>
              <button
                onClick={initiateAuth}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Connect Instagram
              </button>
              {message && (
                <p className="mt-4 text-sm text-blue-600">
                  {message}
                </p>
              )}
            </div>
          )}

          {status === 'loading' && (
            <div className="flex items-center justify-center space-x-3">
              <Loader2 className="animate-spin h-6 w-6 text-blue-600" />
              <span className="text-gray-700">{message || 'Processing...'}</span>
            </div>
          )}

          {status === 'success' && (
            <div className="text-center">
              <CheckCircle className="mx-auto h-12 w-12 text-green-600 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Successfully Connected!
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                {message}
              </p>
              {tokenData && (
                <div className="bg-green-50 border border-green-200 rounded-md p-4 mb-4">
                  <div className="text-sm text-green-800">
                    <div className="font-medium">Access Token:</div>
                    <div className="font-mono text-xs mt-1">
                      {tokenData.access_token}
                    </div>
                    <div className="mt-2">
                      <div>Type: {tokenData.token_type}</div>
                      <div>Expires: {new Date(tokenData.expires_at).toLocaleDateString()}</div>
                    </div>
                  </div>
                </div>
              )}
              <p className="text-xs text-gray-500">
                {onTokenReceived ? 'Modal will close automatically...' : 'This window will close automatically...'}
              </p>
            </div>
          )}

          {status === 'error' && (
            <div className="text-center">
              <XCircle className="mx-auto h-12 w-12 text-red-600 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Authentication Failed
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                {message}
              </p>
              <div className="space-x-3">
                <button
                  onClick={initiateAuth}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Try Again
                </button>
                {!onTokenReceived && (
                  <button
                    onClick={() => window.close()}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    Close Window
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InstagramAuth;
