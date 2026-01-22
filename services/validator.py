"""
Input validation service for generation requests
"""
import logging

logger = logging.getLogger(__name__)

class InputValidator:
    """Validates generation request parameters"""
    
    # Constants for validation
    DEFAULT_SEED = "X:1\nM:4/4\nL:1/8"
    MAX_SEED_LENGTH = 50
    MIN_TEMPERATURE = 0.1
    MAX_TEMPERATURE = 2.0
    TEMPERATURE_STEP = 0.1
    MIN_LENGTH = 50
    MAX_LENGTH = 500
    LENGTH_STEP = 10
    
    def validate(self, data):
        """
        Validate generation request parameters
        
        Args:
            data: Dictionary with 'seed', 'temperature', 'length' keys
        
        Returns:
            Dictionary with 'valid' (bool), 'data' (dict), and 'errors' (list)
        """
        errors = []
        validated_data = {}
        
        # Validate seed (optional)
        seed = data.get('seed', '')
        if seed is None:
            seed = ''
        
        if not isinstance(seed, str):
            errors.append('Seed must be a string')
        elif len(seed) > self.MAX_SEED_LENGTH:
            errors.append(f'Seed must be at most {self.MAX_SEED_LENGTH} characters')
        
        # Use default seed if empty
        if seed == '':
            seed = self.DEFAULT_SEED
        
        validated_data['seed'] = seed
        
        # Validate temperature (required)
        if 'temperature' not in data:
            errors.append('Temperature is required')
        else:
            temperature = data.get('temperature')
            
            if not isinstance(temperature, (int, float)):
                errors.append('Temperature must be a number')
            elif temperature < self.MIN_TEMPERATURE or temperature > self.MAX_TEMPERATURE:
                errors.append(f'Temperature must be between {self.MIN_TEMPERATURE} and {self.MAX_TEMPERATURE}')
            else:
                # Round to nearest step (0.1)
                rounded = round(temperature * 10) / 10
                validated_data['temperature'] = round(rounded, 1)
        
        # Validate length (required)
        if 'length' not in data:
            errors.append('Length is required')
        else:
            length = data.get('length')
            
            if not isinstance(length, int):
                errors.append('Length must be an integer')
            elif length < self.MIN_LENGTH or length > self.MAX_LENGTH:
                errors.append(f'Length must be between {self.MIN_LENGTH} and {self.MAX_LENGTH}')
            elif length % self.LENGTH_STEP != 0:
                errors.append(f'Length must be a multiple of {self.LENGTH_STEP}')
            else:
                validated_data['length'] = length
        
        return {
            'valid': len(errors) == 0,
            'data': validated_data if len(errors) == 0 else {},
            'errors': errors
        }
