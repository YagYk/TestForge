import { useState, useCallback, useEffect, useRef } from 'react';
import apiService from '../services/api';
import { API_URL, ALL_HEALTH_ENDPOINTS, API_CONFIG } from '../config';

/**
 * Custom hook for making API calls with loading and error states
 * @returns {Object} Hook methods and state
 */
const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [connected, setConnected] = useState(false);
  const [activeEndpoint, setActiveEndpoint] = useState(API_URL);
  const connectionAttemptRef = useRef(0);
  const reconnectTimerRef = useRef(null);
  const lastCheckTimeRef = useRef(Date.now());
  
  // Track debugging information
  const [apiDebugInfo, setApiDebugInfo] = useState({
    lastChecked: null,
    connectionAttempts: 0,
    failedAttempts: 0,
    lastErrorMessage: null,
    lastErrorStack: null,
    activeEndpoint: activeEndpoint,
    apiUrl: API_URL,
    possibleEndpoints: ALL_HEALTH_ENDPOINTS,
    restartAttempts: 0,
    browserInfo: {
      userAgent: navigator.userAgent,
      language: navigator.language,
      onLine: navigator.onLine
    }
  });
  
  /**
   * Update a specific field in the debug info
   */
  const updateDebugInfo = useCallback((updates) => {
    setApiDebugInfo(prev => ({
      ...prev,
      ...updates,
      activeEndpoint: activeEndpoint,
      browserInfo: {
        ...prev.browserInfo,
        onLine: navigator.onLine
      }
    }));
  }, [activeEndpoint]);
  
  /**
   * Set up automatic reconnection attempts when disconnected
   */
  useEffect(() => {
    // Only attempt reconnection if we're disconnected and online
    if (!connected && navigator.onLine) {
      console.log('[useApi] Setting up reconnection timer');
      
      // Clear any existing timer
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      
      // Set up a timer that increases delay with each failed attempt
      const attemptCount = connectionAttemptRef.current;
      const baseDelay = 5000; // 5 seconds base
      const maxDelay = 30000; // 30 seconds max
      
      // Calculate exponential backoff with a cap
      const delay = Math.min(baseDelay * Math.pow(1.5, Math.min(attemptCount, 5)), maxDelay);
      
      console.log(`[useApi] Will attempt reconnection in ${delay/1000} seconds (attempt #${attemptCount + 1})`);
      
      reconnectTimerRef.current = setTimeout(() => {
        console.log(`[useApi] Attempting reconnection #${attemptCount + 1}`);
        connectionAttemptRef.current++;
        updateDebugInfo({ 
          connectionAttempts: connectionAttemptRef.current,
          restartAttempts: connectionAttemptRef.current
        });
        
        // Try to reconnect
        checkHealth()
          .then(() => {
            console.log('[useApi] Reconnection successful');
            // Reset attempt counter on success
            connectionAttemptRef.current = 0;
          })
          .catch(err => {
            console.error('[useApi] Reconnection failed:', err.message);
          });
      }, delay);
      
      return () => {
        if (reconnectTimerRef.current) {
          clearTimeout(reconnectTimerRef.current);
        }
      };
    }
    
    // If we're connected or offline, clear any reconnection timer
    if (connected || !navigator.onLine) {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    }
  }, [connected, updateDebugInfo]);
  
  // Monitor online/offline status to trigger reconnection attempts
  useEffect(() => {
    const handleOnline = () => {
      console.log('[useApi] Browser went online, triggering health check');
      updateDebugInfo({ 
        lastChecked: new Date().toISOString(),
        connectionAttempts: connectionAttemptRef.current + 1
      });
      
      // Wait a moment for network to stabilize
      setTimeout(() => {
        checkHealth().catch(err => {
          console.error('[useApi] Online health check failed:', err.message);
        });
      }, 2000);
    };
    
    const handleOffline = () => {
      console.log('[useApi] Browser went offline');
      setConnected(false);
      updateDebugInfo({ browserInfo: { onLine: false } });
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [updateDebugInfo]);

  // Check API health when the component mounts
  useEffect(() => {
    console.log('[useApi] Component mounted, checking API health...');
    lastCheckTimeRef.current = Date.now();
    
    const initialHealthCheck = async () => {
      try {
        console.log('[useApi] Performing initial health check');
        connectionAttemptRef.current++;
        updateDebugInfo({ 
          connectionAttempts: connectionAttemptRef.current,
          lastChecked: new Date().toISOString()
        });
        
        const healthData = await apiService.checkHealth();
        console.log('[useApi] Initial health check successful:', healthData);
        
        // Get the active endpoint from the response
        if (healthData._endpoint) {
          const baseUrl = healthData._endpoint.replace(/\/api\/health$/, '').replace(/\/health$/, '');
          setActiveEndpoint(baseUrl);
          updateDebugInfo({ 
            activeEndpoint: baseUrl,
            lastResponse: healthData,
            lastSuccessTime: new Date().toISOString()
          });
        }
        
        setConnected(true);
      } catch (err) {
        console.error('[useApi] Initial health check failed:', err.message);
        setConnected(false);
        updateDebugInfo({
          failedAttempts: apiDebugInfo.failedAttempts + 1,
          lastErrorMessage: err.message,
          lastErrorStack: err.stack,
          lastChecked: new Date().toISOString()
        });
      }
    };
    
    initialHealthCheck();
    
    // Set up an interval to check API health periodically (less frequently)
    const intervalId = setInterval(() => {
      // Only check if it's been a while since the last check
      const timeSinceLastCheck = Date.now() - lastCheckTimeRef.current;
      if (timeSinceLastCheck < 45000) { // 45 seconds
        console.log(`[useApi] Skipping periodic check, last check was ${timeSinceLastCheck/1000}s ago`);
        return;
      }
      
      console.log('[useApi] Performing periodic health check');
      lastCheckTimeRef.current = Date.now();
      
      checkHealth().catch(err => {
        console.error('[useApi] Periodic health check failed:', err.message);
      });
    }, 60000); // Check every 60 seconds (reduced frequency)
    
    return () => {
      clearInterval(intervalId);
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
    };
  }, [apiDebugInfo.failedAttempts, updateDebugInfo]);

  /**
   * Clear any existing error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Generic method to call an API method with loading and error handling
   * @param {Function} apiMethod - API method to call
   * @param {Array} args - Arguments to pass to the API method
   * @returns {Promise<any>} Result of the API call
   */
  const callApi = useCallback(async (apiMethod, ...args) => {
    console.log('[useApi] API call started', { method: apiMethod.name, args });
    setLoading(true);
    setError(null);
    
    const startTime = performance.now();
    try {
      const result = await apiMethod(...args);
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      console.log('[useApi] API call successful', { 
        method: apiMethod.name, 
        result, 
        responseTime: `${responseTime.toFixed(2)}ms`
      });
      
      setLoading(false);
      updateDebugInfo({
        lastSuccessTimestamp: new Date().toISOString(),
        lastResponseTime: responseTime,
        activeEndpoint: apiService.workingUrl || activeEndpoint
      });
      
      // Update our connected state and endpoint if needed
      setConnected(true);
      if (apiService.workingUrl && apiService.workingUrl !== activeEndpoint) {
        setActiveEndpoint(apiService.workingUrl);
      }
      
      return result;
    } catch (err) {
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      console.error('[useApi] API call failed', { 
        method: apiMethod.name, 
        error: err.message,
        responseTime: `${responseTime.toFixed(2)}ms`
      });
      
      setError(err.message || 'An error occurred');
      setLoading(false);
      
      // Don't mark as disconnected for all errors, only connection-related ones
      if (err.message.includes('connect') || err.message.includes('network') || 
          err.message.includes('timeout') || err.message.includes('CORS')) {
        setConnected(false);
      }
      
      updateDebugInfo({
        lastErrorTimestamp: new Date().toISOString(),
        lastErrorMessage: err.message,
        lastErrorStack: err.stack,
        lastResponseTime: responseTime,
        failedAttempts: apiDebugInfo.failedAttempts + 1
      });
      
      throw err;
    }
  }, [activeEndpoint, apiDebugInfo.failedAttempts, updateDebugInfo]);

  /**
   * Check API health
   * @returns {Promise<Object>} Health status
   */
  const checkHealth = useCallback(async () => {
    console.log('[useApi] Checking API health');
    lastCheckTimeRef.current = Date.now();
    
    try {
      updateDebugInfo({
        connectionAttempts: apiDebugInfo.connectionAttempts + 1,
        lastChecked: new Date().toISOString()
      });
      
      const result = await callApi(apiService.checkHealth.bind(apiService));
      console.log('[useApi] API health check result:', result);
      
      // Get the active endpoint from the response
      if (result._endpoint && result._endpoint !== activeEndpoint) {
        const baseUrl = result._endpoint.replace(/\/api\/health$/, '').replace(/\/health$/, '');
        setActiveEndpoint(baseUrl);
        updateDebugInfo({ activeEndpoint: baseUrl });
      }
      
      setConnected(result.status === 'ok');
      return result;
    } catch (err) {
      console.error('[useApi] API health check failed:', err.message);
      setConnected(false);
      updateDebugInfo({
        failedAttempts: apiDebugInfo.failedAttempts + 1
      });
      throw err;
    }
  }, [activeEndpoint, apiDebugInfo.connectionAttempts, apiDebugInfo.failedAttempts, callApi, updateDebugInfo]);

  /**
   * Run a demo test
   * @returns {Promise<Object>} Test results
   */
  const runDemoTest = useCallback(() => {
    return callApi(apiService.runDemoTest.bind(apiService));
  }, [callApi]);

  /**
   * Test custom code
   * @param {Object} data - Request data
   * @returns {Promise<Object>} Test results
   */
  const testCustomCode = useCallback((data) => {
    return callApi(apiService.testCustomCode.bind(apiService), data);
  }, [callApi]);

  /**
   * Test GitHub repository
   * @param {Object} data - Request data
   * @returns {Promise<Object>} Test results
   */
  const testGithubRepo = useCallback((data) => {
    return callApi(apiService.testGithubRepo.bind(apiService), data);
  }, [callApi]);

  /**
   * Get results for a session
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Test results
   */
  const getResults = useCallback((sessionId) => {
    return callApi(apiService.getResults.bind(apiService), sessionId);
  }, [callApi]);

  return {
    loading,
    error,
    connected,
    activeEndpoint,
    clearError,
    checkHealth,
    runDemoTest,
    testCustomCode,
    testGithubRepo,
    getResults,
    apiDebugInfo,
    updateDebugInfo,
  };
};

export default useApi; 