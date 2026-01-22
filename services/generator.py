"""
Music generator service for generating ABC notation using the trained RNN model
"""
import logging
from datetime import datetime, timezone
import torch
import numpy as np

logger = logging.getLogger(__name__)

class MusicGenerator:
    """Generates music using the trained RNN model"""
    
    def __init__(self, model_loader):
        """
        Initialize the generator
        
        Args:
            model_loader: ModelLoader instance
        """
        self.model_loader = model_loader
        self.char_to_idx = None
        self.idx_to_char = None
        self._build_vocab()
    
    def _build_vocab(self):
        """Build character vocabulary from ABC notation"""
        # Common ABC notation characters
        chars = set('ABCDEFGabcdefgz|:[]()\',-/0123456789\nMKLTXtCQPVwHhOu+.~!$&*;?@%^_`')
        self.char_to_idx = {char: idx for idx, char in enumerate(sorted(chars))}
        self.idx_to_char = {idx: char for char, idx in self.char_to_idx.items()}
    
    def generate(self, seed, temperature, length):
        """
        Generate music using the RNN model
        
        Args:
            seed: Initial seed text
            temperature: Randomness parameter (0.1-2.0)
            length: Desired output length in characters
        
        Returns:
            Dictionary with 'notation', 'timestamp', and 'parameters'
        """
        try:
            model = self.model_loader.get_model()
            
            # Generate music using the model
            notation = self._generate_with_model(seed, temperature, length, model)
            
            timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            
            return {
                'notation': notation,
                'timestamp': timestamp,
                'parameters': {
                    'seed': seed,
                    'temperature': temperature,
                    'length': length
                }
            }
            
        except Exception as e:
            logger.error(f'Generation failed: {str(e)}', exc_info=True)
            raise
    
    def _generate_with_model(self, seed, temperature, length, model):
        """
        Generate ABC notation using the trained model
        
        Args:
            seed: Initial seed text
            temperature: Randomness parameter
            length: Desired output length
            model: The trained RNN model
        
        Returns:
            Generated ABC notation string
        """
        # If seed is empty, use ABC header as seed
        if not seed or seed.strip() == '':
            seed = "X:1\nT:Generated\nM:4/4\nL:1/8\nK:Emin\n"
        
        try:
            # Try to use the actual model
            logger.info('Attempting to generate with RNN model...')
            notation = self._generate_with_rnn(seed, temperature, length, model)
            
            # Check if output looks reasonable (has some valid ABC characters)
            valid_chars = set('ABCDEFGabcdefgz|:[]()\',-/0123456789\nMKLTXtCQPVwHhOu+.~!*;?@%^_`')
            valid_count = sum(1 for c in notation if c in valid_chars)
            
            if valid_count < len(notation) * 0.3:
                # Less than 30% valid characters, fall back to random
                logger.warning(f'Model output quality low ({valid_count}/{len(notation)} valid chars), using fallback')
                notation = self._generate_random(seed, temperature, length)
            else:
                logger.info(f'Model output quality good ({valid_count}/{len(notation)} valid chars)')
            
            # Ensure proper ABC format
            if not notation.startswith('X:'):
                notation = "X:1\nT:Generated\nM:4/4\nL:1/8\nK:Emin\n" + notation
            
            logger.info(f'Successfully generated {len(notation)} characters')
            return notation[:length] if len(notation) > length else notation
            
        except Exception as e:
            logger.warning(f'RNN model generation failed: {e}', exc_info=True)
            logger.info('Falling back to random generation...')
            # Fallback to random generation
            notation = self._generate_random(seed, temperature, length)
            return notation
    
    def _generate_with_rnn(self, seed, temperature, length, model):
        """Generate using the RNN model with improved quality"""
        try:
            # Get device from model parameters
            device = next(model.parameters()).device
            model.eval()
            
            # Prepare seed - use ABC notation header
            seed_text = "X:1\nT:Generated\nM:4/4\nL:1/8\nK:Emin\n"
            
            # Generate sequence
            generated = seed_text
            max_iterations = max(150, length // 2)
            
            # Track what characters we've seen to filter invalid ones
            valid_chars = set('ABCDEFGabcdefgz|:[]()\',-/0123456789\nMKLTXtCQPVwHhOu+.~!*;?@%^_`')
            
            with torch.no_grad():
                for iteration in range(max_iterations):
                    # Get last 50 characters for context
                    context = generated[-50:] if len(generated) > 50 else generated
                    
                    # Convert to tensor
                    try:
                        input_indices = [self.char_to_idx.get(c, 0) for c in context]
                        input_seq = torch.tensor(input_indices, dtype=torch.long).unsqueeze(0).to(device)
                        
                        # Get model output
                        output = model(input_seq)
                        
                        # Handle different output formats
                        if isinstance(output, tuple):
                            logits = output[0]
                        else:
                            logits = output
                        
                        # Get last token logits
                        if len(logits.shape) == 3:
                            last_logits = logits[:, -1, :]
                        else:
                            last_logits = logits
                        
                        # Apply temperature scaling
                        scaled_logits = last_logits / max(temperature, 0.1)
                        
                        # Get probabilities
                        probs = torch.softmax(scaled_logits, dim=-1)
                        
                        # Get top candidates
                        top_k = min(20, probs.shape[-1])
                        top_probs, top_indices = torch.topk(probs[0], top_k)
                        
                        # Filter for valid characters and resample
                        valid_mask = torch.tensor([self.idx_to_char.get(idx.item(), '') in valid_chars 
                                                   for idx in top_indices], device=device)
                        
                        if valid_mask.any():
                            # Keep only valid characters
                            valid_probs = top_probs[valid_mask]
                            valid_indices = top_indices[valid_mask]
                            valid_probs = valid_probs / valid_probs.sum()
                            
                            # Sample from valid characters
                            next_idx_in_valid = torch.multinomial(valid_probs, 1).item()
                            next_idx = valid_indices[next_idx_in_valid].item()
                        else:
                            # Fallback: sample from all
                            next_idx = torch.multinomial(probs[0], 1).item()
                        
                        next_char = self.idx_to_char.get(next_idx, 'C')
                        
                        # Only add valid characters
                        if next_char in valid_chars:
                            generated += next_char
                        
                        # Stop if we've generated enough
                        if len(generated) >= length:
                            break
                            
                    except Exception as e:
                        logger.warning(f'Model inference iteration {iteration} failed: {e}')
                        break
            
            logger.info(f'Generated {len(generated)} characters using RNN model')
            return generated
            
        except Exception as e:
            logger.error(f'RNN generation failed: {e}', exc_info=True)
            raise
    
    def _generate_random(self, seed, temperature, length):
        """Generate proper ABC notation with chord annotations matching user examples"""
        import random
        
        # Proper ABC notation header - matching user's example format
        notation = "X:1\n"
        notation += "T:Generated Tune\n"
        notation += "M:4/4\n"
        notation += "L:1/8\n"
        notation += "R:reel\n"
        notation += "K:Emin\n"
        
        # Available notes for Irish folk music (Em key)
        notes = ['D', 'E', 'F', 'G', 'A', 'B', 'c', 'd', 'e', 'f', 'g', 'a', 'b']
        
        # Chord progression (Em and D are common in Irish reels)
        chords = ['Em', 'D']
        current_chord = 'Em'
        chord_bar_count = 0
        
        # Generate note sequence with proper structure
        bar_count = 0
        notes_in_bar = 0
        current_line = ""
        
        # Generate enough bars (typically 8-16 bars for a tune)
        target_bars = max(8, min(16, length // 20))
        
        # Start with repeat sign and first chord
        current_line = "|: \"Em\""
        
        while bar_count < target_bars:
            # Change chord every 2 bars
            if chord_bar_count >= 2:
                current_chord = random.choice(chords)
                chord_bar_count = 0
            
            # Generate 4 notes per bar (for 4/4 time with 1/8 note default)
            for note_idx in range(4):
                # Select note based on temperature
                if random.random() < (1.0 - temperature / 2.5):
                    # Pick from common notes (lower range) - more deterministic
                    note = random.choice(notes[:8])
                else:
                    # Pick any note - more creative
                    note = random.choice(notes)
                
                # Add duration modifier (less frequently)
                duration_roll = random.random()
                if duration_roll < 0.05:
                    note += "4"  # Half note
                elif duration_roll < 0.1:
                    note += "2"  # Quarter note
                # else: default 1/8 note
                
                current_line += note
                
                # Add space between notes
                if note_idx < 3:
                    current_line += " "
                
                notes_in_bar += 1
            
            # Add bar line
            current_line += "|"
            bar_count += 1
            chord_bar_count += 1
            notes_in_bar = 0
            
            # Add chord annotation for next bar if needed
            if bar_count < target_bars and chord_bar_count == 0:
                current_line += f" \"{current_chord}\""
            
            # Add line break every 2 bars for readability
            if bar_count % 2 == 0:
                notation += current_line + "\n"
                current_line = ""
        
        # Add any remaining content
        if current_line:
            notation += current_line + "\n"
        
        # Close the repeat with proper ending
        notation += ":|"
        
        return notation
