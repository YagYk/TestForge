// Bug Slayer AI - Main JavaScript

$(document).ready(function() {
    // DOM Elements
    const runTestsButton = document.getElementById('run-tests');
    const totalMutantsEl = document.getElementById('total-mutants');
    const killedMutantsEl = document.getElementById('killed-mutants');
    const survivingMutantsEl = document.getElementById('surviving-mutants');
    const testEffectivenessEl = document.getElementById('test-effectiveness');
    const mutationsTableEl = document.getElementById('mutations-table');
    const testCodeDisplayEl = document.getElementById('test-code-display');
    const testCodeModal = new bootstrap.Modal(document.getElementById('testCodeModal'));
    
    // Custom code elements
    const customCodeForm = document.getElementById('custom-code-form');
    const functionNameInput = document.getElementById('function-name');
    const codeInput = document.getElementById('code-input');
    const runCustomTestButton = document.getElementById('run-custom-test');
    const customOutputSection = document.getElementById('custom-output-section');
    const customMutationsTableEl = document.getElementById('custom-mutations-table');
    
    // GitHub repo elements
    const githubForm = document.getElementById('github-form');
    const repoUrlInput = document.getElementById('repo-url');
    const filePathInput = document.getElementById('file-path');
    const repoFunctionNameInput = document.getElementById('repo-function-name');
    const runGithubTestButton = document.getElementById('run-github-test');
    const githubOutputSection = document.getElementById('github-output-section');
    const githubMutationsTableEl = document.getElementById('github-mutations-table');
    
    // Debug check for custom mutations table
    if (!customMutationsTableEl) {
        console.error('Custom mutations table element not found. Please check the HTML.');
    }
    
    // Fetch initial results
    fetchResults();
    
    // Main run tests button
    if (runTestsButton) {
        runTestsButton.addEventListener('click', runTests);
    }
    
    // Function to scroll to results section
    function scrollToResults() {
        const resultsSection = document.getElementById('results');
        if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
            resultsSection.classList.add('highlight-section');
            setTimeout(() => {
                resultsSection.classList.remove('highlight-section');
            }, 2000);
        }
    }
    
    // Run tests function
    function runTests() {
        // Change button state to loading
        runTestsButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Running...';
        runTestsButton.disabled = true;
        
        showLoading('Running tests...');
        
        // Call API to run tests
        fetch('/api/run-tests', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Update results
            updateResults(data);
            
            // Reset button
            runTestsButton.innerHTML = 'Run Test Generation';
            runTestsButton.disabled = false;
            
            hideLoading();
        })
        .catch(error => {
            console.error('Error running tests:', error);
            
            // Reset button
            runTestsButton.innerHTML = 'Run Test Generation';
            runTestsButton.disabled = false;
            
            // Show error message
            alert('Error running tests. Please try again.');
            
            hideLoading();
        });
    }
    
    // Fetch results function
    function fetchResults() {
        fetch('/api/results')
        .then(response => response.json())
        .then(data => {
            updateResults(data);
        })
        .catch(error => {
            console.error('Error fetching results:', error);
        });
    }
    
    // Update results in the UI
    function updateResults(data) {
        // Update summary stats
        totalMutantsEl.textContent = data.total_mutants;
        killedMutantsEl.textContent = data.killed_mutants;
        survivingMutantsEl.textContent = data.surviving_mutants;
        testEffectivenessEl.textContent = Math.round(data.test_effectiveness) + '%';
        
        // Clear mutations table
        mutationsTableEl.innerHTML = '';
        
        // Add mutations to table
        data.mutations.forEach(mutation => {
            const row = document.createElement('tr');
            
            // Mutation ID
            const idCell = document.createElement('td');
            idCell.textContent = mutation.id;
            row.appendChild(idCell);
            
            // Mutation type
            const typeCell = document.createElement('td');
            typeCell.textContent = mutation.mutation_type;
            row.appendChild(typeCell);
            
            // Status
            const statusCell = document.createElement('td');
            if (mutation.killed) {
                statusCell.innerHTML = '<span class="badge bg-success">Killed</span>';
            } else {
                statusCell.innerHTML = '<span class="badge bg-danger">Survived</span>';
            }
            row.appendChild(statusCell);
            
            // Actions
            const actionsCell = document.createElement('td');
            const viewButton = document.createElement('button');
            viewButton.className = 'btn btn-sm btn-primary';
            viewButton.textContent = 'View Test';
            viewButton.addEventListener('click', () => {
                viewTestCode(mutation);
            });
            actionsCell.appendChild(viewButton);
            row.appendChild(actionsCell);
            
            mutationsTableEl.appendChild(row);
        });
    }
    
    // View test code function
    function viewTestCode(mutation) {
        testCodeDisplayEl.textContent = mutation.test_generated;
        
        // If using Prism.js for syntax highlighting
        if (window.Prism) {
            Prism.highlightElement(testCodeDisplayEl);
        }
        
        // Show the modal
        testCodeModal.show();
    }
    
    // Display code in a more readable format using a modal dialog instead of alerts
    function displayCodeModal(title, code) {
        // Check if the modal already exists, remove it if it does
        let existingModal = document.getElementById('codeDisplayModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Create the modal HTML
        const modalHtml = `
        <div class="modal fade" id="codeDisplayModal" tabindex="-1" aria-labelledby="codeDisplayModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="codeDisplayModalLabel">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <pre class="bg-light p-3 rounded"><code>${escapeHtml(code)}</code></pre>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
        `;
        
        // Append the modal to the body
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Initialize and show the modal
        const modalElement = document.getElementById('codeDisplayModal');
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    }
    
    // Escape HTML characters to prevent XSS
    function escapeHtml(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }
    
    // Update custom results in the UI
    function updateCustomResults(data) {
        console.log("Received custom test data:", data);
        
        // Check for error
        if (data.error) {
            $('#customMutationsTable').html(`<tr><td colspan="5" class="text-danger">Error: ${data.error}</td></tr>`);
            return;
        }
        
        // Check if we have any mutations
        if (!data.mutations || data.mutations.length === 0) {
            $('#customMutationsTable').html('<tr><td colspan="5" class="text-center">No mutations were generated. Please try a different function.</td></tr>');
            return;
        }
        
        // Clear custom mutations table
        $('#customMutationsTable').empty();
        
        // Add mutations to table
        data.mutations.forEach(mutation => {
            const row = document.createElement('tr');
            
            // Mutation ID
            const idCell = document.createElement('td');
            idCell.textContent = mutation.id;
            row.appendChild(idCell);
            
            // Mutation type
            const typeCell = document.createElement('td');
            typeCell.textContent = mutation.mutation_type;
            row.appendChild(typeCell);
            
            // Mutated Code
            const codeCell = document.createElement('td');
            const viewMutationButton = document.createElement('button');
            viewMutationButton.className = 'btn btn-sm btn-secondary';
            viewMutationButton.textContent = 'View Mutation';
            viewMutationButton.addEventListener('click', () => {
                displayCodeModal('Mutated Code', mutation.mutated_code);
            });
            codeCell.appendChild(viewMutationButton);
            row.appendChild(codeCell);
            
            // Test Code
            const testCell = document.createElement('td');
            const viewTestButton = document.createElement('button');
            viewTestButton.className = 'btn btn-sm btn-info';
            viewTestButton.textContent = 'View Test';
            viewTestButton.addEventListener('click', () => {
                displayCodeModal('Generated Test', mutation.test_generated);
            });
            testCell.appendChild(viewTestButton);
            row.appendChild(testCell);
            
            // Status
            const statusCell = document.createElement('td');
            if (mutation.killed) {
                statusCell.innerHTML = '<span class="badge bg-success">Killed</span>';
            } else {
                statusCell.innerHTML = '<span class="badge bg-danger">Survived</span>';
            }
            row.appendChild(statusCell);
            
            $('#customMutationsTable').append(row);
        });
        
        // Also update the overall results with custom test data
        updateResultsSummary(data);
        
        // Scroll to the results section
        scrollToResults();
    }
    
    // Update GitHub results in the UI
    function updateGithubResults(data) {
        console.log("Received GitHub test data:", data);
        
        // Check for error
        if (data.error) {
            $('#githubMutationsTable').html(`<tr><td colspan="5" class="text-danger">Error: ${data.error}</td></tr>`);
            return;
        }
        
        // Check if we have any mutations
        if (!data.mutations || data.mutations.length === 0) {
            $('#githubMutationsTable').html('<tr><td colspan="5" class="text-center">No mutations were generated. Please try a different function.</td></tr>');
            return;
        }
        
        // Clear GitHub mutations table
        $('#githubMutationsTable').empty();
        
        // Add mutations to table
        data.mutations.forEach(mutation => {
            const row = document.createElement('tr');
            
            // Mutation ID
            const idCell = document.createElement('td');
            idCell.textContent = mutation.id;
            row.appendChild(idCell);
            
            // Mutation type
            const typeCell = document.createElement('td');
            typeCell.textContent = mutation.mutation_type;
            row.appendChild(typeCell);
            
            // Mutated Code
            const codeCell = document.createElement('td');
            const viewMutationButton = document.createElement('button');
            viewMutationButton.className = 'btn btn-sm btn-secondary';
            viewMutationButton.textContent = 'View Mutation';
            viewMutationButton.addEventListener('click', () => {
                displayCodeModal('Mutated Code', mutation.mutated_code);
            });
            codeCell.appendChild(viewMutationButton);
            row.appendChild(codeCell);
            
            // Test Code
            const testCell = document.createElement('td');
            const viewTestButton = document.createElement('button');
            viewTestButton.className = 'btn btn-sm btn-info';
            viewTestButton.textContent = 'View Test';
            viewTestButton.addEventListener('click', () => {
                displayCodeModal('Generated Test', mutation.test_generated);
            });
            testCell.appendChild(viewTestButton);
            row.appendChild(testCell);
            
            // Status
            const statusCell = document.createElement('td');
            if (mutation.killed) {
                statusCell.innerHTML = '<span class="badge bg-success">Killed</span>';
            } else {
                statusCell.innerHTML = '<span class="badge bg-danger">Survived</span>';
            }
            row.appendChild(statusCell);
            
            $('#githubMutationsTable').append(row);
        });
        
        // Also update the overall results with GitHub test data
        updateResultsSummary(data);
        
        // Scroll to the results section
        scrollToResults();
    }
    
    // Update just the summary stats with any test data
    function updateResultsSummary(data) {
        // Update summary stats
        if (data && typeof data === 'object') {
            totalMutantsEl.textContent = data.total_mutants || 0;
            killedMutantsEl.textContent = data.killed_mutants || 0;
            survivingMutantsEl.textContent = data.surviving_mutants || 0;
            testEffectivenessEl.textContent = (data.test_effectiveness ? Math.round(data.test_effectiveness) : 0) + '%';
        }
    }

    /**
     * Show the loading overlay with a custom message
     * @param {string} message - The message to display in the loading overlay
     */
    function showLoading(message = 'Running tests...') {
        console.log('Showing loading overlay with message:', message);
        $('#loadingMessage').text(message);
        $('#loadingOverlay').addClass('show');
    }

    /**
     * Hide the loading overlay
     */
    function hideLoading() {
        console.log('Hiding loading overlay');
        $('#loadingOverlay').removeClass('show');
    }

    // IMPORTANT: Remove any existing handlers to avoid duplicates
    $('#customTestForm').off('submit');
    $('#githubTestForm').off('submit');

    // Handle custom code test submission
    $('#customTestForm').on('submit', function(e) {
        e.preventDefault();
        
        const functionName = $('#functionName').val().trim();
        const codeInput = $('#codeInput').val().trim();
        
        if (!functionName || !codeInput) {
            alert('Please fill in all fields');
            return;
        }
        
        showLoading('Running custom code tests...');
        
        $.ajax({
            url: '/api/custom-tests',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                function_name: functionName,
                code_input: codeInput
            }),
            success: function(data) {
                hideLoading();
                updateCustomResults(data);
                $('#customResultsContainer').show();
            },
            error: function(xhr, status, error) {
                console.error('Ajax error:', status, error);
                hideLoading();
                let errorMsg = 'An error occurred while testing';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                }
                alert(errorMsg);
            }
        });
    });

    // Handle GitHub repo test submission
    $('#githubTestForm').on('submit', function(e) {
        e.preventDefault();
        
        const repoUrl = $('#repoUrl').val().trim();
        const filePath = $('#filePath').val().trim();
        const functionName = $('#githubFunctionName').val().trim();
        
        if (!repoUrl || !filePath || !functionName) {
            alert('Please fill in all fields');
            return;
        }
        
        showLoading('Cloning repository and running tests...');
        
        $.ajax({
            url: '/api/github-tests',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                repo_url: repoUrl,
                file_path: filePath,
                function_name: functionName
            }),
            success: function(data) {
                hideLoading();
                updateGithubResults(data);
                $('#githubResultsContainer').show();
            },
            error: function(xhr, status, error) {
                console.error('Ajax error:', status, error);
                hideLoading();
                let errorMsg = 'An error occurred while testing';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                }
                alert(errorMsg);
            }
        });
    });

    // Handle the cancel button in the loading overlay
    $('#cancelOperation').on('click', function() {
        // Hide the loading overlay
        hideLoading();
        
        // Show a message to the user
        alert('Operation cancelled. Please try again if needed.');
    });
}); 