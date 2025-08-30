/**
 * API configuration for different environments
 */

// Environment variables with fallbacks
const API_BASE_URL = (import.meta as any).env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt((import.meta as any).env.VITE_API_TIMEOUT || '30000');
const ENVIRONMENT = (import.meta as any).env.VITE_ENVIRONMENT || 'development';

// Feature flags
const ENABLE_AUTH = (import.meta as any).env.VITE_ENABLE_AUTH === 'true';
const ENABLE_OAUTH = (import.meta as any).env.VITE_ENABLE_OAUTH === 'true';
const ENABLE_DEBUG_LOGS = (import.meta as any).env.VITE_ENABLE_DEBUG_LOGS === 'true';

// OAuth redirect URIs
const INSTAGRAM_REDIRECT_URI = (import.meta as any).env.VITE_INSTAGRAM_REDIRECT_URI || 
  `${window.location.origin}/auth/instagram/callback`;
const CANVA_REDIRECT_URI = (import.meta as any).env.VITE_CANVA_REDIRECT_URI || 
  `${window.location.origin}/auth/canva/callback`;

// App configuration
const APP_NAME = (import.meta as any).env.VITE_APP_NAME || 'No Code Sutra';
const APP_VERSION = (import.meta as any).env.VITE_APP_VERSION || '1.0.0';

export const config = {
  api: {
    baseUrl: API_BASE_URL,
    timeout: API_TIMEOUT,
    endpoints: {
      // Workflow endpoints
      generateWorkflow: '/api/workflows/generate',
      executeWorkflow: '/api/workflows/execute',
      saveWorkflow: '/api/workflows/save',
      listWorkflows: '/api/workflows',
      getWorkflow: '/api/workflows',
      deleteWorkflow: '/api/workflows',
      
      // Node endpoints
      executeNode: '/api/nodes/execute',
      getNodeRegistry: '/api/nodes/registry',
      
      // Auth endpoints
      login: '/api/auth/login',
      generateApiKey: '/api/auth/generate-api-key',
      demoCredentials: '/api/auth/demo-credentials',
      
      // Instagram OAuth
      instagramAuthUrl: '/api/auth/instagram/url',
      instagramCallback: '/api/auth/instagram/callback',
      instagramValidate: '/api/auth/instagram/validate',
      instagramCredentials: '/api/auth/instagram/credentials',
      
      // Canva OAuth
      canvaAuthUrl: '/api/auth/canva/url',
      canvaCallback: '/api/auth/canva/callback',
      canvaTemplates: '/api/canva/templates',
      
      // Health check
      health: '/health'
    }
  },
  
  oauth: {
    instagram: {
      redirectUri: INSTAGRAM_REDIRECT_URI
    },
    canva: {
      redirectUri: CANVA_REDIRECT_URI
    }
  },
  
  features: {
    auth: ENABLE_AUTH,
    oauth: ENABLE_OAUTH,
    debugLogs: ENABLE_DEBUG_LOGS
  },
  
  app: {
    name: APP_NAME,
    version: APP_VERSION,
    environment: ENVIRONMENT
  },
  
  // Helper methods
  getApiUrl: (endpoint: string) => `${API_BASE_URL}${endpoint}`,
  
  isProduction: () => ENVIRONMENT === 'production',
  isDevelopment: () => ENVIRONMENT === 'development',
  
  log: (...args: any[]) => {
    if (ENABLE_DEBUG_LOGS) {
      console.log('[API Config]', ...args);
    }
  }
};

export default config;
