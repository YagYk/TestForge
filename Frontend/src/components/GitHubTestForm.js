import React, { useState } from 'react';
import axios from 'axios';

function GitHubTestForm({ setResults }) {
  const [repoUrl, setRepoUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!repoUrl.trim()) {
      setError('Please enter a GitHub repository URL');
      return;
    }
    
    if (!isValidGitHubUrl(repoUrl)) {
      setError('Please enter a valid GitHub repository URL');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:5000/api/test-github', {
        repo_url: repoUrl,
        branch
      });
      
      setResults(response.data);
      
      // Scroll to results
      const resultsSection = document.querySelector('#results');
      if (resultsSection) {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
      }
    } catch (err) {
      console.error("Error testing GitHub repo:", err);
      setError(err.response?.data?.message || 'An error occurred while testing the repository');
    } finally {
      setLoading(false);
    }
  };
  
  const isValidGitHubUrl = (url) => {
    const githubPattern = /^https?:\/\/(www\.)?github\.com\/[\w-]+\/[\w.-]+\/?$/;
    return githubPattern.test(url);
  };

  return (
    <form className="test-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="repoUrl">GitHub Repository URL</label>
        <input
          type="text"
          id="repoUrl"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/username/repository"
          required
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="branch">Branch (Optional)</label>
        <input
          type="text"
          id="branch"
          value={branch}
          onChange={(e) => setBranch(e.target.value)}
          placeholder="main"
        />
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
            Testing Repository...
          </>
        ) : (
          'Test Repository'
        )}
      </button>
    </form>
  );
}

export default GitHubTestForm;