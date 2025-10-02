import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService, User, Profile } from '../services/auth';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (googleToken: string) => Promise<void>;
  logout: () => Promise<void>;
  getProfile: () => Promise<Profile>;
  updateProfile: (profile: Profile) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          const isValid = await authService.verifyToken();
          if (isValid) {
            setUser(authService.getUser());
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (googleToken: string) => {
    setIsLoading(true);
    try {
      const { user } = await authService.loginWithGoogle(googleToken);
      setUser(user);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await authService.logout();
      setUser(null);
      
      // Reset Google Sign-In state if available
      if (window.google && window.google.accounts) {
        window.google.accounts.id.disableAutoSelect();
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getProfile = async (): Promise<Profile> => {
    return await authService.getProfile();
  };

  const updateProfile = async (profile: Profile): Promise<void> => {
    await authService.updateProfile(profile);
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    getProfile,
    updateProfile
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;