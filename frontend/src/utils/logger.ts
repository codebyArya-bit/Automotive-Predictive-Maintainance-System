import { apiService } from '../services/api';
import { AppError } from '../utils/errorHandler';

export interface LogContext {
  [key: string]: any;
}

export type LogLevel = 'debug' | 'info' | 'warning' | 'error' | 'critical';

const sendToBackend = async (payload: any) => {
  try {
    await apiService.post('/logs/ingest', { logs: [payload] });
  } catch {
    // Swallow logging failures to avoid impacting UX
  }
};

export const trackEvent = async (
  eventType: string,
  message: string,
  context: LogContext = {},
  level: LogLevel = 'info'
) => {
  const entry = {
    timestamp: new Date().toISOString(),
    level,
    event_type: eventType,
    message,
    source: 'frontend',
    context,
  };

  // Console for local debugging
  // eslint-disable-next-line no-console
  console.info('UI Event:', entry);

  // Attempt to persist to backend
  await sendToBackend(entry);
};

export const logApplicationError = async (
  error: AppError | Error,
  context: LogContext = {}
) => {
  const payloadContext: LogContext = {
    name: error.name,
    message: error.message,
    stack: error.stack,
    ...context,
  };

  const entry = {
    timestamp: new Date().toISOString(),
    level: 'error' as LogLevel,
    event_type: 'application_error',
    message: `Application Error: ${JSON.stringify({ message: error.message, name: error.name })}`,
    source: 'frontend',
    context: payloadContext,
  };

  console.error('Application Error:', entry);
  await sendToBackend(entry);
};

export const logWebSocketError = async (message: string, details: LogContext = {}) => {
  const serialized = {
    message,
    name: 'AppError',
    stack: `AppError: ${message}`,
  };

  const entry = {
    timestamp: new Date().toISOString(),
    level: 'error' as LogLevel,
    event_type: 'websocket',
    message: `Application Error: ${JSON.stringify(serialized)}`,
    source: 'frontend',
    context: details,
  };
  console.error('Application Error:', entry);
  await sendToBackend(entry);
};