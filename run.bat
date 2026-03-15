@echo off
REM ============================================
REM Script chuẩn bị môi trường và chạy project
REM Windows Batch File
REM ============================================

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  HÊ THỐNG CHẨN ĐOÁN SÂU RĂNG - SETUP SCRIPT           ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Kiểm tra Python
echo Kiểm tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python chưa được cài đặt!
    echo   Vui lòng tải: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python sẵn sàng
echo.

REM Kiểm tra venv
if not exist "venv" (
    echo Tạo virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ✗ Lỗi tạo venv!
        pause
        exit /b 1
    )
    echo ✓ Tạo venv thành công
) else (
    echo ✓ venv đã tồn tại
)
echo.

REM Kích hoạt venv
echo Kích hoạt virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ✗ Lỗi kích hoạt venv!
    pause
    exit /b 1
)
echo ✓ venv đã kích hoạt
echo.

REM Cài đặt dependencies
echo Cài đặt dependencies (lần đầu có thể mất 5-10 phút)...
cd backend
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ✗ Lỗi cài đặt dependencies!
    echo   Thử: pip install --upgrade pip
    pause
    exit /b 1
)
echo ✓ Cài đặt dependencies thành công
echo.

REM Kiểm tra models
echo Kiểm tra file models...
if not exist "models\cnn_model.h5" (
    echo ⚠ Chưa tìm thấy: models\cnn_model.h5
    echo   Hãy copy file vào thư mục models\
)
if not exist "models\yolo_model.pt" (
    echo ⚠ Chưa tìm thấy: models\yolo_model.pt
    echo   Hãy copy file vào thư mục models\
)
echo.

REM Chạy app
echo Khởi chạy ứng dụng...
echo.
python app.py

pause
