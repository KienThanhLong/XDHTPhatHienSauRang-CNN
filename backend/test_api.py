#!/usr/bin/env python3
"""
Script test API của hệ thống
Chạy sau khi app.py đã khởi chạy
"""

import requests
import json
import os
from pathlib import Path

API_BASE_URL = "http://127.0.0.1:5000/api"

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def test_health_check():
    """Test health check endpoint"""
    print_header("TEST 1: Health Check")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        return False

def test_model_status():
    """Test model status endpoint"""
    print_header("TEST 2: Model Status")
    try:
        response = requests.get(f"{API_BASE_URL}/test-models")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if data['cnn_loaded'] and data['yolo_loaded']:
            print("✓ Cả hai model đã load thành công!")
            return True
        else:
            print("✗ Model chưa load đầy đủ")
            if not data['cnn_loaded']:
                print("  - CNN model: Chưa load")
            if not data['yolo_loaded']:
                print("  - YOLO model: Chưa load")
            return False
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        return False

def test_image_analysis(image_path=None):
    """Test image analysis endpoint"""
    print_header("TEST 3: Image Analysis")
    
    # Tìm file test
    if image_path is None:
        # Tìm ảnh trong thư mục hiện tại
        for ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            files = list(Path('.').glob(f'*.{ext}'))
            if files:
                image_path = str(files[0])
                break
    
    if image_path is None or not os.path.exists(image_path):
        print("✗ Không tìm thấy file ảnh test")
        print(f"  Vui lòng chuẩn bị file ảnh và chạy:")
        print(f"  python test_api.py <path_to_image>")
        return False
    
    try:
        print(f"Tải ảnh: {image_path}")
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{API_BASE_URL}/analyze", files=files)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✓ Phân tích thành công!")
                result = data['data']
                print(f"\nKết quả:")
                print(f"  - Health Score: {result['health_score']}%")
                print(f"  - Tổng số răng: {result['summary']['total_teeth']}")
                print(f"  - Khỏe mạnh: {result['summary']['healthy']}")
                print(f"  - Sâu nhẹ: {result['summary']['light_decay']}")
                print(f"  - Sâu vừa: {result['summary']['medium_decay']}")
                print(f"  - Sâu nặng: {result['summary']['severe_decay']}")
                print(f"\n  Khuyến cáo:")
                for rec in result['recommendations']:
                    print(f"    • {rec}")
                return True
            else:
                print(f"✗ Lỗi: {data['error']}")
                return False
        else:
            error = response.json()
            print(f"✗ Lỗi: {error.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        return False

def run_all_tests(image_path=None):
    """Chạy tất cả test"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  HỆ THỐNG CHẨN ĐOÁN SÂU RĂNG - API TEST SUITE            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    results = {
        'Health Check': test_health_check(),
        'Model Status': test_model_status(),
        'Image Analysis': test_image_analysis(image_path)
    }
    
    print_header("TÓMO QUÁT KẾT QUẢ")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nTổng cộng: {passed}/{total} test passed")
    
    if passed == total:
        print("\n✓ Tất cả test đã pass! Hệ thống sẵn sàng sử dụng!")
    else:
        print("\n✗ Một vài test failed. Vui lòng kiểm tra lại setup.")

if __name__ == "__main__":
    import sys
    
    image_path = None
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    
    try:
        run_all_tests(image_path)
    except KeyboardInterrupt:
        print("\n\n⚠ Test bị hủy bỏ")
    except requests.exceptions.ConnectionError:
        print("\n✗ Không thể kết nối đến server!")
        print("  Vui lòng chạy: python app.py")
