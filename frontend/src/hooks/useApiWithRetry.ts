import { useState, useCallback, useEffect } from 'react';
import { retryWithBackoff, logError } from '../utils/errorHandler';

interface UseApiWithRetryOptions {
  maxRetries?: number;
  baseDelay?: number;
  showToast?: boolean;
}

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export const useApiWithRetry = <T = any>(
  options: UseApiWithRetryOptions = {}
) => {
  const { maxRetries = 3, baseDelay = 1000, showToast = true } = options;
  
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async (
    apiCall: () => Promise<T>,
    context?: string
  ): Promise<T | null> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const result = await retryWithBackoff(
        apiCall,
        maxRetries,
        baseDelay,
        context
      );
      
      setState({
        data: result,
        loading: false,
        error: null,
      });
      
      return result;
    } catch (error) {
      const appError = error as Error;
      setState({
        data: null,
        loading: false,
        error: appError,
      });
      
      if (showToast) {
        logError(appError, context);
      }
      
      return null;
    }
  }, [maxRetries, baseDelay, showToast]);

  const executeWithFallback = useCallback(async <F>(
    apiCall: () => Promise<T>,
    fallbackData: F,
    context?: string
  ): Promise<T | F> => {
    const result = await execute(apiCall, context);
    return result !== null ? result : fallbackData;
  }, [execute]);

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
    });
  }, []);

  return {
    ...state,
    execute,
    executeWithFallback,
    reset,
  };
};

export const useApiCall = <T = any>(
  apiCall: () => Promise<T>,
  options: UseApiWithRetryOptions & { 
    immediate?: boolean;
    dependencies?: any[];
  } = {}
) => {
  const { immediate = false, dependencies = [], ...retryOptions } = options;
  const { execute, ...state } = useApiWithRetry<T>(retryOptions);

  const call = useCallback(() => {
    return execute(apiCall, apiCall.name || 'API Call');
  }, [execute, apiCall]);

  // Auto-execute on mount or dependency change if immediate is true
  useEffect(() => {
    if (immediate) {
      call();
    }
  }, [immediate, call, ...dependencies]);

  return {
    ...state,
    call,
    refetch: call,
  };
};

// Specialized hooks for common patterns
export const useApiData = <T = any>(
  apiCall: () => Promise<T>,
  fallbackData: T,
  options: UseApiWithRetryOptions = {}
) => {
  const { executeWithFallback, loading, error } = useApiWithRetry<T>(options);
  
  const [data, setData] = useState<T>(fallbackData);

  const fetchData = useCallback(async () => {
    const result = await executeWithFallback(
      apiCall,
      fallbackData,
      apiCall.name || 'Fetch Data'
    );
    setData(result);
    return result;
  }, [executeWithFallback, apiCall, fallbackData]);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
    setData,
  };
};

export const useApiMutation = <T = any, P = any>(
  mutationFn: (params: P) => Promise<T>,
  options: UseApiWithRetryOptions & {
    onSuccess?: (data: T) => void;
    onError?: (error: Error) => void;
  } = {}
) => {
  const { onSuccess, onError, ...retryOptions } = options;
  const { execute, loading, error } = useApiWithRetry<T>(retryOptions);

  const mutate = useCallback(async (params: P): Promise<T | null> => {
    const result = await execute(
      () => mutationFn(params),
      mutationFn.name || 'Mutation'
    );

    if (result !== null && onSuccess) {
      onSuccess(result);
    } else if (result === null && error && onError) {
      onError(error);
    }

    return result;
  }, [execute, mutationFn, onSuccess, onError, error]);

  return {
    mutate,
    loading,
    error,
  };
};