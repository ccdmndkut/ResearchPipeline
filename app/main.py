"""
Research Pipeline Flask Application
Main entry point for the AI research pipeline.
"""
import os
import sys
from flask import Flask

# Add the parent directory to Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routes import register_routes


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    app.config['DEBUG'] = True
    
    # Register routes
    register_routes(app)
    
    return app


def run_dev():
    """Run the application in development mode."""
    app = create_app()
    # IMPORTANT: Allow all hosts for Replit environment
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    run_dev()