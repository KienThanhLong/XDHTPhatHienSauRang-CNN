#!/usr/bin/env python3
"""
Test script: Kiểm tra xem file YOLO model có thể load được không
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_yolo_model():
    """Test load YOLO model"""
    print("\n" + "="*60)
    print("TEST LOAD YOLO MODEL")
    print("="*60 + "\n")
    
    try:
        from ultralytics import YOLO
        print("✓ Ultralytics imported successfully")
        
        model_path = "backend/models/best.pt"
        
        # Check file exists
        if not os.path.exists(model_path):
            print(f"✗ File not found: {model_path}")
            # List what's in models folder
            models_dir = "backend/models"
            if os.path.exists(models_dir):
                files = os.listdir(models_dir)
                print(f"\nFiles in {models_dir}:")
                for f in files:
                    size = os.path.getsize(os.path.join(models_dir, f)) / (1024*1024)
                    print(f"  • {f} ({size:.1f} MB)")
            return False
        
        file_size = os.path.getsize(model_path) / (1024*1024)
        print(f"✓ File found: {model_path}")
        print(f"  Size: {file_size:.1f} MB\n")
        
        # Try to load
        print("Loading YOLO model...")
        model = YOLO(model_path)
        print("✓ YOLO model loaded successfully!\n")
        
        # Print model info
        print("Model Information:")
        print(f"  • Model name: {model.model_name}")
        print(f"  • Device: {model.device}")
        print(f"  • Task: {model.task}")
        
        # Test prediction on dummy image
        print("\nTesting with dummy prediction...")
        # Create simple test image
        import numpy as np
        import cv2
        
        # Create a simple image
        dummy_img = np.ones((640, 640, 3), dtype=np.uint8) * 128
        
        # Predict
        results = model(dummy_img, conf=0.5)
        print(f"✓ Prediction successful!")
        print(f"  • Detections: {len(results[0].boxes)}")
        
        print("\n" + "="*60)
        print("✅ YOLO MODEL TEST PASSED!")
        print("="*60 + "\n")
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False

def test_cnn_model():
    """Test load CNN model"""
    print("\n" + "="*60)
    print("TEST LOAD CNN MODEL")
    print("="*60 + "\n")
    
    try:
        import tensorflow as tf
        print("✓ TensorFlow imported successfully")
        
        model_path = "backend/models/cnn_model.h5"
        
        if not os.path.exists(model_path):
            print(f"✗ File not found: {model_path}")
            print("\n  → You need to add CNN model file")
            print("     FILE: cnn_model.h5 (or similar)")
            print("     PATH: backend/models/")
            return False
        
        file_size = os.path.getsize(model_path) / (1024*1024)
        print(f"✓ File found: {model_path}")
        print(f"  Size: {file_size:.1f} MB\n")
        
        print("Loading CNN model...")
        model = tf.keras.models.load_model(model_path)
        print("✓ CNN model loaded successfully!\n")
        
        print("Model Information:")
        print(f"  • Input shape: {model.input_shape}")
        print(f"  • Output shape: {model.output_shape}")
        print(f"  • Total params: {model.count_params():,}")
        
        print("\n" + "="*60)
        print("✅ CNN MODEL TEST PASSED!")
        print("="*60 + "\n")
        return True
        
    except ImportError:
        print("⚠ TensorFlow not installed")
        print("  → Install: pip install tensorflow")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False

def test_pipeline(image_path):
    """Run YOLO+CNN end-to-end on a sample image and print results."""
    print("\n" + "="*60)
    print("TEST FULL PIPELINE")
    print("="*60 + "\n")
    try:
        from utils.inference import ToothAnalyzer
        import cv2, json
    except ImportError as e:
        print(f"✗ Unable to import pipeline dependencies: {e}")
        return False

    if not os.path.exists(image_path):
        print(f"✗ Image not found: {image_path}")
        return False

    print(f"Loading image {image_path}...")
    img = cv2.imread(image_path)
    if img is None:
        print("✗ Failed to read image (cv2 returned None)")
        return False

    # analyze
    an = ToothAnalyzer()
    results = an.analyze_image(img)
    print("Pipeline results:")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print("\n" + "="*60)
    return True


def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  HỆTHỐNG CHẨN ĐOÁN SÂU RĂNG - MODEL TEST".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    yolo_ok = test_yolo_model()
    cnn_ok = test_cnn_model()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"YOLO Model: {'✅ OK' if yolo_ok else '❌ FAIL'}")
    print(f"CNN Model:  {'✅ OK' if cnn_ok else '❌ FAIL'}")
    
    if yolo_ok and cnn_ok:
        print("\n✅ All models loaded! You can run: python app.py")
    elif yolo_ok:
        print("\n⚠ YOLO ready, but need CNN model to run full app")
        print("  → Add cnn_model.h5 to backend/models/")
    else:
        print("\n❌ Issues found - check errors above")
    
    print("="*60 + "\n")

if __name__ == '__main__':
    # allow optional image path after tests
    import sys
    main()
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        test_pipeline(img_path)
