import { useState, useEffect, useRef, useCallback } from 'react';
import { logError, AppError } from '../utils/errorHandler';
import { logWebSocketError } from '../utils/logger';

export interface WebSocketOptions {
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onOpen?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
  onError?: (error: Error | AppError | any) => void;
  onMessage?: (data: any) => void;
  protocols?: string | string[];
}

export interface WebSocketState {
  socket: WebSocket | null;
  lastMessage: any;
  readyState: number;
  isConnected: boolean;
  isConnecting: boolean;
  error: Error | null;
  reconnectCount: number;
}

export const useWebSocket = (url: string, options: WebSocketOptions = {}) => {
  const {
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    onOpen,
    onClose,
    onError,
    onMessage,
    protocols,
  } = options;

  const [state, setState] = useState<WebSocketState>({
    socket: null,
    lastMessage: null,
    readyState: WebSocket.CLOSED,
    isConnected: false,
    isConnecting: false,
    error: null,
    reconnectCount: 0,
  });

  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const shouldReconnectRef = useRef(true);
  const urlRef = useRef(url);

  // Update URL ref when URL changes
  useEffect(() => {
    urlRef.current = url;
  }, [url]);

  const connect = useCallback(() => {
    if (state.isConnecting || (state.socket && state.socket.readyState === WebSocket.OPEN)) {
      return;
    }

    setState(prev => ({ ...prev, isConnecting: true, error: null }));

    try {
      const socket = new WebSocket(urlRef.current, protocols);

      socket.onopen = (event) => {
        setState(prev => ({
          ...prev,
          socket,
          readyState: socket.readyState,
          isConnected: true,
          isConnecting: false,
          error: null,
          reconnectCount: 0,
        }));

        if (onOpen) {
          onOpen(event);
        }
      };

      socket.onclose = (event) => {
        setState(prev => ({
          ...prev,
          socket: null,
          readyState: WebSocket.CLOSED,
          isConnected: false,
          isConnecting: false,
        }));

        if (onClose) {
          onClose(event);
        }

        // Attempt to reconnect if not manually closed
        if (shouldReconnectRef.current && event.code !== 1000) {
          setState(prev => {
            if (prev.reconnectCount < maxReconnectAttempts) {
              reconnectTimeoutRef.current = setTimeout(() => {
                connect();
              }, reconnectInterval);

              return {
                ...prev,
                reconnectCount: prev.reconnectCount + 1,
              };
            } else {
              const error = new AppError(
                'WebSocket connection failed after maximum retry attempts',
                'WEBSOCKET_MAX_RETRIES',
                { reconnectCount: prev.reconnectCount }
              );
              logError(error, 'WebSocket');
              logWebSocketError('WebSocket connection failed after maximum retry attempts', {
                reconnectCount: prev.reconnectCount,
                url,
              });
              
              return {
                ...prev,
                error,
              };
            }
          });
        }
      };

      socket.onerror = (event) => {
        const error = new AppError(
          'WebSocket connection error',
          'WEBSOCKET_ERROR',
          { event }
        );

        setState(prev => ({
          ...prev,
          error,
          isConnecting: false,
        }));

        logError(error, 'WebSocket');
        logWebSocketError('WebSocket connection error', { url, event });

        if (onError) {
          onError(error);
        }
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setState(prev => ({
            ...prev,
            lastMessage: data,
          }));

          if (onMessage) {
            onMessage(data);
          }
        } catch (parseError) {
          const error = new AppError(
            'Failed to parse WebSocket message',
            'WEBSOCKET_PARSE_ERROR',
            { originalData: event.data, parseError }
          );
          logError(error, 'WebSocket');
          logWebSocketError('Failed to parse WebSocket message', { url });
        }
      };

      setState(prev => ({ ...prev, socket }));
    } catch (error) {
      const appError = new AppError(
        'Failed to create WebSocket connection',
        'WEBSOCKET_CREATE_ERROR',
        { error }
      );

      setState(prev => ({
        ...prev,
        error: appError,
        isConnecting: false,
      }));

      logError(appError, 'WebSocket');
      logWebSocketError('Failed to create WebSocket connection', { url });
    }
  }, [protocols, onOpen, onClose, onError, onMessage, reconnectInterval, maxReconnectAttempts]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (state.socket) {
      state.socket.close(1000, 'Manual disconnect');
    }

    setState(prev => ({
      ...prev,
      socket: null,
      readyState: WebSocket.CLOSED,
      isConnected: false,
      isConnecting: false,
      reconnectCount: 0,
    }));
  }, [state.socket]);

  const sendMessage = useCallback((data: any) => {
    if (state.socket && state.socket.readyState === WebSocket.OPEN) {
      try {
        const message = typeof data === 'string' ? data : JSON.stringify(data);
        state.socket.send(message);
        return true;
      } catch (error) {
        const appError = new AppError(
          'Failed to send WebSocket message',
          'WEBSOCKET_SEND_ERROR',
          { data, error }
        );
        logError(appError, 'WebSocket');
        logWebSocketError('Failed to send WebSocket message', { url });
        return false;
      }
    } else {
      const error = new AppError(
        'WebSocket is not connected',
        'WEBSOCKET_NOT_CONNECTED',
        { readyState: state.socket?.readyState }
      );
      logError(error, 'WebSocket');
      logWebSocketError('WebSocket is not connected', { url });
      return false;
    }
  }, [state.socket]);

  const reconnect = useCallback(() => {
    disconnect();
    shouldReconnectRef.current = true;
    setState(prev => ({ ...prev, reconnectCount: 0 }));
    setTimeout(connect, 100);
  }, [disconnect, connect]);

  // Auto-connect on mount
  useEffect(() => {
    shouldReconnectRef.current = true;
    connect();

    return () => {
      shouldReconnectRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (state.socket) {
        state.socket.close(1000, 'Component unmount');
      }
    };
  }, [url]); // Only reconnect when URL changes

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    ...state,
    connect,
    disconnect,
    reconnect,
    sendMessage,
  };
};

export default useWebSocket;