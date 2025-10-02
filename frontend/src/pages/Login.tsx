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
  const [googleButtonReady, setGoogleButtonReady] = useState(false);

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
              setGoogleButtonReady(true);
              setError(''); // Clear any previous errors
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
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        {/* Floating card design */}
        <div className="bg-white rounded-2xl shadow-xl p-8 space-y-8">
          {/* Logo and branding */}
          <div className="text-center">
            <div className="mx-auto h-16 w-16 flex items-center justify-center rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 shadow-lg">
              <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h1 className="mt-8 text-3xl font-bold text-gray-900 text-center">
              Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Garudaco</span>
            </h1>
            <p className="mt-4 text-gray-600 text-lg text-center">
              Your ultimate DSA companion
            </p>
            <p className="mt-2 text-gray-500 text-sm text-center">
              Master Data Structures & Algorithms with AI-powered practice
            </p>
          </div>

          {/* Features showcase */}
          <div className="space-y-4 text-center">
            <div className="flex items-center justify-center space-x-3 text-gray-700">
              <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-2">
                <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className="text-sm font-medium">Smart DSA topic recommendations</span>
            </div>
            <div className="flex items-center justify-center space-x-3 text-gray-700">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-2">
                <svg className="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <span className="text-sm font-medium">AI-generated coding challenges</span>
            </div>
            <div className="flex items-center justify-center space-x-3 text-gray-700">
              <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mr-2">
                <svg className="w-4 h-4 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <span className="text-sm font-medium">Track your coding progress</span>
            </div>
          </div>

          {/* Sign-in section */}
          <div className="space-y-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-3 bg-white text-gray-500 font-medium">Sign in to get started</span>
              </div>
            </div>

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div className="flex justify-center">
              {isGoogleLoading ? (
                <div className="flex items-center space-x-3 animate-pulse">
                  <div className="bg-gray-200 h-12 w-80 rounded-lg"></div>
                </div>
              ) : (
                <div id="google-signin-button" className="shadow-lg rounded-lg overflow-hidden"></div>
              )}
            </div>
          </div>

          {/* Security note */}
          <div className="text-center pt-4 border-t border-gray-100">
            <p className="text-xs text-gray-500 leading-relaxed">
              🔒 Secure authentication powered by Google<br/>
              Your DSA progress is encrypted and never shared with third parties
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;