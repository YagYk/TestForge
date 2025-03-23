import React, { useState, useEffect, useRef } from 'react';
import useApi from '../hooks/useApi';
import { API_ENDPOINTS } from '../config';

// Dummy data for testing UI rendering
const DUMMY_RESULTS = {
  total_mutations: 5,
  tests_passed_original: 2,
  tests_detected_mutations: 3,
  mutation_detection_rate: 60,
  mutation_results: [
    {
      mutation_id: 1,
      was_detected: true,
      mutation_description: "Changed arithmetic operator: + to -",
      original_code: "return a + b",
      mutated_code: "return a - b",
      detected_by_tests: [1, 2]
    },
    {
      mutation_id: 2,
      was_detected: false,
      mutation_description: "Changed comparison operator: == to !=",
      original_code: "if b == 0:",
      mutated_code: "if b != 0:"
    }
  ],
  test_details: [
    {
      name: "Test #1: Addition Test",
      passes_original: true,
      detection_count: 1,
      detected_mutations: [1]
    },
    {
      name: "Test #2: Division Test",
      passes_original: true,
      detection_count: 2,
      detected_mutations: [1, 3]
    }
  ]
};

const TestForm = () => {
  const [code, setCode] = useState('def add(a, b):\n    return a + b\n\ndef divide(a, b):\n    if b == 0:\n        raise ValueError("Cannot divide by zero")\n    return a / b');
  const [customTests, setCustomTests] = useState('import unittest\n\nclass TestCalculator(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(1, 2), 3)\n\n    def test_divide(self):\n        self.assertEqual(divide(10, 2), 5)');
  const [generateAiTests, setGenerateAiTests] = useState(true);
  const [results, setResults] = useState(DUMMY_RESULTS); // Preload with dummy data
  const [apiStatus, setApiStatus] = useState('unknown');
  const [activeTab, setActiveTab] = useState('custom'); // 'custom' or 'github'
  const [repoUrl, setRepoUrl] = useState('');
  const [targetFile, setTargetFile] = useState('');
  const [githubCustomTests, setGithubCustomTests] = useState('');
  const [githubGenerateAiTests, setGithubGenerateAiTests] = useState(true);
  const [renderCount, setRenderCount] = useState(0);
  const [debugMode, setDebugMode] = useState(false);
  const [chunkLoadingError, setChunkLoadingError] = useState(false);
  const [isLoading, setLoading] = useState(false);
  
  const { loading, error, checkHealth, testCustomCode, testGithubRepo, apiDebugInfo } = useApi();
  
  // Add renderCountRef to track renders without causing re-renders
  const renderCountRef = useRef(0);
  
  // Fix the render count issue by using a ref and updating state less frequently
  useEffect(() => {
    // Increment the ref on every render
    renderCountRef.current += 1;
    
    // But only update the state occasionally to avoid infinite loop
    if (renderCountRef.current % 10 === 0) {
      setRenderCount(renderCountRef.current);
    }
  });
  
  // Separate useEffect for API health check to avoid render loops
  useEffect(() => {
    console.log('[TestForm] Component mounted for initial API health check');
    
    // Check API health on component mount
    const initialCheck = async () => {
      try {
        console.log('[TestForm] Performing initial health check');
        const healthData = await checkHealth();
        const newStatus = healthData.status === 'ok' ? 'connected' : 'error';
        console.log(`[TestForm] Initial API health status: ${newStatus}`, healthData);
        setApiStatus(newStatus);
      } catch (err) {
        console.error('[TestForm] Initial health check failed:', err);
        setApiStatus('error');
      }
    };
    
    initialCheck();
    
    // Set up periodic health checks
    const intervalId = setInterval(async () => {
      try {
        console.log('[TestForm] Performing periodic health check');
        const healthData = await checkHealth();
        const newStatus = healthData.status === 'ok' ? 'connected' : 'error';
        console.log(`[TestForm] Periodic API health status: ${newStatus}`);
        setApiStatus(newStatus);
      } catch (err) {
        console.error('[TestForm] Periodic health check failed:', err);
        setApiStatus('error');
      }
    }, 30000); // Check every 30 seconds, not too frequent
    
    return () => {
      clearInterval(intervalId);
      console.log('[TestForm] Cleanup: cleared health check interval');
    };
  }, []); // Empty dependency array so this only runs on mount
  
  // Log component rendering to console
  useEffect(() => {
    console.log('TestForm component rendered');
    console.log('Current active tab:', activeTab);
    console.log('Form has results object:', results ? 'Yes' : 'No');
    console.log('Mutation results count:', results?.mutation_results?.length);
    console.log('Test details count:', results?.test_details?.length);
  }, [activeTab, results]);
  
  // Add a better direct fetch function that specifically checks for CORS issues
  const testDirectFetch = async () => {
    try {
      console.log('[TestForm] Testing direct fetch to API');
      
      // First try with credentials included to test for CORS issues
      const response = await fetch('http://localhost:5000/api/health', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        mode: 'cors',
        credentials: 'include', // This will trigger CORS preflight
      }).catch(error => {
        throw new Error(`CORS preflight test failed: ${error.message}`);
      });
      
      const data = await response.json();
      console.log('[TestForm] Direct fetch successful:', data);
      alert(`Direct fetch successful: ${JSON.stringify(data, null, 2)}`);
      
      // If we got here, update the API status
      setApiStatus('connected');
      
    } catch (error) {
      console.error('[TestForm] Direct fetch failed:', error);
      
      // Try again without credentials to see if that's the issue
      try {
        console.log('[TestForm] Retrying without credentials...');
        const simpleResponse = await fetch('http://localhost:5000/api/health', {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
          mode: 'cors',
          credentials: 'omit', // Don't send cookies or auth headers
        });
        
        const data = await simpleResponse.json();
        console.log('[TestForm] Simple fetch successful:', data);
        alert(`CORS issue detected! Simple fetch worked but credentials don't:\n${JSON.stringify(data, null, 2)}`);
        
        // Update status since basic fetch works
        setApiStatus('connected');
        
      } catch (simpleError) {
        console.error('[TestForm] Simple fetch also failed:', simpleError);
        alert(`Both fetch attempts failed:\n1. ${error.message}\n2. ${simpleError.message}`);
      }
    }
  };
  
  // Fix the handleSubmit function to properly handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Form submitted with activeTab:', activeTab);
    
    if (activeTab === 'custom' && !code.trim()) {
      alert('Please enter some code to test');
      return;
    }
    
    if (activeTab === 'github' && !repoUrl.trim()) {
      alert('Please enter a GitHub repository URL');
      return;
    }
    
    try {
      // Check API connection first
      if (apiStatus !== 'connected') {
        try {
          console.log('[TestForm] Checking API connection before form submission...');
          await checkHealth();
          // If we get here, connection is good
          setApiStatus('connected');
        } catch (err) {
          console.error('[TestForm] API is not available:', err);
          alert('API connection failed. Please make sure the Flask server is running at http://localhost:5000');
          return;
        }
      }
      
      if (activeTab === 'custom') {
        const data = {
          code,
          custom_tests: customTests.trim() || undefined,
          generate_ai_tests: generateAiTests,
        };
        
        console.log('[TestForm] Submitting custom code test:', data);
        
        try {
          setLoading(true);
          // Try to get real results from backend
          const response = await testCustomCode(data);
          console.log('[TestForm] Custom code test successful:', response);
          setResults(response);
        } catch (err) {
          console.error('Failed to get results from backend:', err);
          alert(`Test failed: ${err.message}`);
          
          // If backend fails, use dummy data with updated code
          setResults({
            ...DUMMY_RESULTS,
            code: code,
            custom_tests: customTests
          });
        } finally {
          setLoading(false);
        }
      } else {
        // GitHub repo testing
        const data = {
          repo_url: repoUrl,
          target_file: targetFile.trim() || undefined,
          custom_tests: githubCustomTests.trim() || undefined,
          generate_ai_tests: githubGenerateAiTests,
        };
        
        console.log('[TestForm] Submitting GitHub repo test:', data);
        
        try {
          setLoading(true);
          // Try to get real results from backend
          const response = await testGithubRepo(data);
          console.log('[TestForm] GitHub repo test successful:', response);
          setResults(response);
        } catch (err) {
          console.error('Failed to get results from backend:', err);
          alert(`Test failed: ${err.message}`);
          
          // If backend fails, use dummy data with updated repo info
          setResults({
            ...DUMMY_RESULTS,
            repo_url: repoUrl,
            target_file: targetFile
          });
        } finally {
          setLoading(false);
        }
      }
    } catch (err) {
      console.error('Failed to test code:', err);
      alert(`Test failed: ${err.message}`);
    }
  };
  
  // Add event listener for chunk loading errors
  useEffect(() => {
    const handleChunkError = (event) => {
      // Check if error is a chunk loading error
      if (event.error && event.error.message && event.error.message.includes('Loading chunk')) {
        console.error('[TestForm] Detected chunk loading error:', event.error);
        setChunkLoadingError(true);
      }
    };
    
    // Add event listener
    window.addEventListener('error', handleChunkError);
    
    // Check if errors already occurred before this component mounted
    if (window.chunkLoadingErrorOccurred) {
      console.warn('[TestForm] Chunk error occurred before component mount');
      setChunkLoadingError(true);
    }
    
    return () => {
      window.removeEventListener('error', handleChunkError);
    };
  }, []);
  
  // Disable additional debug info if we have chunk errors to reduce complexity
  const effectiveDebugMode = debugMode && !chunkLoadingError;
  
  return (
    <div className="test-form" style={{
      border: '2px solid red', 
      padding: '20px', 
      margin: '20px 0',
      display: 'block',
      visibility: 'visible',
      opacity: 1,
      background: '#141414'
    }}>
      {chunkLoadingError && (
        <div style={{
          background: '#480000',
          color: '#ff9999',
          padding: '10px',
          marginBottom: '15px',
          borderRadius: '5px',
          fontSize: '0.9rem'
        }}>
          <h4 style={{ margin: '0 0 8px 0' }}>Warning: Resource Loading Issues Detected</h4>
          <p style={{ margin: '0 0 5px 0' }}>
            Some JavaScript resources failed to load. The core functionality will still work, 
            but you may experience limited features or styling issues.
          </p>
          <p style={{ margin: '0', fontSize: '0.8rem' }}>
            Try refreshing the page or clearing your browser cache if problems persist.
          </p>
        </div>
      )}
      
      <div className="form-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <h2>Test Your Code</h2>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
          <div 
            className={`api-status api-status-${apiStatus}`}
            style={{
              padding: '8px 12px',
              borderRadius: '4px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <span style={{ 
              width: '10px', 
              height: '10px', 
              borderRadius: '50%', 
              background: apiStatus === 'connected' ? '#4caf50' : apiStatus === 'error' ? '#f44336' : '#ffc107',
              display: 'inline-block'
            }}></span>
            API: {apiStatus === 'connected' 
              ? 'Connected' 
              : apiStatus === 'error' 
                ? <span>
                    Disconnected 
                    <button 
                      onClick={() => {
                        console.log('[TestForm] Manual health check initiated');
                        checkHealth().catch(err => {
                          console.error('[TestForm] Manual health check failed:', err);
                        });
                      }} 
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#f44336',
                        cursor: 'pointer',
                        textDecoration: 'underline',
                        padding: '0 4px',
                        fontSize: '0.8rem'
                      }}
                    >
                      Retry
                    </button>
                    <div style={{
                      fontSize: '0.8rem',
                      marginTop: '5px',
                      color: '#aaa'
                    }}>
                      Make sure Flask server is running at: http://localhost:5000
                    </div>
                  </span> 
                : 'Checking...'}
          </div>
          
          <button 
            onClick={() => setDebugMode(!debugMode)}
            style={{
              marginTop: '10px',
              background: 'transparent',
              border: '1px solid #666',
              color: '#999',
              padding: '4px 8px',
              fontSize: '0.7rem',
              cursor: 'pointer',
              borderRadius: '3px'
            }}
          >
            {debugMode ? 'Hide Debug Info' : 'Show Debug Info'}
          </button>
        </div>
      </div>
      
      {/* Debug panel */}
      {effectiveDebugMode && (
        <div style={{
          background: '#222',
          padding: '15px',
          marginTop: '15px',
          borderRadius: '5px',
          fontSize: '0.9rem'
        }}>
          <h3 style={{ color: '#00ffcc', marginTop: 0 }}>Debug Controls</h3>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
            <button 
              onClick={testDirectFetch}
              style={{
                background: '#333',
                border: '1px solid #666',
                color: '#fff',
                padding: '8px 12px',
                cursor: 'pointer',
                borderRadius: '4px'
              }}
            >
              Test Direct Fetch
            </button>
            <button 
              onClick={() => {
                console.log('[TestForm] Manual health check initiated');
                checkHealth().catch(err => {
                  console.error('[TestForm] Manual health check failed:', err);
                });
              }}
              style={{
                background: '#333',
                border: '1px solid #666',
                color: '#fff',
                padding: '8px 12px',
                cursor: 'pointer',
                borderRadius: '4px'
              }}
            >
              Test API Service
            </button>
          </div>
          
          <h4 style={{ color: '#fff', marginBottom: '5px' }}>Connection Info</h4>
          <div style={{ marginBottom: '15px', fontFamily: 'monospace', color: '#ccc' }}>
            <p>Frontend URL: {window.location.href}</p>
            <p>API Endpoint: {API_ENDPOINTS?.HEALTH || 'Unknown'}</p>
            <p>API Status: {apiStatus}</p>
            <p>Is CORS issue: {apiStatus === 'error' ? 'Possible' : 'No'}</p>
          </div>
          
          <h4 style={{ color: '#fff', marginBottom: '5px' }}>API Debug Information</h4>
          <div style={{ marginBottom: '15px', fontFamily: 'monospace', color: '#ccc', maxHeight: '200px', overflow: 'auto' }}>
            <p>API URL: {apiDebugInfo.apiUrl}</p>
            <p>Connection Attempts: {apiDebugInfo.connectionAttempts}</p>
            <p>Failed Attempts: {apiDebugInfo.failedAttempts}</p>
            <p>Last Checked: {apiDebugInfo.lastChecked}</p>
            <p>Browser Online: {apiDebugInfo.browserInfo.onLine ? 'Yes' : 'No'}</p>
            {apiDebugInfo.lastErrorMessage && (
              <>
                <p style={{ color: '#ff6b6b' }}>Last Error: {apiDebugInfo.lastErrorMessage}</p>
                <details>
                  <summary>Error Stack</summary>
                  <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.8rem' }}>
                    {apiDebugInfo.lastErrorStack}
                  </pre>
                </details>
              </>
            )}
            {apiDebugInfo.lastResponseTime && (
              <p>Last Response Time: {apiDebugInfo.lastResponseTime.toFixed(2)}ms</p>
            )}
          </div>
        </div>
      )}
      
      {/* Debug information */}
      <div style={{background: '#333', color: '#fff', padding: '10px', marginBottom: '15px'}}>
        <p>Debug Info - Active Tab: {activeTab} | Render Count: {renderCount}</p>
        <p>Results Available: {results ? 'Yes' : 'No'} | Mutations: {results?.mutation_results?.length || 0} | Tests: {results?.test_details?.length || 0}</p>
      </div>
      
      {error && (
        <div className="error-message" style={{
          background: 'rgba(255,0,0,0.1)',
          border: '1px solid red',
          color: 'red',
          padding: '10px',
          margin: '10px 0'
        }}>
          Error: {error}
        </div>
      )}
      
      {/* Tab controls */}
      <div className="tab-controls" style={{
        display: 'flex', 
        marginBottom: '20px',
        position: 'relative',
        zIndex: 50
      }}>
        <button 
          className={`tab-btn ${activeTab === 'custom' ? 'active' : ''}`}
          onClick={() => setActiveTab('custom')}
          style={{
            flex: 1,
            padding: '10px',
            background: activeTab === 'custom' ? '#00ffcc' : '#333',
            color: activeTab === 'custom' ? 'black' : 'white',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          Custom Code
        </button>
        <button 
          className={`tab-btn ${activeTab === 'github' ? 'active' : ''}`}
          onClick={() => setActiveTab('github')}
          style={{
            flex: 1,
            padding: '10px',
            background: activeTab === 'github' ? '#00ffcc' : '#333',
            color: activeTab === 'github' ? 'black' : 'white',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          GitHub Repository
        </button>
      </div>
      
      {/* Custom Code Form */}
      {activeTab === 'custom' ? (
        <form onSubmit={handleSubmit} style={{background: '#1a1a1a', padding: '15px', borderRadius: '5px'}}>
          <div className="form-group">
            <label htmlFor="code">Python Code:</label>
            <textarea
              id="code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="def add(a, b):
    return a + b"
              rows={10}
              required
              style={{width: '100%', background: '#222', color: 'white', padding: '10px'}}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="customTests">Custom Tests (Optional):</label>
            <textarea
              id="customTests"
              value={customTests}
              onChange={(e) => setCustomTests(e.target.value)}
              placeholder="import unittest

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)"
              rows={8}
              style={{width: '100%', background: '#222', color: 'white', padding: '10px'}}
            />
          </div>
          
          <div className="form-check" style={{marginBottom: '15px'}}>
            <input
              type="checkbox"
              id="generateAiTests"
              checked={generateAiTests}
              onChange={(e) => setGenerateAiTests(e.target.checked)}
            />
            <label htmlFor="generateAiTests" style={{marginLeft: '8px'}}>Generate AI Tests</label>
          </div>
          
          <button 
            type="submit" 
            className="submit-button" 
            disabled={isLoading}
            style={{
              background: isLoading ? '#333' : 'linear-gradient(135deg, #00ffcc 0%, #3a86ff 100%)',
              color: 'black',
              padding: '10px 20px',
              border: 'none',
              borderRadius: '5px',
              cursor: isLoading ? 'not-allowed' : 'pointer'
            }}
          >
            {isLoading ? 'Testing...' : 'Run Tests'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleSubmit} style={{background: '#1a1a1a', padding: '15px', borderRadius: '5px'}}>
          <div className="form-group">
            <label htmlFor="repoUrl">GitHub Repository URL:</label>
            <input
              type="text"
              id="repoUrl"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/username/repository"
              required
              className="form-input"
              style={{width: '100%', background: '#222', color: 'white', padding: '10px', marginBottom: '15px'}}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="targetFile">Target File Path (Optional):</label>
            <input
              type="text"
              id="targetFile"
              value={targetFile}
              onChange={(e) => setTargetFile(e.target.value)}
              placeholder="path/to/file.py"
              className="form-input"
              style={{width: '100%', background: '#222', color: 'white', padding: '10px', marginBottom: '15px'}}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="githubCustomTests">Custom Tests (Optional):</label>
            <textarea
              id="githubCustomTests"
              value={githubCustomTests}
              onChange={(e) => setGithubCustomTests(e.target.value)}
              placeholder="import unittest

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)"
              rows={8}
              className="form-textarea"
              style={{width: '100%', background: '#222', color: 'white', padding: '10px'}}
            />
          </div>
          
          <div className="form-check" style={{marginBottom: '15px'}}>
            <input
              type="checkbox"
              id="githubGenerateAiTests"
              checked={githubGenerateAiTests}
              onChange={(e) => setGithubGenerateAiTests(e.target.checked)}
            />
            <label htmlFor="githubGenerateAiTests" style={{marginLeft: '8px'}}>Generate AI Tests</label>
          </div>
          
          <button 
            type="submit" 
            className="submit-button" 
            disabled={isLoading}
            style={{
              background: isLoading ? '#333' : 'linear-gradient(135deg, #00ffcc 0%, #3a86ff 100%)',
              color: 'black',
              padding: '10px 20px',
              border: 'none',
              borderRadius: '5px',
              cursor: isLoading ? 'not-allowed' : 'pointer'
            }}
          >
            {isLoading ? 'Testing...' : 'Run Tests'}
          </button>
        </form>
      )}
      
      {/* Results Section */}
      {results && (
        <div className="results" style={{
          marginTop: '30px',
          background: '#1a1a1a',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)',
          display: 'block',
          visibility: 'visible',
          opacity: 1
        }}>
          <h3>Test Results</h3>
          
          <div className="results-summary" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '15px',
            margin: '20px 0',
            background: '#111',
            padding: '15px',
            borderRadius: '5px'
          }}>
            <div className="result-item">
              <span className="result-label">Total Mutations:</span>
              <span className="result-value">{results.total_mutations}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Tests Passed on Original:</span>
              <span className="result-value">{results.tests_passed_original}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Mutations Detected:</span>
              <span className="result-value">{results.tests_detected_mutations}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Detection Rate:</span>
              <span className="result-value">{results.mutation_detection_rate.toFixed(2)}%</span>
            </div>
          </div>
          
          <h4>Mutation Results</h4>
          <div className="mutation-results" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '20px',
            margin: '20px 0'
          }}>
            {results.mutation_results.map((mutation, index) => (
              <div key={index} className={`mutation-card ${mutation.was_detected ? 'detected' : 'survived'}`} style={{
                border: `1px solid ${mutation.was_detected ? 'rgba(0, 255, 153, 0.4)' : 'rgba(255, 100, 100, 0.4)'}`,
                borderRadius: '8px',
                padding: '15px',
                background: mutation.was_detected ? 'rgba(0, 255, 153, 0.1)' : 'rgba(255, 100, 100, 0.1)',
                display: 'block',
                visibility: 'visible',
                opacity: 1
              }}>
                <div className="mutation-header" style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  marginBottom: '10px'
                }}>
                  <span className="mutation-id">Mutation #{mutation.mutation_id}</span>
                  <span className={`mutation-status ${mutation.was_detected ? 'detected' : 'survived'}`} style={{
                    padding: '3px 8px',
                    borderRadius: '4px',
                    background: mutation.was_detected ? 'rgba(0, 255, 153, 0.3)' : 'rgba(255, 100, 100, 0.3)',
                    color: mutation.was_detected ? '#00ff99' : '#ff6464'
                  }}>
                    {mutation.was_detected ? 'Detected' : 'Survived'}
                  </span>
                </div>
                <div className="mutation-description" style={{marginBottom: '10px'}}>{mutation.mutation_description}</div>
                <div className="mutation-code" style={{marginBottom: '15px'}}>
                  <div className="code-block" style={{marginBottom: '10px'}}>
                    <div className="code-label" style={{marginBottom: '5px', color: '#aaa'}}>Original:</div>
                    <pre style={{
                      background: '#000',
                      padding: '8px',
                      borderRadius: '4px',
                      overflow: 'auto',
                      maxHeight: '100px'
                    }}>{mutation.original_code}</pre>
                  </div>
                  <div className="code-block">
                    <div className="code-label" style={{marginBottom: '5px', color: '#aaa'}}>Mutated:</div>
                    <pre style={{
                      background: '#000',
                      padding: '8px',
                      borderRadius: '4px',
                      overflow: 'auto',
                      maxHeight: '100px'
                    }}>{mutation.mutated_code}</pre>
                  </div>
                </div>
                {mutation.was_detected && (
                  <div className="detected-tests">
                    <div className="detected-label" style={{marginBottom: '5px', color: '#aaa'}}>Detected by tests:</div>
                    <ul style={{
                      margin: '0',
                      padding: '0 0 0 20px',
                      listStyle: 'disc'
                    }}>
                      {mutation.detected_by_tests.map(testId => (
                        <li key={testId}>Test #{testId}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
          
          <h4>Test Details</h4>
          <div className="test-details" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '20px',
            margin: '20px 0'
          }}>
            {results.test_details.map((test, index) => (
              <div key={index} className="test-card" style={{
                border: `1px solid ${test.passes_original ? 'rgba(0, 255, 153, 0.4)' : 'rgba(255, 100, 100, 0.4)'}`,
                borderRadius: '8px',
                padding: '15px',
                background: test.passes_original ? 'rgba(0, 255, 153, 0.1)' : 'rgba(255, 100, 100, 0.1)',
                display: 'block',
                visibility: 'visible',
                opacity: 1
              }}>
                <div className="test-header" style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  marginBottom: '10px',
                  flexWrap: 'wrap'
                }}>
                  <span className="test-name" style={{fontWeight: 'bold'}}>{test.name}</span>
                  <span className={`test-status ${test.passes_original ? 'passed' : 'failed'}`} style={{
                    padding: '3px 8px',
                    borderRadius: '4px',
                    background: test.passes_original ? 'rgba(0, 255, 153, 0.3)' : 'rgba(255, 100, 100, 0.3)',
                    color: test.passes_original ? '#00ff99' : '#ff6464'
                  }}>
                    {test.passes_original ? 'Passed Original' : 'Failed Original'}
                  </span>
                </div>
                <div className="test-detection" style={{marginBottom: '10px'}}>
                  <span className="detection-label" style={{color: '#aaa', marginRight: '5px'}}>Detected Mutations:</span>
                  <span className="detection-count">{test.detection_count}</span>
                </div>
                {test.detected_mutations.length > 0 && (
                  <div className="detected-mutations">
                    <div className="detected-label" style={{marginBottom: '5px', color: '#aaa'}}>Detected mutations:</div>
                    <ul style={{
                      margin: '0',
                      padding: '0 0 0 20px',
                      listStyle: 'disc'
                    }}>
                      {test.detected_mutations.map(mutationId => (
                        <li key={mutationId}>Mutation #{mutationId}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Add a global handler for chunk loading errors
if (typeof window !== 'undefined') {
  window.addEventListener('error', (event) => {
    if (event.error && event.error.message && event.error.message.includes('Loading chunk')) {
      window.chunkLoadingErrorOccurred = true;
      console.error('[Global] Chunk loading error detected:', event.error);
    }
  });
}

export default TestForm; 