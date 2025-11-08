import { toast } from 'react-hot-toast';

export interface ErrorInfo {
  message: string;
  code?: string;
  details?: any;
  timestamp: Date;
}

export class AppError extends Error {
  public code?: string;
  public details?: any;
  public timestamp: Date;

  constructor(message: string, code?: string, details?: any) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.details = details;
    this.timestamp = new Date();
  }
}

export class NetworkError extends AppError {
  constructor(message: string = 'Network connection failed', details?: any) {
    super(message, 'NETWORK_ERROR', details);
    this.name = 'NetworkError';
  }
}

export class ValidationError extends AppError {
  constructor(message: string = 'Validation failed', details?: any) {
    super(message, 'VALIDATION_ERROR', details);
    this.name = 'ValidationError';
  }
}

export class AuthenticationError extends AppError {
  constructor(message: string = 'Authentication failed', details?: any) {
    super(message, 'AUTH_ERROR', details);
    this.name = 'AuthenticationError';
  }
}

export class ServerError extends AppError {
  constructor(message: string = 'Server error occurred', details?: any) {
    super(message, 'SERVER_ERROR', details);
    this.name = 'ServerError';
  }
}

export const handleApiError = (error: any): AppError => {
  if (error.response) {
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return new ValidationError(data.message || 'Invalid request data', data);
      case 401:
        return new AuthenticationError(data.message || 'Authentication required', data);
      case 403:
        return new AuthenticationError(data.message || 'Access forbidden', data);
      case 404:
        return new AppError(data.message || 'Resource not found', 'NOT_FOUND', data);
      case 429:
        return new AppError(data.message || 'Too many requests', 'RATE_LIMIT', data);
      case 500:
      case 502:
      case 503:
      case 504:
        return new ServerError(data.message || 'Server error occurred', data);
      default:
        return new AppError(data.message || 'An unexpected error occurred', 'UNKNOWN', data);
    }
  } else if (error.request) {
    // Likely network/CORS failure. Capture contextual hints to aid debugging.
    const isAxiosNetworkErr = error.code === 'ERR_NETWORK' || /Network Error/i.test(error.message || '');
    const origin = typeof window !== 'undefined' ? window.location.origin : undefined;
    const cfg = error.config || {};
    const baseURL = cfg.baseURL || '';
    const url = cfg.url || '';
    const targetUrl = `${baseURL}${url}`;
    const method = (cfg.method || 'GET').toUpperCase();
    const headers = cfg.headers || {};
    const withCredentials = !!cfg.withCredentials;
    const hasAuthHeader = !!(headers['Authorization'] || headers['authorization']);
    const requestedHeaderKeys = Object.keys(headers || {});

    const details = {
      isAxiosNetworkErr,
      likelyCorsBlocked: isAxiosNetworkErr && !!origin,
      origin,
      targetUrl,
      method,
      withCredentials,
      hasAuthHeader,
      requestedHeaderKeys,
      online: typeof navigator !== 'undefined' ? navigator.onLine : undefined,
    };

    return new NetworkError('Network connection failed - possible CORS or connectivity issue', details);
  } else {
    return new AppError(error.message || 'An unexpected error occurred');
  }
};

export const showErrorToast = (error: AppError | Error) => {
  const message = error instanceof AppError ? error.message : 'An unexpected error occurred';
  toast.error(message, {
    duration: 5000,
    position: 'top-right',
  });
};

export const logError = (error: AppError | Error, context?: string) => {
  const errorInfo = {
    message: error.message,
    name: error.name,
    stack: error.stack,
    context,
    timestamp: new Date().toISOString(),
    ...(error instanceof AppError && {
      code: error.code,
      details: error.details,
    }),
  };

  console.error('Application Error:', errorInfo);
  
  // In production, you might want to send this to a logging service
  if (process.env.NODE_ENV === 'production') {
    // Send to logging service (e.g., Sentry, LogRocket, etc.)
    // logToService(errorInfo);
  }
};

export const withErrorHandling = <T extends any[], R>(
  fn: (...args: T) => Promise<R>,
  context?: string
) => {
  return async (...args: T): Promise<R | null> => {
    try {
      return await fn(...args);
    } catch (error) {
      const appError = error instanceof AppError ? error : handleApiError(error);
      logError(appError, context);
      showErrorToast(appError);
      return null;
    }
  };
};

export const retryWithBackoff = async <T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000,
  context?: string
): Promise<T> => {
  let lastError: Error;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      
      if (attempt === maxRetries) {
        const appError = error instanceof AppError ? error : handleApiError(error);
        logError(appError, `${context} - Final attempt failed`);
        throw appError;
      }

      // Exponential backoff with jitter
      const delay = baseDelay * Math.pow(2, attempt - 1) + Math.random() * 1000;
      console.warn(`Attempt ${attempt} failed, retrying in ${delay}ms...`, error);
      
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError!;
};

export const isNetworkError = (error: any): boolean => {
  return error instanceof NetworkError || 
         error.code === 'NETWORK_ERROR' ||
         error.message?.includes('Network Error') ||
         error.message?.includes('fetch');
};

export const isRetryableError = (error: any): boolean => {
  if (error instanceof NetworkError) return true;
  if (error instanceof ServerError) return true;
  if (error.response?.status >= 500) return true;
  if (error.response?.status === 429) return true; // Rate limit
  return false;
};