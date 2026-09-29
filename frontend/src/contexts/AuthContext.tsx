import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'customer' | 'service_staff' | 'manufacturing_engineer' | 'system_admin' | 'fleet_manager';
  phone?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

// Provide a safe default so hooks won’t throw during edge cases (e.g., HMR, split roots)
const defaultAuthContext: AuthContextType = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  login: async (email: string, password: string) => {
    // Fallback login outside provider: attempt API call and persist to localStorage
    try {
      const response = await apiService.login(email, password);
      localStorage.setItem('auth_token', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));
      // eslint-disable-next-line no-console
      console.warn('[AuthContext] Fallback login used without provider. State not reactive.');
    } catch (err) {
      throw err;
    }
  },
  logout: async () => {
    try {
      await apiService.logout();
    } catch {
      // ignore
    } finally {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      // eslint-disable-next-line no-console
      console.warn('[AuthContext] Fallback logout used without provider.');
    }
  },
  checkAuth: async () => {
    // Non-reactive fallback: best-effort verification
    const token = localStorage.getItem('auth_token');
    const userStr = localStorage.getItem('user');
    if (token && userStr) {
      try {
        await apiService.getCurrentUser();
      } catch {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
      }
    }
    // eslint-disable-next-line no-console
    console.warn('[AuthContext] Fallback checkAuth used without provider.');
  }
};

const AuthContext = createContext<AuthContextType>(defaultAuthContext);

export const useAuth = () => {
  const context = useContext(AuthContext);
  // Log if the fallback is being used (no provider in tree)
  if (context === defaultAuthContext) {
    // eslint-disable-next-line no-console
    console.warn('[AuthContext] useAuth accessed without AuthProvider. Using fallback context.');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is already authenticated on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      setIsLoading(true);
      const storedToken = localStorage.getItem('auth_token');
      const storedUser = localStorage.getItem('user');

      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));

        // Verify token is still valid by fetching current user
        try {
          const currentUser = await apiService.getCurrentUser();
          if (!currentUser?.user) {
            throw new Error('Invalid /auth/me response');
          }
          setUser(currentUser.user);
          localStorage.setItem('user', JSON.stringify(currentUser.user));
        } catch (error) {
          // Token expired or invalid, clear auth
          console.error('Token verification failed:', error);
          await logout();
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      await logout();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const response = await apiService.login(email, password);

      setToken(response.token);
      setUser(response.user);

      // Store in localStorage
      localStorage.setItem('auth_token', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);

    // Clear browser auth first so logout always succeeds locally, even when
    // the backend is unavailable or the JWT has already expired.
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');

    try {
      await apiService.logout();
    } catch (error) {
      // Stateless JWT logout is complete once local credentials are removed.
      console.warn('Logout API acknowledgement failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!user && !!token,
    isLoading,
    login,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Protected Route Component
interface ProtectedRouteProps {
  children: ReactNode;
  allowedRoles?: string[];
  redirectTo?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles = [],
  redirectTo = '/login'
}) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        navigate(redirectTo);
      } else if (allowedRoles.length > 0 && user && !allowedRoles.includes(user.role)) {
        // User doesn't have required role, redirect to their default dashboard
        navigate(getRoleBasedRoute(user.role));
      }
    }
  }, [isAuthenticated, isLoading, user, navigate, allowedRoles, redirectTo]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-300 text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  if (allowedRoles.length > 0 && user && !allowedRoles.includes(user.role)) {
    return null;
  }

  return <>{children}</>;
};

// Helper function to get role-based default route
export const getRoleBasedRoute = (role: string): string => {
  switch (role) {
    case 'customer':
      return '/customer-dashboard';
    case 'service_staff':
      return '/demand-forecast';
    case 'manufacturing_engineer':
      return '/manufacturing-dashboard';
    case 'system_admin':
      return '/dashboard';
    case 'fleet_manager':
      return '/analytics';
    default:
      return '/';
  }
};
