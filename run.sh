#!/bin/bash

# ============================================
# Script chuẩn bị môi trường và chạy project
# Ubuntu/Mac Bash File
# ============================================

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  HỆ THỐNG CHẨN ĐOÁN SÂU RĂNG - SETUP SCRIPT            ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Kiểm tra Python
echo "Kiểm tra Python..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python chưa được cài đặt!"
    echo "  Vui lòng cài đặt: brew install python3 (macOS) hoặc apt install python3 (Linux)"
    exit 1
fi
echo "✓ Python sẵn sàng"
echo ""

# Kiểm tra venv
if [ ! -d "venv" ]; then
    echo "Tạo virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "✗ Lỗi tạo venv!"
        exit 1
    fi
    echo "✓ Tạo venv thành công"
else
    echo "✓ venv đã tồn tại"
fi
echo ""

# Kích hoạt venv
echo "Kích hoạt virtual environment..."
source venv/bin/activate
echo "✓ venv đã kích hoạt"
echo ""

# Cài đặt dependencies
echo "Cài đặt dependencies (lần đầu có thể mất 5-10 phút)..."
cd backend
pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "✗ Lỗi cài đặt dependencies!"
    echo "  Thử: pip install --upgrade pip"
    exit 1
fi
echo "✓ Cài đặt dependencies thành công"
echo ""

# Kiểm tra models
echo "Kiểm tra file models..."
if [ ! -f "models/cnn_model.h5" ]; then
    echo "⚠ Chưa tìm thấy: models/cnn_model.h5"
    echo "  Hãy copy file vào thư mục models/"
fi
if [ ! -f "models/yolo_model.pt" ]; then
    echo "⚠ Chưa tìm thấy: models/yolo_model.pt"
    echo "  Hãy copy file vào thư mục models/"
fi
echo ""

# Chạy app
echo "Khởi chạy ứng dụng..."
echo ""
python app.py
