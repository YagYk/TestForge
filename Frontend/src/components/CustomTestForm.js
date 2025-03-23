import React, { useState } from 'react';
import axios from 'axios';

function CustomTestForm({ setResults }) {
  const [code, setCode] = useState('');
  const [tests, setTests] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!code.trim()) {
      setError('Please enter your code');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:5000/api/test-custom', {
        code,
        tests
      });
      
      setResults(response.data);
      
      // Scroll to results
      const resultsSection = document.querySelector('#results');
      if (resultsSection) {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
      }
    } catch (err) {
      console.error("Error submitting custom test:", err);
      setError(err.response?.data?.message || 'An error occurred while testing the code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="test-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="code">Your Code</label>
        <textarea
          id="code"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Paste your source code here..."
          required
        ></textarea>
      </div>
      
      <div className="form-group">
        <label htmlFor="tests">Your Tests (optional)</label>
        <textarea
          id="tests"
          value={tests}
          onChange={(e) => setTests(e.target.value)}
          placeholder="Paste your tests here... (If empty, we'll generate tests for you)"
        ></textarea>
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      <button 
        type="submit" 
        className="form-btn" 
        disabled={loading}
      >
        {loading ? (
          <>
            <span className="loading-spinner"></span>
            Analyzing...
          </>
        ) : (
          'Run Test'
        )}
      </button>
    </form>
  );
}

export default CustomTestForm;