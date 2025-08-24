import React, { useEffect, useState } from 'react';
import apiService from '../services/api';

const LinkedInConnect: React.FC = () => {
  const [status, setStatus] = useState<{ authenticated: boolean } | null>(null);
  const [loading, setLoading] = useState(false);

  const refreshStatus = async () => {
    try {
      const s = await apiService.getLinkedInStatus('default_user');
      setStatus({ authenticated: !!s.authenticated });
    } catch {
      setStatus(null);
    }
  };

  useEffect(() => {
    refreshStatus();
  }, []);

  const connect = async () => {
    try {
      setLoading(true);
      const { auth_url } = await apiService.getLinkedInAuthUrl();
      const popup = window.open(auth_url, 'linkedin_oauth', 'width=600,height=700');
      const timer = setInterval(() => {
        if (popup && popup.closed) {
          clearInterval(timer);
          refreshStatus();
        }
      }, 800);
    } catch (e) {
      console.error('Failed to start LinkedIn OAuth', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-4">Connect LinkedIn</h1>
      <p className="text-gray-600 mb-6">Authorize the app to post to your LinkedIn account.</p>
      <div className="flex items-center gap-4">
        <button
          onClick={connect}
          className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
          disabled={loading}
        >
          {loading ? 'Opening…' : 'Connect LinkedIn'}
        </button>
        {status && (
          <span className={status.authenticated ? 'text-green-600' : 'text-red-600'}>
            {status.authenticated ? 'Connected' : 'Not connected'}
          </span>
        )}
      </div>
    </div>
  );
};

export default LinkedInConnect;

