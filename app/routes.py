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
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Research Pipeline</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .query-form { margin: 20px 0; }
                input[type="text"] { width: 60%; padding: 10px; }
                button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
                .result { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>AI Research Pipeline</h1>
                <p>Welcome to the AI-powered research system. Enter your research query below:</p>
                
                <div class="query-form">
                    <form id="queryForm">
                        <input type="text" id="queryInput" placeholder="Enter your research question..." required>
                        <button type="submit">Research</button>
                    </form>
                </div>
                
                <div id="result" class="result" style="display: none;">
                    <h3>Research Results:</h3>
                    <div id="resultContent"></div>
                </div>
            </div>
            
            <script>
                document.getElementById('queryForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    const query = document.getElementById('queryInput').value;
                    const resultDiv = document.getElementById('result');
                    const resultContent = document.getElementById('resultContent');
                    
                    resultDiv.style.display = 'block';
                    resultContent.innerHTML = 'Processing your research query...';
                    
                    try {
                        const response = await fetch('/query', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({query: query})
                        });
                        const data = await response.json();
                        resultContent.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    } catch (error) {
                        resultContent.innerHTML = 'Error: ' + error.message;
                    }
                });
            </script>
        </body>
        </html>
        """
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