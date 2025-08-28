import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

const CanvaAuthCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const error = searchParams.get('error');
        const errorDescription = searchParams.get('error_description');
        const success = searchParams.get('canva_success');
        const userId = searchParams.get('user_id');

        if (error) {
          setStatus('error');
          setMessage(`Authentication failed: ${error}${errorDescription ? ` - ${errorDescription}` : ''}`);
          return;
        }

        if (success === 'true') {
          setStatus('success');
          setMessage('Canva authentication successful! Credentials have been automatically saved to the database.');
          
          // Close the window after a short delay
          setTimeout(() => {
            window.close();
            // If window.close() doesn't work, redirect to main app
            navigate('/app');
          }, 3000);
          
          return;
        }

        // If no success parameter, this might be an error
        setStatus('error');
        setMessage('Authentication failed: No success parameter received.');
        
      } catch (error) {
        console.error('Canva auth callback error:', error);
        setStatus('error');
        setMessage(error instanceof Error ? error.message : 'Authentication failed');
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Canva Authentication
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Completing your Canva connection...
          </p>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          {status === 'loading' && (
            <div className="flex items-center justify-center space-x-3">
              <Loader2 className="animate-spin h-6 w-6 text-blue-600" />
              <span className="text-gray-700">Processing authentication...</span>
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
              <p className="text-xs text-gray-500">
                This window will close automatically...
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
                  onClick={() => window.close()}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Close Window
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CanvaAuthCallback;

