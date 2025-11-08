/**
 * Application Configuration
 * Centralized configuration using environment variables
 */

export interface AppConfig {
  // API Configuration
  apiBaseUrl: string;
  wsUrl: string;

  // Environment
  environment: 'development' | 'staging' | 'production';
  isDevelopment: boolean;
  isProduction: boolean;

  // Feature Flags
  enableAnalytics: boolean;
  enableDebug: boolean;
  enableWebSockets: boolean;

  // Refresh Intervals (in milliseconds)
  dataRefreshInterval: number;
  metricsRefreshInterval: number;

  // Analytics
  googleAnalyticsId?: string;
  sentryDsn?: string;
}

// Load configuration from environment variables
const loadConfig = (): AppConfig => {
  const environment = (import.meta.env.VITE_ENVIRONMENT || 'development') as AppConfig['environment'];

  return {
    // API Configuration
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',

    // Environment
    environment,
    isDevelopment: environment === 'development',
    isProduction: environment === 'production',

    // Feature Flags
    enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
    enableDebug: import.meta.env.VITE_ENABLE_DEBUG === 'true',
    enableWebSockets: import.meta.env.VITE_ENABLE_WEBSOCKETS !== 'false', // Default true

    // Refresh Intervals
    dataRefreshInterval: Number(import.meta.env.VITE_DATA_REFRESH_INTERVAL) || 30000,
    metricsRefreshInterval: Number(import.meta.env.VITE_METRICS_REFRESH_INTERVAL) || 5000,

    // Analytics
    googleAnalyticsId: import.meta.env.VITE_GOOGLE_ANALYTICS_ID,
    sentryDsn: import.meta.env.VITE_SENTRY_DSN,
  };
};

// Export singleton config instance
export const config: AppConfig = loadConfig();

// Log configuration in development
if (config.enableDebug) {
  console.log('App Configuration:', {
    ...config,
    // Hide sensitive data
    googleAnalyticsId: config.googleAnalyticsId ? '***' : undefined,
    sentryDsn: config.sentryDsn ? '***' : undefined,
  });
}

export default config;
