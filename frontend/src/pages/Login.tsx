import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

declare global {
  interface Window {
    google: any;
  }
}

const LoginPage: React.FC = () => {
  const { login, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string>('');
  const [isGoogleLoading, setIsGoogleLoading] = useState(true);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    const loadGoogleScript = () => {
      // Check if Google script is already loaded
      if (window.google) {
        initializeGoogleSignIn();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = initializeGoogleSignIn;
      script.onerror = () => {
        console.error('Failed to load Google Sign-In script');
        setError('Failed to load Google Sign-In. Please check your internet connection.');
        setIsGoogleLoading(false);
      };
      document.head.appendChild(script);
    };

    const initializeGoogleSignIn = () => {
      const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;
      
      if (!clientId || clientId === 'your-google-client-id') {
        setError('Google Client ID not configured. Please check your environment variables.');
        setIsGoogleLoading(false);
        return;
      }

      if (window.google && window.google.accounts) {
        try {
          window.google.accounts.id.initialize({
            client_id: clientId,
            callback: handleGoogleResponse,
          });

          // Wait for the element to be rendered
          setTimeout(() => {
            const buttonElement = document.getElementById('google-signin-button');
            if (buttonElement) {
              window.google.accounts.id.renderButton(
                buttonElement,
                { 
                  theme: 'outline', 
                  size: 'large',
                  width: 350,
                  text: 'signin_with'
                }
              );
            } else {
              setError('Failed to render Google Sign-In button');
            }
            setIsGoogleLoading(false);
          }, 200);
        } catch (error) {
          console.error('Error initializing Google Sign-In:', error);
          setError('Failed to initialize Google Sign-In');
          setIsGoogleLoading(false);
        }
      } else {
        setError('Google Sign-In API not available');
        setIsGoogleLoading(false);
      }
    };

    const handleGoogleResponse = async (response: any) => {
      try {
        setError('');
        await login(response.credential);
      } catch (err: any) {
        setError(err.message || 'Login failed');
      }
    };

    loadGoogleScript();
  }, [login]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-blue-100">
            <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Welcome to Garudaco
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Your personalized learning assessment platform
          </p>
        </div>

        <div className="mt-8 space-y-6">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-6">
              Sign in with your Google account to get started
            </p>
            
            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                {error}
              </div>
            )}

            <div className="flex justify-center">
              {isGoogleLoading ? (
                <div className="animate-pulse bg-gray-200 h-12 w-80 rounded"></div>
              ) : (
                <div id="google-signin-button"></div>
              )}
            </div>
          </div>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-50 text-gray-500">
                  Secure authentication powered by Google
                </span>
              </div>
            </div>
          </div>

          <div className="mt-6 text-center text-xs text-gray-500">
            <p>
              By signing in, you agree to use this application for learning purposes.
              Your data is stored securely and never shared with third parties.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;