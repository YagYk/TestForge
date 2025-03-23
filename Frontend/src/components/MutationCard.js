import React, { useState } from 'react';

function MutationCard({ mutation, animationDelay = 0 }) {
  const [expanded, setExpanded] = useState(false);

  // Apply animation delay style
  const cardStyle = {
    animationDelay: `${animationDelay}s`
  };

  return (
    <div 
      className={`mutation-card ${mutation.killed ? 'killed' : 'survived'}`}
      style={cardStyle}
    >
      <div className="mutation-header" onClick={() => setExpanded(!expanded)}>
        <h3>
          <span className="mutation-id">Mutation #{mutation.id || 'Unknown'}</span>
          <span className={mutation.killed ? 'status-killed' : 'status-survived'}>
            {mutation.killed ? 'Killed' : 'Survived'}
          </span>
        </h3>
        <div className="mutation-type">
          {mutation.mutation_type}
          <span className="expand-icon">{expanded ? '−' : '+'}</span>
        </div>
      </div>

      <div className={`mutation-details ${expanded ? 'expanded' : ''}`}>
        {(mutation.original_code && mutation.mutated_code) && (
          <div className="code-diff">
            <div className="code-diff-title">
              <span className="code-diff-old-title">Original Code</span>
              <span className="code-diff-new-title">Mutated Code</span>
            </div>
            <div className="code-diff-content">
              <div className="code-diff-old">
                <pre dangerouslySetInnerHTML={{ __html: mutation.original_code }} />
              </div>
              <div className="code-diff-new">
                <pre dangerouslySetInnerHTML={{ __html: mutation.mutated_code }} />
              </div>
            </div>
          </div>
        )}
        
        {(!mutation.original_code || !mutation.mutated_code) && (
          <>
            {mutation.original_code && (
              <div className="code-block">
                <strong>Original Code:</strong>
                <pre dangerouslySetInnerHTML={{ __html: mutation.original_code }} />
              </div>
            )}
            {mutation.mutated_code && (
              <div className="code-block">
                <strong>Mutated Code:</strong>
                <pre dangerouslySetInnerHTML={{ __html: mutation.mutated_code }} />
              </div>
            )}
          </>
        )}
        
        <div className="code-block test-block">
          <strong>Test Generated:</strong>
          <pre dangerouslySetInnerHTML={{ __html: mutation.test_generated }} />
        </div>
      </div>
    </div>
  );
}

export default MutationCard;