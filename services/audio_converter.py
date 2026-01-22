"""
Audio conversion service for generating MP4 files from ABC notation
"""
import logging
import os
import tempfile
from pathlib import Path
import numpy as np
from scipy.io import wavfile

logger = logging.getLogger(__name__)


class AudioConverter:
    """Converts ABC notation to MP4 audio files"""
    
    def __init__(self):
        """Initialize the audio converter"""
        self.sample_rate = 44100
    
    def abc_to_mp4(self, notation, output_path=None):
        """
        Convert ABC notation to MP4 file
        
        Args:
            notation: ABC notation string
            output_path: Path to save MP4 file (optional)
        
        Returns:
            Path to generated MP4 file
        """
        try:
            # Parse ABC notation to get notes
            notes = self._parse_abc_notation(notation)
            
            if not notes:
                raise ValueError('No valid notes found in ABC notation')
            
            # Generate audio from notes
            audio_data = self._generate_audio(notes)
            
            # Create output path if not provided
            if output_path is None:
                output_path = tempfile.mktemp(suffix='.mp4')
            
            # Try to use moviepy if available, otherwise use scipy
            try:
                self._generate_mp4_with_moviepy(audio_data, output_path)
            except ImportError:
                logger.warning('moviepy not available, generating WAV instead')
                # Fallback to WAV generation
                wav_path = output_path.replace('.mp4', '.wav')
                wavfile.write(wav_path, self.sample_rate, audio_data)
                output_path = wav_path
            
            logger.info(f'Generated audio file: {output_path}')
            return output_path
            
        except Exception as e:
            logger.error(f'ABC to MP4 conversion failed: {e}', exc_info=True)
            raise
    
    def _generate_mp4_with_moviepy(self, audio_data, output_path):
        """
        Generate MP4 using moviepy
        
        Args:
            audio_data: Audio samples
            output_path: Path to save MP4 file
        """
        try:
            from moviepy.editor import AudioFileClip, CompositeAudioClip
            from moviepy.audio.AudioClip import AudioArrayClip
            
            # Create audio clip from numpy array
            # Normalize audio to [-1, 1] range for moviepy
            audio_normalized = audio_data.astype(np.float32) / 32768.0
            
            # Create audio clip (mono to stereo)
            audio_clip = AudioArrayClip(
                np.array([audio_normalized, audio_normalized]),  # Stereo
                fps=self.sample_rate
            )
            
            # Write to MP4 (audio only)
            audio_clip.write_audiofile(
                output_path,
                verbose=False,
                logger=None,
                codec='aac'
            )
            
            logger.info(f'MP4 generated successfully: {output_path}')
            
        except ImportError:
            raise ImportError('moviepy is required for MP4 generation')
    
    def abc_to_wav(self, notation, output_path=None):
        """
        Convert ABC notation to WAV file (fallback)
        
        Args:
            notation: ABC notation string
            output_path: Path to save WAV file (optional)
        
        Returns:
            Path to generated WAV file
        """
        try:
            # Parse ABC notation to get notes
            notes = self._parse_abc_notation(notation)
            
            if not notes:
                raise ValueError('No valid notes found in ABC notation')
            
            # Generate audio from notes
            audio_data = self._generate_audio(notes)
            
            # Create output path if not provided
            if output_path is None:
                output_path = tempfile.mktemp(suffix='.wav')
            
            # Write WAV file
            wavfile.write(output_path, self.sample_rate, audio_data)
            
            logger.info(f'Generated WAV file: {output_path}')
            return output_path
            
        except Exception as e:
            logger.error(f'ABC to WAV conversion failed: {e}', exc_info=True)
            raise
    
    def _parse_abc_notation(self, notation):
        """
        Parse ABC notation to extract notes
        
        Args:
            notation: ABC notation string
        
        Returns:
            List of note dictionaries with pitch and duration
        """
        notes = []
        lines = notation.split('\n')
        
        for line in lines:
            # Skip header lines
            if line.startswith(('X:', 'T:', 'M:', 'L:', 'R:', 'K:')):
                continue
            
            # Skip empty lines
            if not line.strip():
                continue
            
            # Parse notes in the line
            i = 0
            while i < len(line):
                char = line[i]
                
                # Skip chord annotations
                if char == '"':
                    i += 1
                    while i < len(line) and line[i] != '"':
                        i += 1
                    i += 1
                    continue
                
                # Skip bar lines and repeats
                if char in '|:[]':
                    i += 1
                    continue
                
                # Skip spaces
                if char == ' ':
                    i += 1
                    continue
                
                # Skip decorations
                if char in '{}~!+.':
                    i += 1
                    continue
                
                # Parse note
                if char in 'ABCDEFGabcdefgz':
                    note_char = char
                    i += 1
                    
                    # Skip accidentals
                    while i < len(line) and line[i] in '^_=':
                        i += 1
                    
                    # Handle octave changes
                    octave_mod = 0
                    while i < len(line) and line[i] in '\',':
                        if line[i] == "'":
                            octave_mod += 1
                        else:
                            octave_mod -= 1
                        i += 1
                    
                    # Parse duration
                    duration = 1.0
                    if i < len(line) and line[i].isdigit():
                        duration = float(line[i])
                        i += 1
                    
                    if i < len(line) and line[i] == '/':
                        i += 1
                        if i < len(line) and line[i].isdigit():
                            duration = duration / float(line[i])
                            i += 1
                        else:
                            duration = duration / 2.0
                    
                    # Convert to MIDI pitch
                    if note_char != 'z':
                        midi_pitch = self._note_to_midi(note_char, octave_mod)
                        notes.append({
                            'pitch': midi_pitch,
                            'duration': duration,
                            'rest': False
                        })
                    else:
                        notes.append({
                            'pitch': 0,
                            'duration': duration,
                            'rest': True
                        })
                else:
                    i += 1
        
        return notes
    
    def _note_to_midi(self, note_char, octave_mod=0):
        """
        Convert ABC note character to MIDI pitch
        
        Args:
            note_char: Single note character (A-G, a-g)
            octave_mod: Octave modification (+1 for ', -1 for ,)
        
        Returns:
            MIDI pitch number
        """
        note_map = {
            'C': 60, 'D': 62, 'E': 64, 'F': 65, 'G': 67, 'A': 69, 'B': 71,
            'c': 72, 'd': 74, 'e': 76, 'f': 77, 'g': 79, 'a': 81, 'b': 83
        }
        
        midi = note_map.get(note_char, 60)
        midi += octave_mod * 12
        
        # Clamp to valid MIDI range
        return max(0, min(127, midi))
    
    def _generate_audio(self, notes, tempo_bpm=120):
        """
        Generate audio data from notes
        
        Args:
            notes: List of note dictionaries
            tempo_bpm: Tempo in beats per minute
        
        Returns:
            NumPy array of audio samples
        """
        # Calculate beat duration in seconds
        beat_duration = 60.0 / tempo_bpm
        
        # Generate audio for each note
        audio_segments = []
        
        for note in notes:
            # Calculate note duration in seconds
            note_duration = beat_duration * note['duration']
            
            if note['rest']:
                # Generate silence
                num_samples = int(note_duration * self.sample_rate)
                segment = np.zeros(num_samples, dtype=np.float32)
            else:
                # Generate sine wave for the note
                frequency = 440 * (2 ** ((note['pitch'] - 69) / 12))
                num_samples = int(note_duration * self.sample_rate)
                t = np.linspace(0, note_duration, num_samples, dtype=np.float32)
                
                # Generate sine wave with envelope
                segment = np.sin(2 * np.pi * frequency * t).astype(np.float32)
                
                # Apply envelope (attack, decay, sustain, release)
                envelope = self._apply_envelope(num_samples, note_duration)
                segment = segment * envelope
            
            audio_segments.append(segment)
        
        # Concatenate all segments
        audio_data = np.concatenate(audio_segments)
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val * 0.9
        
        # Convert to 16-bit PCM
        audio_data = (audio_data * 32767).astype(np.int16)
        
        return audio_data
    
    def _apply_envelope(self, num_samples, duration):
        """
        Apply ADSR envelope to audio
        
        Args:
            num_samples: Number of samples
            duration: Duration in seconds
        
        Returns:
            Envelope array
        """
        # ADSR times as fraction of note duration
        attack_time = 0.01  # 10ms
        decay_time = 0.05   # 50ms
        sustain_level = 0.7
        release_time = 0.1  # 100ms
        
        envelope = np.ones(num_samples, dtype=np.float32)
        
        # Attack
        attack_samples = int(attack_time * self.sample_rate)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay
        decay_samples = int(decay_time * self.sample_rate)
        decay_start = attack_samples
        decay_end = decay_start + decay_samples
        if decay_end <= num_samples:
            envelope[decay_start:decay_end] = np.linspace(1, sustain_level, decay_samples)
        
        # Release
        release_samples = int(release_time * self.sample_rate)
        release_start = max(0, num_samples - release_samples)
        if release_start < num_samples:
            envelope[release_start:] = np.linspace(sustain_level, 0, num_samples - release_start)
        
        return envelope
