"""
Model loader service for loading and caching the RNN model
"""
import logging
import torch
import torch.nn as nn
import os

logger = logging.getLogger(__name__)

class CharRNN(nn.Module):
    """Simple character-level RNN model for music generation"""
    
    def __init__(self, vocab_size, hidden_size=256, num_layers=2):
        super(CharRNN, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.embedding = nn.Embedding(vocab_size, 128)
        self.rnn = nn.LSTM(128, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, vocab_size)
    
    def forward(self, x):
        embedded = self.embedding(x)
        rnn_out, _ = self.rnn(embedded)
        logits = self.fc(rnn_out)
        return logits

class ModelLoader:
    """Loads and caches the RNN model"""
    
    def __init__(self, model_path):
        """
        Initialize the model loader
        
        Args:
            model_path: Path to the model file (best_model.pt)
        """
        self.model_path = model_path
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the model from disk"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f'Model file not found: {self.model_path}')
            
            logger.info(f'Loading model from {self.model_path}')
            loaded_data = torch.load(self.model_path, map_location='cpu')
            
            # Check if it's a state dict or a full model
            if isinstance(loaded_data, dict):
                # It's a state dict - need to reconstruct the model
                if 'model_state_dict' in loaded_data:
                    # Saved with state dict key
                    state_dict = loaded_data['model_state_dict']
                    vocab_size = loaded_data.get('vocab_size', 100)
                    hidden_size = loaded_data.get('hidden_size', 256)
                    num_layers = loaded_data.get('num_layers', 2)
                else:
                    # Direct state dict
                    state_dict = loaded_data
                    # Infer vocab size from output layer
                    if 'fc.weight' in state_dict:
                        vocab_size = state_dict['fc.weight'].shape[0]
                    else:
                        vocab_size = 100
                    hidden_size = 256
                    num_layers = 2
                
                # Create model and load state
                self.model = CharRNN(vocab_size, hidden_size, num_layers)
                self.model.load_state_dict(state_dict)
                logger.info(f'Loaded model state dict (vocab_size={vocab_size}, hidden_size={hidden_size})')
            else:
                # It's a full model object
                self.model = loaded_data
                logger.info('Loaded full model object')
            
            # Set to eval mode
            if hasattr(self.model, 'eval'):
                self.model.eval()
            
            logger.info('Model loaded successfully')
            
        except Exception as e:
            logger.error(f'Failed to load model: {str(e)}')
            raise
    
    def get_model(self):
        """
        Get the cached model
        
        Returns:
            The loaded PyTorch model
        """
        if self.model is None:
            raise RuntimeError('Model not loaded')
        return self.model

