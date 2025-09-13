"""
Flask routes for the research pipeline application.
"""
from flask import jsonify, request, render_template_string
from app.pipeline.orchestrator import ResearchOrchestrator


def register_routes(app):
    """Register all routes with the Flask app."""
    
    orchestrator = ResearchOrchestrator()
    
    @app.route('/')
    def index():
        """Main page showing the research pipeline interface."""
        html_template = r'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover">
            <meta name="mobile-web-app-capable" content="yes">
            <meta name="apple-mobile-web-app-status-bar-style" content="default">
            <meta name="apple-mobile-web-app-title" content="AI Research">
            <meta name="format-detection" content="telephone=no">
            <title>AI Research Pipeline</title>
            <style>
                :root {
                    --primary-color: #007AFF;
                    --secondary-color: #5856D6;
                    --success-color: #34C759;
                    --background-color: #F2F2F7;
                    --card-background: #FFFFFF;
                    --text-primary: #000000;
                    --text-secondary: #6D6D70;
                    --border-color: #E5E5EA;
                    --shadow: 0 2px 10px rgba(0,0,0,0.1);
                    --border-radius: 12px;
                }
                
                @media (prefers-color-scheme: dark) {
                    :root {
                        --background-color: #000000;
                        --card-background: #1C1C1E;
                        --text-primary: #FFFFFF;
                        --text-secondary: #8E8E93;
                        --border-color: #38383A;
                        --shadow: 0 2px 10px rgba(0,0,0,0.3);
                    }
                }
                
                * {
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }
                
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                    background-color: var(--background-color);
                    color: var(--text-primary);
                    line-height: 1.6;
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                    padding-top: env(safe-area-inset-top);
                    padding-bottom: env(safe-area-inset-bottom);
                    min-height: 100vh;
                }
                
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                }
                
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    padding: 20px 0;
                }
                
                .header h1 {
                    font-size: 2.5rem;
                    font-weight: 700;
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin-bottom: 10px;
                }
                
                .header p {
                    color: var(--text-secondary);
                    font-size: 1.1rem;
                    max-width: 500px;
                    margin: 0 auto;
                }
                
                .query-section {
                    background: var(--card-background);
                    border-radius: var(--border-radius);
                    padding: 25px;
                    margin-bottom: 25px;
                    box-shadow: var(--shadow);
                    border: 1px solid var(--border-color);
                }
                
                .query-form {
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                }
                
                .input-group {
                    position: relative;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                
                .input-group label {
                    font-weight: 600;
                    color: var(--text-secondary);
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                #queryInput {
                    width: 100%;
                    padding: 18px 20px;
                    border: 2px solid var(--border-color);
                    border-radius: var(--border-radius);
                    font-size: 1.1rem;
                    background: var(--card-background);
                    color: var(--text-primary);
                    transition: all 0.3s ease;
                    -webkit-appearance: none;
                    appearance: none;
                }
                
                #queryInput:focus {
                    outline: none;
                    border-color: var(--primary-color);
                    box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
                }
                
                .submit-btn {
                    width: 100%;
                    padding: 18px;
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                    color: white;
                    border: none;
                    border-radius: var(--border-radius);
                    font-size: 1.1rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }
                
                .submit-btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(0, 122, 255, 0.3);
                }
                
                .submit-btn:active {
                    transform: translateY(0);
                }
                
                .submit-btn:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                    transform: none;
                }
                
                .loading-spinner {
                    display: none;
                    width: 20px;
                    height: 20px;
                    border: 2px solid transparent;
                    border-top: 2px solid white;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin-right: 10px;
                }
                
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                .result {
                    background: var(--card-background);
                    border-radius: var(--border-radius);
                    padding: 25px;
                    box-shadow: var(--shadow);
                    border: 1px solid var(--border-color);
                    display: none;
                    animation: slideIn 0.3s ease-out;
                }
                
                @keyframes slideIn {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                .result h3 {
                    color: var(--text-primary);
                    margin-bottom: 20px;
                    font-size: 1.4rem;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .result-content {
                    color: var(--text-primary);
                }
                
                .answer-section {
                    background: var(--background-color);
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    line-height: 1.8;
                    font-size: 1.05rem;
                }
                
                .sources-section {
                    margin-top: 20px;
                }
                
                .sources-section h4 {
                    color: var(--text-secondary);
                    margin-bottom: 10px;
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                .source-link {
                    display: block;
                    color: var(--primary-color);
                    text-decoration: none;
                    padding: 8px 0;
                    border-bottom: 1px solid var(--border-color);
                    transition: color 0.2s ease;
                }
                
                .source-link:hover {
                    color: var(--secondary-color);
                }
                
                .source-link:last-child {
                    border-bottom: none;
                }
                
                .confidence-badge {
                    display: inline-block;
                    background: var(--success-color);
                    color: white;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 0.85rem;
                    font-weight: 600;
                    margin-left: 10px;
                }
                
                .entities-section {
                    margin-top: 15px;
                }
                
                .entity-tag {
                    display: inline-block;
                    background: var(--border-color);
                    color: var(--text-secondary);
                    padding: 4px 10px;
                    border-radius: 15px;
                    font-size: 0.8rem;
                    margin: 2px;
                }
                
                @media (max-width: 768px) {
                    .container {
                        padding: 15px;
                    }
                    
                    .header h1 {
                        font-size: 2rem;
                    }
                    
                    .query-section, .result {
                        padding: 20px;
                    }
                    
                    #queryInput, .submit-btn {
                        padding: 16px;
                        font-size: 1rem;
                    }
                }
                
                @media (max-width: 480px) {
                    .header h1 {
                        font-size: 1.8rem;
                    }
                    
                    .query-section, .result {
                        padding: 15px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>AI Research Pipeline</h1>
                    <p>Discover comprehensive insights powered by advanced AI analysis, knowledge graphs, and intelligent synthesis</p>
                </div>
                
                <div class="query-section">
                    <form id="queryForm" class="query-form">
                        <div class="input-group">
                            <label for="queryInput">Research Question</label>
                            <input type="text" id="queryInput" placeholder="What would you like to research today?" required autocomplete="off" autocapitalize="sentences">
                        </div>
                        <button type="submit" class="submit-btn" id="submitBtn">
                            <span class="loading-spinner" id="loadingSpinner"></span>
                            <span id="btnText">Start Research</span>
                        </button>
                    </form>
                </div>
                
                <div id="result" class="result">
                    <h3>
                        <span>Research Results</span>
                        <span class="confidence-badge" id="confidenceBadge"></span>
                    </h3>
                    <div id="resultContent" class="result-content"></div>
                </div>
            </div>
            
            <script>
                // Function to format text content with proper structure
                function formatTextContent(container, text) {
                    // Handle escaped newlines from JSON and convert to actual newlines
                    const processedText = text.replace(/\\\\n/g, '\n').replace(/\\n/g, '\n');
                    
                    // Split text by double newlines for paragraphs, then by single newlines
                    const paragraphs = processedText.split('\n\n').filter(p => p.trim());
                    
                    paragraphs.forEach((paragraph, index) => {
                        if (index > 0) {
                            // Add spacing between paragraphs
                            const spacer = document.createElement('div');
                            spacer.style.height = '16px';
                            container.appendChild(spacer);
                        }
                        
                        const lines = paragraph.split('\n').filter(line => line.trim());
                        
                        if (lines.length === 1) {
                            // Single line paragraph
                            const p = document.createElement('p');
                            p.style.cssText = 'margin: 0 0 12px 0; line-height: 1.6;';
                            p.textContent = lines[0].trim();
                            container.appendChild(p);
                        } else {
                            // Multi-line content (lists or structured data)
                            const section = document.createElement('div');
                            section.style.cssText = 'margin-bottom: 16px;';
                            
                            lines.forEach(line => {
                                const trimmedLine = line.trim();
                                if (trimmedLine.charAt(0) === '•' || trimmedLine.charAt(0) === '-' || trimmedLine.charAt(0) === '*') {
                                    // Bullet point
                                    const listItem = document.createElement('div');
                                    listItem.style.cssText = 'margin: 4px 0 4px 20px; position: relative; line-height: 1.5;';
                                    
                                    const bullet = document.createElement('span');
                                    bullet.style.cssText = 'position: absolute; left: -16px; color: var(--primary-color); font-weight: bold;';
                                    bullet.textContent = '●';
                                    listItem.appendChild(bullet);
                                    
                                    const text = document.createElement('span');
                                    text.textContent = trimmedLine.substring(1).trim();
                                    listItem.appendChild(text);
                                    
                                    section.appendChild(listItem);
                                } else if (trimmedLine.startsWith('# ')) {
                                    // Main heading
                                    const heading = document.createElement('h2');
                                    heading.style.cssText = 'font-weight: 700; color: var(--text-primary); margin: 16px 0 8px 0; font-size: 1.4em; border-bottom: 2px solid var(--primary-color); padding-bottom: 4px;';
                                    heading.textContent = trimmedLine.replace('# ', '');
                                    section.appendChild(heading);
                                } else if (trimmedLine.startsWith('## ')) {
                                    // Section heading
                                    const heading = document.createElement('h3');
                                    heading.style.cssText = 'font-weight: 600; color: var(--primary-color); margin: 12px 0 6px 0; font-size: 1.2em;';
                                    heading.textContent = trimmedLine.replace('## ', '');
                                    section.appendChild(heading);
                                } else if (trimmedLine.startsWith('### ')) {
                                    // Subsection heading
                                    const heading = document.createElement('h4');
                                    heading.style.cssText = 'font-weight: 600; color: var(--text-primary); margin: 10px 0 4px 0; font-size: 1.1em;';
                                    heading.textContent = trimmedLine.replace('### ', '');
                                    section.appendChild(heading);
                                } else if (trimmedLine.startsWith('---')) {
                                    // Horizontal rule
                                    const hr = document.createElement('hr');
                                    hr.style.cssText = 'border: none; border-top: 1px solid var(--border-color); margin: 16px 0;';
                                    section.appendChild(hr);
                                } else if (trimmedLine.charAt(0) === '*' && trimmedLine.charAt(trimmedLine.length - 1) === '*' && trimmedLine.charAt(1) !== ' ') {
                                    // Italic text (emphasis)
                                    const emphasis = document.createElement('div');
                                    emphasis.style.cssText = 'font-style: italic; color: var(--text-secondary); margin: 8px 0; font-size: 0.95em;';
                                    emphasis.textContent = trimmedLine.substring(1, trimmedLine.length - 1);
                                    section.appendChild(emphasis);
                                } else if (trimmedLine.includes(':') && trimmedLine.length < 100) {
                                    // Regular heading or label
                                    const heading = document.createElement('div');
                                    heading.style.cssText = 'font-weight: 600; color: var(--text-primary); margin: 8px 0 4px 0; font-size: 1.05em;';
                                    heading.textContent = trimmedLine;
                                    section.appendChild(heading);
                                } else if (trimmedLine) {
                                    // Regular text line
                                    const textLine = document.createElement('div');
                                    textLine.style.cssText = 'margin: 4px 0; line-height: 1.6;';
                                    textLine.textContent = trimmedLine;
                                    section.appendChild(textLine);
                                }
                            });
                            
                            container.appendChild(section);
                        }
                    });
                }
                
                document.getElementById('queryForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    const query = document.getElementById('queryInput').value.trim();
                    if (!query) return;
                    
                    const resultDiv = document.getElementById('result');
                    const resultContent = document.getElementById('resultContent');
                    const submitBtn = document.getElementById('submitBtn');
                    const loadingSpinner = document.getElementById('loadingSpinner');
                    const btnText = document.getElementById('btnText');
                    const confidenceBadge = document.getElementById('confidenceBadge');
                    
                    // Show loading state
                    submitBtn.disabled = true;
                    loadingSpinner.style.display = 'inline-block';
                    btnText.textContent = 'Researching...';
                    resultDiv.style.display = 'block';
                    resultContent.innerHTML = '<div style="text-align: center; padding: 20px; color: var(--text-secondary);">Analyzing your query and gathering insights...</div>';
                    
                    try {
                        const response = await fetch('/query', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({query: query})
                        });
                        
                        if (!response.ok) {
                            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                        }
                        
                        const data = await response.json();
                        
                        if (data.status === 'success' && data.result) {
                            const result = data.result;
                            
                            // Update confidence badge
                            const confidence = Math.round((result.confidence || 0) * 100);
                            confidenceBadge.textContent = `${confidence}% Confidence`;
                            
                            // Safely format the response using DOM manipulation
                            resultContent.innerHTML = ''; // Clear content first
                            
                            // Create answer section with proper formatting
                            const answerDiv = document.createElement('div');
                            answerDiv.className = 'answer-section';
                            
                            // Format the answer text properly
                            const answerText = result.answer || 'No answer generated';
                            formatTextContent(answerDiv, answerText);
                            
                            resultContent.appendChild(answerDiv);
                            
                            // Create sources section safely
                            if (result.sources && result.sources.length > 0) {
                                const sourcesDiv = document.createElement('div');
                                sourcesDiv.className = 'sources-section';
                                
                                const sourcesTitle = document.createElement('h4');
                                sourcesTitle.textContent = 'Sources';
                                sourcesDiv.appendChild(sourcesTitle);
                                
                                result.sources.forEach(source => {
                                    const sourceElement = document.createElement('div');
                                    sourceElement.className = 'source-link';
                                    sourceElement.style.cursor = 'default';
                                    sourceElement.textContent = source;
                                    sourcesDiv.appendChild(sourceElement);
                                });
                                
                                resultContent.appendChild(sourcesDiv);
                            }
                            
                            // Create entities section safely
                            if (result.entities && result.entities.length > 0) {
                                const entitiesDiv = document.createElement('div');
                                entitiesDiv.className = 'entities-section';
                                
                                const entitiesTitle = document.createElement('h4');
                                entitiesTitle.style.cssText = 'color: var(--text-secondary); margin-bottom: 10px; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;';
                                entitiesTitle.textContent = 'Key Entities';
                                entitiesDiv.appendChild(entitiesTitle);
                                
                                result.entities.forEach(entity => {
                                    const entitySpan = document.createElement('span');
                                    entitySpan.className = 'entity-tag';
                                    entitySpan.textContent = entity;
                                    entitiesDiv.appendChild(entitySpan);
                                });
                                
                                resultContent.appendChild(entitiesDiv);
                            }
                        } else {
                            throw new Error(data.error || 'Unknown error occurred');
                        }
                        
                    } catch (error) {
                        console.error('Research error:', error);
                        
                        // Safely create error message
                        resultContent.innerHTML = '';
                        const errorDiv = document.createElement('div');
                        errorDiv.style.cssText = 'background: #FF3B30; color: white; padding: 15px; border-radius: 8px; text-align: center;';
                        
                        const errorTitle = document.createElement('strong');
                        errorTitle.textContent = 'Error';
                        errorDiv.appendChild(errorTitle);
                        
                        errorDiv.appendChild(document.createElement('br'));
                        
                        const errorText = document.createTextNode(
                            error.message || 'Failed to process your research query. Please try again.'
                        );
                        errorDiv.appendChild(errorText);
                        
                        resultContent.appendChild(errorDiv);
                        confidenceBadge.textContent = '0% Confidence';
                    } finally {
                        // Reset button state
                        submitBtn.disabled = false;
                        loadingSpinner.style.display = 'none';
                        btnText.textContent = 'Start Research';
                    }
                });
                
                // Auto-focus input on mobile
                if (window.innerWidth <= 768) {
                    setTimeout(() => {
                        document.getElementById('queryInput').focus();
                    }, 100);
                }
            </script>
        </body>
        </html>
        '''
        return render_template_string(html_template)
    
    @app.route('/query', methods=['POST'])
    def query():
        """Process a research query through the pipeline."""
        try:
            data = request.get_json()
            if not data or 'query' not in data:
                return jsonify({'error': 'Query is required'}), 400
            
            query_text = data['query']
            
            # Run the research pipeline
            result = orchestrator.run_pipeline(query_text)
            
            return jsonify({
                'status': 'success',
                'query': query_text,
                'result': result
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': 'research-pipeline',
            'version': '1.0.0'
        })