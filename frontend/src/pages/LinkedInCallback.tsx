import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const LinkedInCallback: React.FC = () => {
  const navigate = useNavigate();
  useEffect(() => {
    // The backend redirects here after OAuth. We can close the window or navigate.
    // If opened in a popup, just close; else go to connect page which will show status.
    if (window.opener) {
      window.close();
    } else {
      navigate('/linkedin/connect');
    }
  }, [navigate]);

  return (
    <div className="p-8 text-center">Completing LinkedIn authentication…</div>
  );
};

export default LinkedInCallback;

