import React from 'react';

function TestResults({ results }) {
  const { 
    total_mutants = 0, 
    killed_mutants = 0, 
    surviving_mutants = 0, 
    test_effectiveness = 0,
    mutations = []
  } = results;

  // Skip rendering if no results
  if (total_mutants === 0 && mutations.length === 0) {
    return null;
  }

  return (
    <section className="test-results" id="results">
      <h2 className="section-title">Test Results</h2>
      
      <div className="results-summary">
        <div className="result-card">
          <h3>Total Mutants</h3>
          <div className="value">{total_mutants}</div>
        </div>
        
        <div className="result-card">
          <h3>Killed Mutants</h3>
          <div className="value">{killed_mutants}</div>
        </div>
        
        <div className="result-card">
          <h3>Surviving Mutants</h3>
          <div className="value">{surviving_mutants}</div>
        </div>
        
        <div className="result-card">
          <h3>Test Effectiveness</h3>
          <div className="value">{test_effectiveness}%</div>
        </div>
      </div>
      
      {mutations.length > 0 && (
        <div className="mutations-list">
          <h3>Mutation Details</h3>
          
          {mutations.map((mutation, index) => (
            <div key={index} className="mutation-item">
              <div className="mutation-header">
                <div className="mutation-title">
                  {mutation.file_path}:{mutation.line_number}
                </div>
                <div className={`mutation-status ${mutation.status.toLowerCase()}`}>
                  {mutation.status}
                </div>
              </div>
              
              <div className="mutation-details">
                <p>
                  <strong>Mutation Type:</strong> {mutation.mutation_type}
                </p>
                <div className="mutation-code">
                  <pre>
                    <strong>Original:</strong> {mutation.original_code}
                    <br /><br />
                    <strong>Mutated:</strong> {mutation.mutated_code}
                  </pre>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export default TestResults;