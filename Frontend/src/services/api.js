import { API_ENDPOINTS, DEFAULT_HEADERS, REQUEST_TIMEOUT, ALL_HEALTH_ENDPOINTS, API_URL } from '../config';

/**
 * API Service to handle communication with the TestForge backend
 */
class ApiService {
  constructor() {
    this.baseUrl = API_URL;
    this.endpoints = { ...API_ENDPOINTS };
    this.workingUrl = null;
    this.lastSuccessfulEndpoint = null;
    this.failedEndpoints = new Set();
    this.endpointTriesCount = {};
    this.healthEndpoints = [...ALL_HEALTH_ENDPOINTS];
    
    console.log('[API] Initialized with base URL:', this.baseUrl);
    console.log('[API] Available health endpoints:', this.healthEndpoints);
  }
  
  /**
   * Find a working API endpoint by trying all available options
   * @returns {Promise<string>} The first working endpoint
   */
  async findWorkingEndpoint() {
    console.log('[API] Searching for a working endpoint...');
    
    // If we already found a working URL recently, try it first
    if (this.workingUrl) {
      try {
        const healthEndpoint = this.workingUrl.endsWith('/api') 
          ? `${this.workingUrl}/health` 
          : `${this.workingUrl}/api/health`;
          
        console.log(`[API] Trying previously working endpoint: ${healthEndpoint}`);
        
        const response = await fetch(healthEndpoint, {
          method: 'GET',
          headers: DEFAULT_HEADERS,
          mode: 'cors',
          credentials: 'omit',
          cache: 'no-cache',
        });
        
        if (response.ok) {
          console.log(`[API] Previously working endpoint is still working: ${this.workingUrl}`);
          return this.workingUrl;
        } else {
          console.log(`[API] Previously working endpoint is no longer working: ${this.workingUrl}`);
          this.workingUrl = null;
        }
      } catch (error) {
        console.log(`[API] Previously working endpoint failed: ${this.workingUrl}`, error.message);
        this.workingUrl = null;
      }
    }
    
    // Try each health endpoint until one works
    for (const endpoint of this.healthEndpoints) {
      // Skip endpoints we've already tried too many times
      if (this.endpointTriesCount[endpoint] && this.endpointTriesCount[endpoint] > 3) {
        console.log(`[API] Skipping repeatedly failed endpoint: ${endpoint}`);
        continue;
      }
      
      // Increment the tries counter
      this.endpointTriesCount[endpoint] = (this.endpointTriesCount[endpoint] || 0) + 1;
      
      try {
        console.log(`[API] Trying endpoint: ${endpoint}`);
        
        const response = await fetch(endpoint, {
          method: 'GET',
          headers: DEFAULT_HEADERS,
          mode: 'cors',
          credentials: 'omit',
          cache: 'no-cache',
          timeout: 5000, // Short timeout for health checks
        });
        
        if (response.ok) {
          const data = await response.json();
          console.log(`[API] Found working endpoint: ${endpoint}`, data);
          
          // Extract base URL from endpoint
          const baseUrl = endpoint.replace(/\/api\/health$/, '').replace(/\/health$/, '');
          this.workingUrl = baseUrl;
          this.lastSuccessfulEndpoint = endpoint;
          
          // Update the API endpoints with the new base URL
          this.updateBaseUrl(baseUrl);
          
          return baseUrl;
        } else {
          console.log(`[API] Endpoint returned non-OK status: ${endpoint}`, response.status);
          this.failedEndpoints.add(endpoint);
        }
      } catch (error) {
        console.error(`[API] Failed to connect to endpoint: ${endpoint}`, error.message);
        this.failedEndpoints.add(endpoint);
      }
    }
    
    console.error('[API] All endpoints failed. No working connection found.');
    throw new Error('Unable to connect to any API endpoint. Please check if the server is running.');
  }
  
  /**
   * Update the base URL for all API endpoints
   * @param {string} newBaseUrl - The new base URL to use
   */
  updateBaseUrl(newBaseUrl) {
    if (!newBaseUrl) return;
    
    this.baseUrl = newBaseUrl;
    console.log('[API] Updating endpoints to use base URL:', newBaseUrl);
    
    // Update all endpoints with the new base URL
    const apiPath = newBaseUrl.endsWith('/api') ? '' : '/api';
    
    this.endpoints = {
      HEALTH: `${newBaseUrl}${apiPath}/health`,
      TEST_CUSTOM: `${newBaseUrl}${apiPath}/test-custom`,
      TEST_GITHUB: `${newBaseUrl}${apiPath}/test-github`,
      RUN_TESTS: `${newBaseUrl}${apiPath}/run-tests`,
      GET_RESULTS: (sessionId) => `${newBaseUrl}${apiPath}/results/${sessionId}`,
    };
    
    console.log('[API] Updated endpoints:', this.endpoints);
  }
  
  /**
   * Get the current endpoints
   * @returns {Object} The current API endpoints
   */
  getEndpoints() {
    return this.endpoints;
  }
  
  /**
   * Generic method to fetch data from the API
   * @param {string} url - API endpoint URL
   * @param {Object} options - Fetch options
   * @returns {Promise<Object>} - Response data
   */
  async fetchApi(url, options = {}) {
    try {
      console.log(`[API] Making API request to: ${url}`, options);
      
      // If we don't have a working URL yet or we get a URL that doesn't match
      // our current working URL, find a working endpoint first
      if (!this.workingUrl || 
         (url.indexOf(this.workingUrl) !== 0 && !url.startsWith('/api'))) {
        console.log('[API] No working URL or URL mismatch, finding working endpoint first');
        await this.findWorkingEndpoint();
        
        // Rewrite the URL using the working base URL
        const urlPath = new URL(url, window.location.origin).pathname;
        const apiPath = this.workingUrl.endsWith('/api') ? '' : '/api';
        url = `${this.workingUrl}${apiPath}${urlPath.replace(/^\/api/, '')}`;
        
        console.log(`[API] Rewritten URL to use working endpoint: ${url}`);
      }
      
      const controller = new AbortController();
      const signal = controller.signal;
      
      // Set timeout to abort request if it takes too long
      const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);
      
      // Merge default options with provided options
      const mergedOptions = {
        headers: DEFAULT_HEADERS,
        signal,
        mode: 'cors',
        credentials: 'omit', // Don't send cookies to avoid CORS issues
        ...options,
      };
      
      console.log(`[API] Fetch starting with options:`, mergedOptions);
      
      try {
        const response = await fetch(url, mergedOptions);
        console.log(`[API] Response received:`, { 
          status: response.status, 
          statusText: response.statusText,
          headers: [...response.headers.entries()].reduce((obj, [key, val]) => ({ ...obj, [key]: val }), {})
        });
        
        clearTimeout(timeoutId);
        
        // Try to parse as JSON
        let data;
        try {
          data = await response.json();
          console.log(`[API] Response data:`, data);
        } catch (e) {
          // If not JSON, get the text
          const text = await response.text();
          console.error(`[API] Failed to parse response as JSON:`, text);
          throw new Error(`Failed to parse response as JSON: ${text}`);
        }
        
        if (!response.ok) {
          const errorMessage = data.error || `Error: ${response.status} - ${response.statusText}`;
          console.error(`[API] Request error: ${errorMessage}`, data);
          throw new Error(errorMessage);
        }
        
        // If we got here, the endpoint is working
        if (url.includes('/api/health')) {
          const baseUrl = url.replace(/\/api\/health$/, '');
          this.workingUrl = baseUrl;
          console.log(`[API] Updated working URL from successful request: ${baseUrl}`);
        }
        
        return data;
      } catch (fetchError) {
        clearTimeout(timeoutId);
        
        // Handle network errors
        if (fetchError.name === 'TypeError' && fetchError.message === 'Failed to fetch') {
          console.error('[API] Network error - possible CORS issue or server is down');
          
          // Try to find a different working endpoint
          this.workingUrl = null;
          
          throw new Error('Cannot connect to the server. The application is trying alternative connection methods. Please check if the backend service is running.');
        }
        
        throw fetchError;
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.error(`[API] Request timeout for ${url}`);
        throw new Error('Request timeout. The server took too long to respond. Please try again or try with simpler code.');
      }
      console.error(`[API] Request failed for ${url}:`, error);
      throw error;
    }
  }
  
  /**
   * Check if the API is healthy - now tries multiple endpoints
   * @returns {Promise<Object>} Health status
   */
  async checkHealth() {
    // First, try to find a working endpoint
    try {
      const workingBaseUrl = await this.findWorkingEndpoint();
      
      // Now use the working endpoint to get the health status
      const apiPath = workingBaseUrl.endsWith('/api') ? '' : '/api';
      const healthEndpoint = `${workingBaseUrl}${apiPath}/health`;
      
      console.log('[API] Checking API health at:', healthEndpoint);
      
      const result = await this.fetchApi(healthEndpoint, {
        // Use simpler options for health check to avoid CORS issues
        credentials: 'omit',
        cache: 'no-cache',
      });
      
      console.log('[API] Health check successful:', result);
      return {
        ...result,
        _endpoint: healthEndpoint, // Include the endpoint for debugging
      };
    } catch (error) {
      console.error('[API] Health check failed for all endpoints:', error.message);
      throw error;
    }
  }
  
  /**
   * Run a demo test
   * @returns {Promise<Object>} Test results
   */
  runDemoTest() {
    return this.fetchApi(this.endpoints.RUN_TESTS);
  }
  
  /**
   * Test custom code
   * @param {Object} data - Request data
   * @param {string} data.code - Python code to test
   * @param {string} [data.custom_tests] - Custom test code
   * @param {boolean} [data.generate_ai_tests] - Whether to generate AI tests
   * @returns {Promise<Object>} Test results
   */
  testCustomCode(data) {
    console.log('Testing custom code:', data);
    return this.fetchApi(this.endpoints.TEST_CUSTOM, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
  
  /**
   * Test code from a GitHub repository
   * @param {Object} data - Request data
   * @param {string} data.repo_url - GitHub repository URL
   * @param {string} [data.target_file] - Target file path
   * @param {string} [data.custom_tests] - Custom test code
   * @param {boolean} [data.generate_ai_tests] - Whether to generate AI tests
   * @returns {Promise<Object>} Test results
   */
  testGithubRepo(data) {
    console.log('Testing GitHub repo:', data);
    return this.fetchApi(this.endpoints.TEST_GITHUB, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
  
  /**
   * Get results from a previous session
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Test results
   */
  getResults(sessionId) {
    return this.fetchApi(this.endpoints.GET_RESULTS(sessionId));
  }
}

// Export a singleton instance
export default new ApiService(); 