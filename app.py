"""
Music Generation GUI - Flask Application
Main entry point for the web application
"""
import os
import logging
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from config.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configuration from environment variables
app.config['MODEL_PATH'] = os.getenv('MODEL_PATH', 'best_model.pt')
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
app.config['PORT'] = int(os.getenv('PORT', 5000))

# Import blueprints
from api.routes import api_bp

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'model_loaded': True})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f'Internal server error: {error}')
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info(f'Starting Music Generation GUI on port {app.config["PORT"]}')
    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
