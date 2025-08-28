let trafficData = [];
let selectedTraffic = null;

// Add event listeners once DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('loadTraffic').addEventListener('click', loadTrafficData);
    document.getElementById('searchBox').addEventListener('input', updateTrafficList);
    document.getElementById('clearTraffic').addEventListener('click', clearTrafficData);
    
    // Automatically load traffic data when page loads
    loadTrafficData();
    
    // Set up auto-refresh every 5 seconds
    setInterval(loadTrafficData, 5000);
    
    // Active Scan Button Handler with improved error handling
    const activeBtn = document.getElementById('activeScanBtn');
    const resultsContainer = document.getElementById('results');
    if (activeBtn && resultsContainer) {
        activeBtn.addEventListener('click', () => {
            resultsContainer.innerHTML = '<p class="loading">🔍 Running Active Scan...</p>';
            fetch('/api/active_scan')
                .then(r => r.json())
                .then(data => {
                    resultsContainer.innerHTML = '';
                    const findings = (data && data.findings) || [];
                    if (!findings.length) {
                        resultsContainer.innerHTML = '<p class="no-findings">✅ No issues found during active scan.</p>';
                        return;
                    }
                    findings.forEach(f => {
                        const div = document.createElement('div');
                        div.className = 'finding';
                        div.innerHTML = `
                            <div class="finding-title">${f.title}
                                <span class="finding-severity severity-${(f.severity||'Info').toLowerCase()}">${f.severity||'Info'}</span>
                            </div>
                            <p><em>${f.url||''}</em></p>
                            <p>${f.description||''}</p>
                            <p><strong>Remediation:</strong> ${f.remediation||''}</p>
                        `;
                        resultsContainer.appendChild(div);
                    });
                })
                .catch(err => {
                    resultsContainer.innerHTML = `<p class="error">⚠️ Error running active scan: ${err.message}</p>`;
                });
        });
    }

    // Load session cookies
    loadSessionCookies();

    // Clear session cookies button handler
    const clearBtn = document.getElementById('clearSessionCookies');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            fetch('http://localhost:8080/api/session/cookies', { method: 'DELETE' })
                .then(r => r.json())
                .then(() => {
                    loadSessionCookies();
                });
        });
    }
});

// Tab switching logic
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab + 'View').classList.add('active');
    });
});

function loadTrafficData() {
    console.log('Loading traffic data...');
    document.getElementById('trafficItems').innerHTML = '<div class="no-data">Loading traffic data...</div>';
    
    fetch('/api/traffic')
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) throw new Error(`Failed to load traffic data (Status: ${response.status})`);
            return response.json();
        })
        .then(data => {
            console.log('Traffic data loaded:', data.length, 'entries');
            trafficData = data;
            updateTrafficList();
            document.getElementById('detailHeader').innerHTML = 
                `<h2>HTTP Traffic Inspector</h2><p>Loaded ${data.length} request(s)</p>`;
        })
        .catch(error => {
            console.error('Error loading traffic data:', error);
            document.getElementById('trafficItems').innerHTML =
                `<div class="no-data">Error loading traffic data: ${error.message}</div>`;
        });
}

function clearTrafficData() {
    // Display loading message
    document.getElementById('trafficItems').innerHTML = '<div class="no-data">Clearing traffic data...</div>';
    document.getElementById('detailHeader').innerHTML = '<h2>HTTP Traffic Inspector</h2><p>Clearing traffic data...</p>';
    
    // Call the API to clear the traffic.json file
    fetch('/api/clear')
        .then(response => {
            if (!response.ok) throw new Error(`Failed to clear traffic data (Status: ${response.status})`);
            return response.json();
        })
        .then(data => {
            console.log('Traffic data cleared:', data);
            
            // Clear the data in memory
            trafficData = [];
            selectedTraffic = null;
            
            // Update the UI
            updateTrafficList();
            
            // Clear the detail views
            document.getElementById('requestView').innerHTML = '<div class="no-data">No request selected</div>';
            document.getElementById('responseView').innerHTML = '<div class="no-data">No response selected</div>';
            document.getElementById('findingsView').innerHTML = '<div class="no-data">No security findings available</div>';
            
            // Update header with success message
            document.getElementById('detailHeader').innerHTML = '<h2>HTTP Traffic Inspector</h2><p>✅ Traffic data cleared successfully</p>';
        })
        .catch(error => {
            console.error('Error clearing traffic data:', error);
            document.getElementById('trafficItems').innerHTML =
                `<div class="no-data">Error clearing traffic data: ${error.message}</div>`;
            document.getElementById('detailHeader').innerHTML = 
                `<h2>HTTP Traffic Inspector</h2><p>❌ Error: ${error.message}</p>`;
        });
}

function updateTrafficList() {
    const trafficList = document.getElementById('trafficItems');
    const searchText = document.getElementById('searchBox').value.toLowerCase();

    if (!trafficData || trafficData.length === 0) {
        trafficList.innerHTML = '<div class="no-data">No traffic data available</div>';
        return;
    }

    trafficList.innerHTML = '';
    let matchFound = false;

    trafficData.forEach((item, index) => {
        const fullText = JSON.stringify(item).toLowerCase();
        if (!searchText || fullText.includes(searchText)) {
            matchFound = true;
            const trafficItem = document.createElement('div');
            trafficItem.className = 'traffic-item';
            trafficItem.dataset.index = index;
            
            // Store the entry ID in a data attribute if available
            if (item.id) {
                trafficItem.dataset.id = item.id;
            }

            const methodClass = `method-${item.method}`;
            const statusClass = `status-${Math.floor(item.response_code / 100)}xx`;

            trafficItem.innerHTML = `
                <span class="method ${methodClass}">${item.method}</span>
                <span class="status-code ${statusClass}">${item.response_code}</span>
                <span class="path">${item.path}</span>
            `;

            const bodyString = JSON.stringify(item.request_body || '').toLowerCase();
            if (bodyString.includes('password') || bodyString.includes('eyj')) {
                trafficItem.style.backgroundColor = '#4a1c1c';
            }

            trafficItem.addEventListener('click', () => {
                // Pass both index and ID to selectTraffic
                selectTraffic(index, item.id);
            });

            trafficList.appendChild(trafficItem);
        }
    });

    if (!matchFound) {
        trafficList.innerHTML = '<div class="no-data">No matches found for your search.</div>';
    }
}

function selectTraffic(index, id) {
    // Clear previous selection
    document.querySelectorAll('.traffic-item.selected').forEach(item => {
        item.classList.remove('selected');
    });

    // Highlight the selected item
    document.querySelector(`.traffic-item[data-index="${index}"]`).classList.add('selected');
    
    // If an ID is provided, fetch the complete entry data by ID
    if (id) {
        // Show loading indicator
        document.getElementById('requestView').innerHTML = '<div class="loading">Loading request details...</div>';
        document.getElementById('responseView').innerHTML = '<div class="loading">Loading response details...</div>';
        
        fetch(`/api/db/entry?id=${id}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to load entry (Status: ${response.status})`);
                }
                return response.json();
            })
            .then(data => {
                // Check if the response contains an error
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Update the selected traffic with the full entry data
                selectedTraffic = data;
                
                // Update all views with the complete data
                updateRequestView();
                updateResponseView();
                updateFindingsView();
            })
            .catch(error => {
                console.error('Error loading entry details:', error);
                // If there's an error, fall back to using the array index
                selectedTraffic = trafficData[index];
                updateRequestView();
                updateResponseView();
                updateFindingsView();
            });
    } else {
        // If no ID is provided, use the array index as before (fallback)
        selectedTraffic = trafficData[index];
        updateRequestView();
        updateResponseView();
        updateFindingsView();
    }
}

function updateRequestView() {
    const requestView = document.getElementById('requestView');
    if (!selectedTraffic) {
        requestView.innerHTML = '<div class="no-data">No request selected</div>';
        return;
    }

    let headersHTML = '';
    for (const [key, value] of Object.entries(selectedTraffic.request_headers)) {
        headersHTML += `<div><span class="header-name">${key}:</span> ${value}</div>`;
    }
    
    // Add ID display if available
    const idDisplay = selectedTraffic.id ? 
        `<div class="entry-id">ID: <span class="id-value">${selectedTraffic.id}</span></div>` : '';

    requestView.innerHTML = `
        <h3>${selectedTraffic.method} ${selectedTraffic.path}</h3>
        ${idDisplay}
        <h4>Headers:</h4>
        <div class="headers">${headersHTML}</div>
        <h4>Body:</h4>
        <pre>${formatBody(selectedTraffic.request_body)}</pre>
    `;
}

function updateResponseView() {
    const responseView = document.getElementById('responseView');
    if (!selectedTraffic) {
        responseView.innerHTML = '<div class="no-data">No response selected</div>';
        return;
    }

    let headersHTML = '';
    for (const [key, value] of Object.entries(selectedTraffic.response_headers || {})) {
        headersHTML += `<div><span class="header-name">${key}:</span> ${value}</div>`;
    }

    const statusClass = `status-${Math.floor(selectedTraffic.response_code / 100)}xx`;
    
    // Calculate response time if available
    let responseTimeDisplay = '';
    if (selectedTraffic.timestamp && selectedTraffic.response_timestamp) {
        const requestTime = new Date(selectedTraffic.timestamp);
        const responseTime = new Date(selectedTraffic.response_timestamp);
        const elapsedMs = responseTime - requestTime;
        responseTimeDisplay = `<div class="response-time">Response time: ${elapsedMs}ms</div>`;
    }

    responseView.innerHTML = `
        <h3>Response <span class="status-code ${statusClass}">${selectedTraffic.response_code}</span></h3>
        ${responseTimeDisplay}
        <h4>Headers:</h4>
        <div class="headers">${headersHTML}</div>
        <h4>Body:</h4>
        <pre>${formatBody(selectedTraffic.response_body)}</pre>
    `;
}

function updateFindingsView() {
    const findingsView = document.getElementById('findingsView');

    if (!selectedTraffic || !selectedTraffic.response_headers) {
        findingsView.innerHTML = '<div class="no-data">No findings available</div>';
        return;
    }

    const findings = [];
    const headers = selectedTraffic.response_headers;
    const headersLowerCase = {};
    for (const key in headers) {
        headersLowerCase[key.toLowerCase()] = headers[key];
    }

    if (!headersLowerCase['content-security-policy']) {
        findings.push({
            severity: 'medium',
            title: 'Missing Content-Security-Policy Header',
            description: 'The Content-Security-Policy header is missing, which could make the site vulnerable to XSS attacks.',
            remediation: 'Add a Content-Security-Policy header to responses.'
        });
    }

    if (!headersLowerCase['x-frame-options']) {
        findings.push({
            severity: 'low',
            title: 'Missing X-Frame-Options Header',
            description: 'The X-Frame-Options header is missing, which could make the site vulnerable to clickjacking attacks.',
            remediation: 'Add X-Frame-Options header with value DENY or SAMEORIGIN.'
        });
    }

    if (headersLowerCase['set-cookie']) {
        const cookieHeader = headersLowerCase['set-cookie'];
        if (!cookieHeader.includes('httponly')) {
            findings.push({
                severity: 'medium',
                title: 'Cookie Without HttpOnly Flag',
                description: 'A cookie is set without the HttpOnly flag, which could make it accessible to client-side scripts.',
                remediation: 'Add HttpOnly flag to cookies.'
            });
        }
        if (!cookieHeader.includes('secure')) {
            findings.push({
                severity: 'medium',
                title: 'Cookie Without Secure Flag',
                description: 'A cookie is set without the Secure flag, which could allow it to be transmitted over unencrypted connections.',
                remediation: 'Add Secure flag to cookies.'
            });
        }
    }

    if (findings.length === 0) {
        findingsView.innerHTML = '<div class="findings-panel">No security issues found</div>';
        return;
    }

    let findingsHTML = '<div class="findings-panel">';
    findings.forEach(finding => {
        findingsHTML += `
            <div class="finding ${finding.severity}">
                <div class="finding-title">
                    ${finding.title}
                    <span class="finding-severity severity-${finding.severity}">${finding.severity}</span>
                </div>
                <p>${finding.description}</p>
                <p><strong>Remediation:</strong> ${finding.remediation}</p>
            </div>
        `;
    });
    findingsHTML += '</div>';
    findingsView.innerHTML = findingsHTML;
}

// --- Session Cookie Management ---
function loadSessionCookies() {
    const container = document.getElementById('sessionCookies');
    container.innerHTML = '<p>Loading session cookies...</p>';
    fetch('http://localhost:8080/api/session/cookies')
        .then(r => r.json())
        .then(cookies => {
            if (Object.keys(cookies).length === 0) {
                container.innerHTML = '<p>No session cookies set.</p>';
                return;
            }
            let html = '<ul class="cookie-list">';
            for (const [k, v] of Object.entries(cookies)) {
                html += `<li><span class="cookie-name">${k}</span>: <span class="cookie-value">${v}</span></li>`;
            }
            html += '</ul>';
            container.innerHTML = html;
        })
        .catch(err => {
            container.innerHTML = `<p class="error">Error loading cookies: ${err.message}</p>`;
        });
}

document.addEventListener('DOMContentLoaded', () => {
    // ...existing code...
    loadSessionCookies();
    const clearBtn = document.getElementById('clearSessionCookies');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            fetch('http://localhost:8080/api/session/cookies', { method: 'DELETE' })
                .then(r => r.json())
                .then(() => {
                    loadSessionCookies();
                });
        });
    }
});
// --- End Session Cookie Management ---

function formatBody(body) {
    if (!body) return '<em>(empty)</em>';
    try {
        const json = JSON.parse(body);
        return JSON.stringify(json, null, 2);
    } catch (e) {
        return body;
    }
}

