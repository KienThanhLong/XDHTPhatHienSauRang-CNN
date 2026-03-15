# 🦷 Hệ Thống Phân Tích Sâu Răng (CNN + YOLO)

Đây là dự án luận văn xây dựng hệ thống phân tích sâu răng tự động bằng **Deep Learning** kết hợp **YOLOv8** (phát hiện vị trí) và **CNN** (phân loại mức độ sâu).

> 🚀 Mục tiêu: Nhận đầu vào là ảnh X-quang răng, trả về vị trí răng bị sâu và thống kê tổng quan.

---

## 📌 Tính Năng Chính

- ✅ Phát hiện vị trí răng và vùng sâu bằng **YOLOv8**
- ✅ Phân loại mức độ sâu (Không sâu / Sâu nhẹ / Sâu vừa / Sâu nặng)
- ✅ Tích hợp giao diện web (Frontend + Backend)
- ✅ Xuất báo cáo PDF (kèm ảnh kết quả)
- ✅ API endpoint cho hệ thống khác gọi

---

## 📁 Cấu Trúc Dự Án

```
Luận Văn/
├── backend/                    # Flask + ML pipeline
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── models/                 # Lưu model CNN + YOLO
│   ├── utils/                  # Xử lý ảnh, inference
│   └── uploads/                # Lưu ảnh upload + kết quả
├── frontend/                   # Web UI
│   ├── index.html
│   ├── css/
│   └── js/
└── README.md
```

---

## 🛠️ Yêu Cầu Hệ Thống

### Môi trường
- Python **3.8+** (khuyến nghị 3.9 / 3.10)
- pip

### Phần cứng
- RAM ≥ 4GB
- Ổ cứng ≥ 2GB (cho model + upload)
- **GPU không bắt buộc**, nhưng sẽ tăng tốc đáng kể nếu dùng Nvidia + CUDA

---

## 🚀 Cài Đặt & Chạy Ứng Dụng

### 1) Chuẩn bị Python environment

**Windows (PowerShell)**
```powershell
cd D:\Luận\ văn
python -m venv .venv
# Kích hoạt
.venv\Scripts\Activate.ps1
```

> Nếu gặp lỗi ExecutionPolicy, chạy: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`


**Mac / Linux**
```bash
cd /path/to/Luận\ văn
python3 -m venv .venv
source .venv/bin/activate
```

---

### 2) Cài dependencies

```bash
cd backend
pip install -r requirements.txt
```

> Nếu cần phiên bản cụ thể của TensorFlow/PyTorch, cài thêm như:
> ```bash
> pip install tensorflow==2.10.0
> pip install torch torchvision torchaudio
> pip install ultralytics
> ```

---

### 3) Đặt model vào thư mục đúng

Copy file model vào thư mục:

```
backend/models/
├── cnn_model.h5     # (CNN)
└── yolo_model.pt    # (YOLO)
```

> Nếu bạn dùng tên khác, hãy cập nhật trong `backend/config.py` hoặc đổi tên file cho giống với cấu hình.

---

### 4) Chạy server

```bash
# Trong thư mục backend
python app.py
```

Nếu chạy thành công, bạn sẽ thấy output như:
```
✓ Load CNN model thành công: backend/models/cnn_model.h5
✓ Load YOLO model thành công: backend/models/yolo_model.pt
 * Running on http://127.0.0.1:5000
```

---

### 5) Mở giao diện web

Truy cập:

```
http://127.0.0.1:5000
```

---

## 🧠 Model & Cấu hình

### Folder chứa model
- `backend/models/cnn_model.h5`
- `backend/models/yolo_model.pt`

> Nếu dùng tên khác, hãy cập nhật trong `backend/config.py` hoặc đổi tên file.

### Cấu hình quan trọng (backend/config.py)
- `TOOTH_CLASSES`: Bảng mapping class → tên trạng thái răng
- `CONFIDENCE_THRESHOLD`, `IOU_THRESHOLD`: ngưỡng lọc YOLO
- `IMAGE_SIZE`: kích thước input cho CNN

---

## 🧪 Sử Dụng Giao Diện

1. Tải lên ảnh răng (kéo/thả hoặc click)
2. Chờ hệ thống phân tích
3. Xem kết quả cùng bounding box + thống kê
4. Tải báo cáo PDF nếu cần

---

## 🔌 API

### POST `/api/analyze`
- Mục đích: phân tích ảnh
- Content-Type: `multipart/form-data`
- Body:
  - `image`: file ảnh

**Response (200)**
```json
{
  "success": true,
  "data": {
    "image": "data:image/jpeg;base64,...",
    "filename": "result_...jpg",
    "detections": [
      {
        "bbox": [x, y, w, h],
        "confidence": 0.92,
        "class_id": 1,
        "class_name": "Sâu nhẹ",
        "classification_confidence": 0.87
      }
    ],
    "summary": {
      "total_teeth": 32,
      "healthy": 20,
      "light_decay": 8,
      "medium_decay": 3,
      "severe_decay": 1
    }
  }
}
```

### GET `/api/test-models`
**Response**
```json
{
  "cnn_loaded": true,
  "yolo_loaded": true,
  "status": "ready"
}
```

### GET `/api/health`
**Response**
```json
{
  "status": "ok",
  "timestamp": "2026-03-15T..."
}
```

---

## 🛠️ Debug

- Bật debug trong `backend/app.py`: `app.run(debug=True)`
- Kiểm tra log console (Python)
- Mở DevTools (Chrome) để xem requests API

---

## 🤝 Đóng Góp

Mọi góp ý/báo lỗi: mở issue hoặc gửi PR (nếu có GitHub).

---

## 📄 Giấy Phép
Dự án hướng tới mục đích học tập / nghiên cứu.

---

**Last updated:** 15/03/2026
