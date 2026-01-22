#!/usr/bin/env python
"""Test if music is generated from the trained model"""

import logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

from services.model_loader import ModelLoader
from services.generator import MusicGenerator

print("=" * 60)
print("TESTING MODEL-BASED MUSIC GENERATION")
print("=" * 60)

try:
    print("\n[1] Loading your trained model...")
    model_loader = ModelLoader('best_model.pt')
    print("✓ Model loaded successfully")
    
    print("\n[2] Initializing generator...")
    generator = MusicGenerator(model_loader)
    print("✓ Generator initialized")
    
    print("\n[3] Generating music with your trained model...")
    result = generator.generate('', 1.0, 200)
    notation = result['notation']
    
    print("\n" + "=" * 60)
    print("GENERATED MUSIC (from your trained model)")
    print("=" * 60)
    print(notation[:500])
    print("...")
    print("=" * 60)
    
    print(f"\nTotal length: {len(notation)} characters")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Temperature: {result['parameters']['temperature']}")
    print(f"Length param: {result['parameters']['length']}")
    
    # Check if it looks like ABC notation
    if notation.startswith('X:'):
        print("\n✓ Output is valid ABC notation")
    
    # Count notes
    import re
    notes = re.findall(r'[A-Ga-g]', notation)
    print(f"✓ Found {len(notes)} notes in generated music")
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Music is generated from your trained model!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
