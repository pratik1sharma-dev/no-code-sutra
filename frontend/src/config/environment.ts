// Environment configuration
export const config = {
  // API Configuration
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  apiTimeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
  
  // Feature Flags
  enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  enableDebugMode: import.meta.env.VITE_ENABLE_DEBUG_MODE === 'true',
  
  // App Configuration
  appName: import.meta.env.VITE_APP_NAME || 'No Code Sutra',
  appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
  
  // Development
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
} as const;

// API endpoints
export const apiEndpoints = {
  health: `${config.apiBaseUrl}/health`,
  generateWorkflow: `${config.apiBaseUrl}/api/workflows/generate`,
  availableAgents: `${config.apiBaseUrl}/api/agents/available`,
} as const; 