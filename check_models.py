#!/usr/bin/env python3
"""
Simple test - Just check if model files exist
"""

import os
from pathlib import Path

def main():
    print("\n" + "="*60)
    print("CHECKING MODEL FILES")
    print("="*60 + "\n")
    
    models_dir = "backend/models"
    
    print(f"Looking in: {models_dir}\n")
    
    if not os.path.exists(models_dir):
        print(f"✗ Folder not found: {models_dir}")
        return
    
    files = os.listdir(models_dir)
    print(f"Found {len(files)} file(s):\n")
    
    for filename in files:
        filepath = os.path.join(models_dir, filename)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"  ✓ {filename}")
        print(f"    Size: {size_mb:.1f} MB")
        print()
    
    # Check for specific files
    print("="*60)
    print("EXPECTED FILES:\n")
    
    yolo_path = os.path.join(models_dir, "best.pt")
    cnn_path = os.path.join(models_dir, "cnn_model.h5")
    
    if os.path.exists(yolo_path):
        size = os.path.getsize(yolo_path) / (1024 * 1024)
        print(f"✅ YOLO: best.pt ({size:.1f} MB) - READY")
    else:
        print(f"❌ YOLO: best.pt - NOT FOUND")
    
    if os.path.exists(cnn_path):
        size = os.path.getsize(cnn_path) / (1024 * 1024)
        print(f"✅ CNN:  cnn_model.h5 ({size:.1f} MB) - READY")
    else:
        print(f"❌ CNN:  cnn_model.h5 - NOT FOUND")
    
    print("\n" + "="*60)
    print("NEXT STEPS:\n")
    
    if os.path.exists(yolo_path) and os.path.exists(cnn_path):
        print("✅ Both models ready!")
        print("   Run: python app.py")
    elif os.path.exists(yolo_path):
        print("⚠ YOLO ready, but missing CNN model")
        print("   Add: cnn_model.h5 to backend/models/")
        print("   Then: python app.py")
    else:
        print("⚠ Both models needed:")
        print("   1. Add cnn_model.h5 to backend/models/")
        print("   2. best.pt is already there ✓")
        print("   3. Run: python app.py")
    
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
