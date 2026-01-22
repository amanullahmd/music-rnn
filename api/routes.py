"""
API routes for music generation
"""
import logging
import os
from flask import Blueprint, request, jsonify, current_app, send_file
from services.model_loader import ModelLoader
from services.validator import InputValidator
from services.generator import MusicGenerator
from services.audio_converter import AudioConverter

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Initialize services
model_loader = None
validator = InputValidator()
generator = None
audio_converter = None

def init_services():
    """Initialize services on first request"""
    global model_loader, generator, audio_converter
    if model_loader is None:
        model_loader = ModelLoader(current_app.config['MODEL_PATH'])
        generator = MusicGenerator(model_loader)
        audio_converter = AudioConverter()

@api_bp.before_request
def before_request():
    """Initialize services before first request"""
    init_services()

@api_bp.route('/generate', methods=['POST'])
def generate():
    """
    Generate music based on provided parameters
    
    Request JSON:
    {
        "seed": "string (optional)",
        "temperature": float (0.1-2.0),
        "length": int (50-500)
    }
    
    Response JSON:
    {
        "notation": "string",
        "timestamp": "ISO 8601 datetime",
        "parameters": {
            "seed": "string",
            "temperature": float,
            "length": int
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        validation_result = validator.validate(data)
        if not validation_result['valid']:
            logger.warning(f'Invalid input: {validation_result["errors"]}')
            return jsonify({'error': validation_result['errors']}), 400
        
        # Extract validated parameters
        seed = validation_result['data']['seed']
        temperature = validation_result['data']['temperature']
        length = validation_result['data']['length']
        
        logger.info(f'Generating music with seed="{seed}", temp={temperature}, len={length}')
        
        # Generate music
        result = generator.generate(seed, temperature, length)
        
        logger.info('Music generation successful')
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'Generation error: {str(e)}', exc_info=True)
        return jsonify({'error': 'Generation failed', 'details': str(e)}), 500

@api_bp.route('/generate-mp4', methods=['POST'])
def generate_mp4():
    """
    Generate WAV audio file from ABC notation
    
    Request JSON:
    {
        "notation": "string (ABC notation)"
    }
    
    Response: WAV file download
    """
    try:
        data = request.get_json()
        notation = data.get('notation', '')
        
        if not notation or notation.strip() == '':
            return jsonify({'error': 'No notation provided'}), 400
        
        logger.info('Generating WAV audio from ABC notation...')
        
        # Convert ABC to WAV
        audio_path = audio_converter.abc_to_wav(notation)
        
        if not os.path.exists(audio_path):
            return jsonify({'error': 'Audio generation failed'}), 500
        
        logger.info(f'WAV generated successfully: {audio_path}')
        
        # Send file
        timestamp = os.path.basename(audio_path).split('.')[0]
        return send_file(
            audio_path,
            mimetype='audio/wav',
            as_attachment=True,
            download_name=f'music_{timestamp}.wav'
        )
        
    except Exception as e:
        logger.error(f'Audio generation error: {str(e)}', exc_info=True)
        return jsonify({'error': 'Audio generation failed', 'details': str(e)}), 500

@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        model_loaded = model_loader is not None and model_loader.model is not None
        return jsonify({
            'status': 'ok',
            'model_loaded': model_loaded
        }), 200
    except Exception as e:
        logger.error(f'Health check error: {str(e)}')
        return jsonify({
            'status': 'error',
            'model_loaded': False
        }), 500
