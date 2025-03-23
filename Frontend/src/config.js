/**
 * Configuration for the TestForge application
 */

// API URL detection with improved fallbacks
const getBaseApiUrl = () => {
  const hostname = window.location.hostname;
  const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1';
  
  // Create a collection of possible backend URLs to try
  const possibleUrls = [];
  
  // Current hostname IP address from network logs
  const networkIp = '172.20.10.5';
  
  if (isLocalhost) {
    // Development: Try multiple connection options
    console.log('[Config] Development mode detected, configuring multiple fallback options');
    
    // Regular localhost options (most common)
    possibleUrls.push('http://localhost:5000');
    possibleUrls.push('http://127.0.0.1:5000');
    
    // Try the network IP address that appears in logs
    possibleUrls.push(`http://${networkIp}:5000`);
    
    // Try direct https version for cases where the server might be secured
    possibleUrls.push('https://localhost:5000');
    
    // Try alternate ports in case the default port is blocked
    possibleUrls.push('http://localhost:8000');
    possibleUrls.push('http://localhost:3001/api');
    
    // Try direct access to Flask API as a last resort
    possibleUrls.push('/api');
    
    // Try the same domain access (when frontend and backend share the domain)
    possibleUrls.push(`${window.location.origin}/api`);
  } else {
    // Production: Handle cases where backend might be on same domain or separate
    console.log('[Config] Production mode detected');
    possibleUrls.push(`${window.location.origin}/api`); // Same origin (most common for production)
    possibleUrls.push('/api'); // Root-relative path
    possibleUrls.push('https://api.testforge.app'); // Dedicated API domain (if configured)
  }
  
  console.log('[Config] Possible backend URLs to try:', possibleUrls);
  return { possibleUrls, isLocalhost };
};

// Get configuration details
const { possibleUrls, isLocalhost } = getBaseApiUrl();

// Debugging output
console.log('[Config] Environment:', process.env.NODE_ENV);
console.log('[Config] Current URL:', window.location.href);
console.log('[Config] Hostname:', window.location.hostname);
console.log('[Config] Current Port:', window.location.port);
console.log('[Config] Is localhost:', isLocalhost);

// Export configuration
export const API_CONFIG = {
  isLocalhost,
  possibleUrls,
  primaryApiUrl: possibleUrls[0], // Default to first URL
  timeout: 60000, // 60 seconds
};

// Default API URL (can be overridden via health checks)
export const API_URL = API_CONFIG.primaryApiUrl;

console.log('[Config] Using primary API URL:', API_URL);

// Generate health check endpoints for each possible URL
export const ALL_HEALTH_ENDPOINTS = possibleUrls.map(url => 
  url.endsWith('/api') ? `${url}/health` : `${url}/api/health`
);

// API endpoints - note we'll use more dynamic creation in the API service
export const API_ENDPOINTS = {
  HEALTH: `${API_URL}/api/health`,
  TEST_CUSTOM: `${API_URL}/api/test-custom`,
  TEST_GITHUB: `${API_URL}/api/test-github`,
  RUN_TESTS: `${API_URL}/api/run-tests`,
  GET_RESULTS: (sessionId) => `${API_URL}/api/results/${sessionId}`,
};

// Log all endpoints
console.log('[Config] API Endpoints:', Object.keys(API_ENDPOINTS).reduce((acc, key) => {
  acc[key] = typeof API_ENDPOINTS[key] === 'function' 
    ? API_ENDPOINTS[key]('example-id') 
    : API_ENDPOINTS[key];
  return acc;
}, {}));

console.log('[Config] All health endpoints to try:', ALL_HEALTH_ENDPOINTS);

// Default headers for API requests
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
};

// API request timeout in milliseconds (60 seconds)
export const REQUEST_TIMEOUT = 60000; 