#!/usr/bin/env python
"""Integration test for music generation pipeline"""

import json
import re
from services.generator import MusicGenerator
from services.model_loader import ModelLoader
from services.validator import InputValidator

def test_full_pipeline():
    """Test the complete generation pipeline"""
    
    # Initialize services
    validator = InputValidator()
    model_loader = ModelLoader('best_model.pt')
    generator = MusicGenerator(model_loader)
    
    print("=" * 60)
    print("MUSIC GENERATION PIPELINE INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: Input Validation
    print("\n[Test 1] Input Validation")
    test_input = {'seed': '', 'temperature': 1.0, 'length': 200}
    validation = validator.validate(test_input)
    assert validation['valid'], "Validation failed"
    print(f"✓ Input validation passed")
    print(f"  - Seed: {validation['data']['seed'][:30]}...")
    print(f"  - Temperature: {validation['data']['temperature']}")
    print(f"  - Length: {validation['data']['length']}")
    
    # Test 2: Music Generation
    print("\n[Test 2] Music Generation")
    result = generator.generate('', 1.0, 200)
    notation = result['notation']
    assert len(notation) > 0, "No notation generated"
    print(f"✓ Generated {len(notation)} characters of ABC notation")
    
    # Test 3: ABC Format Verification
    print("\n[Test 3] ABC Format Verification")
    lines = notation.split('\n')
    headers = [l for l in lines if l.startswith(('X:', 'T:', 'M:', 'L:', 'K:', 'R:'))]
    assert len(headers) >= 5, "Missing ABC headers"
    print(f"✓ Found {len(headers)} ABC headers:")
    for h in headers:
        print(f"  - {h}")
    
    # Test 4: Note Extraction
    print("\n[Test 4] Note Extraction")
    notes = re.findall(r'[A-Ga-g]', notation)
    chords = re.findall(r'"[A-Za-z]+"', notation)
    assert len(notes) > 0, "No notes found"
    assert len(chords) > 0, "No chords found"
    print(f"✓ Extracted {len(notes)} notes")
    print(f"✓ Extracted {len(chords)} chord annotations")
    print(f"  - Unique chords: {set(chords)}")
    
    # Test 5: Temperature Variation
    print("\n[Test 5] Temperature Variation")
    notations = {}
    for temp in [0.5, 1.0, 1.5]:
        result = generator.generate('', temp, 200)
        notations[temp] = result['notation']
        notes_count = len(re.findall(r'[A-Ga-g]', result['notation']))
        print(f"✓ Temperature {temp}: {notes_count} notes generated")
    
    # Verify different temperatures produce different results
    assert notations[0.5] != notations[1.0], "Different temperatures should produce different results"
    print("✓ Different temperatures produce different outputs")
    
    # Test 6: Chord Progression
    print("\n[Test 6] Chord Progression")
    chord_pattern = re.findall(r'"(Em|D)"', notation)
    print(f"✓ Chord progression: {' → '.join(chord_pattern[:8])}...")
    assert 'Em' in chord_pattern, "Em chord not found"
    assert 'D' in chord_pattern, "D chord not found"
    print("✓ Proper Em/D chord progression detected")
    
    # Test 7: Sample Output
    print("\n[Test 7] Sample Output")
    print("First 300 characters of generated notation:")
    print("-" * 60)
    print(notation[:300])
    print("-" * 60)
    
    print("\n" + "=" * 60)
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("=" * 60)

if __name__ == '__main__':
    test_full_pipeline()
