# Docker Guide

Tài liệu này hướng dẫn cách build và chạy dự án bằng Docker theo cấu hình hiện tại:

- `1` container Flask
- `CPU-only PyTorch`
- model được mount từ máy host, không đóng gói sẵn vào image

Mục tiêu là để dự án chạy được trên nhiều máy bằng một lệnh, đồng thời giảm kích thước image so với cách đóng gói cả model và GPU dependencies.

## 1. Yêu cầu trước khi chạy

Máy cần có:

- Docker Desktop
- Docker Compose

Kiểm tra nhanh:

```bash
docker --version
docker compose version
```

## 2. Cấu trúc file liên quan

Các file Docker chính của dự án:

- [`Dockerfile`](/d:/Luận%20văn/Dockerfile)
- [`docker-compose.yml`](/d:/Luận%20văn/docker-compose.yml)
- [`.dockerignore`](/d:/Luận%20văn/.dockerignore)

Thư mục được mount từ máy host vào container:

- [`backend/models`](/d:/Luận%20văn/backend/models)
- [`backend/uploads`](/d:/Luận%20văn/backend/uploads)

## 3. Chuẩn bị model

Đặt các file model vào thư mục [`backend/models`](/d:/Luận%20văn/backend/models):

- `cnn_caries_model.h5`
- `best.pt`

Tên file hiện tại đang được khai báo trong [`backend/config.py`](/d:/Luận%20văn/backend/config.py).

Nếu bạn đổi tên model, cần sửa lại:

- `CNN_MODEL_PATH`
- `YOLO_MODEL_PATH`

## 4. Build image

Từ thư mục gốc dự án, chạy:

```bash
docker compose build --no-cache
```

Lần build đầu có thể khá lâu vì phải cài:

- TensorFlow
- OpenCV
- Ultralytics
- PyTorch CPU-only

## 5. Chạy ứng dụng

Chạy nền:

```bash
docker compose up -d
```

Hoặc build và chạy luôn:

```bash
docker compose up -d --build
```

Sau khi chạy thành công, mở:

```text
http://localhost:5000
```

## 6. Dừng ứng dụng

```bash
docker compose down
```

## 7. Xem log

```bash
docker compose logs -f
```

Nếu chỉ muốn xem log service chính:

```bash
docker compose logs -f dental-caries-app
```

## 8. Kiểm tra container đang chạy

```bash
docker compose ps
```

## 9. Cách hoạt động hiện tại

Container sẽ:

- chạy [`backend/app.py`](/d:/Luận%20văn/backend/app.py)
- bind địa chỉ `0.0.0.0:5000`
- serve cả API và frontend

`docker-compose.yml` hiện map:

- cổng `5000:5000`
- `./backend/models -> /app/backend/models`
- `./backend/uploads -> /app/backend/uploads`

Điều này có nghĩa:

- model nằm ngoài image
- đổi model không cần build lại image
- ảnh kết quả được lưu trực tiếp ở máy host

## 10. Chạy lại sau khi sửa code

Nếu chỉ sửa file Python, HTML, CSS, JS mà image chưa đổi, tốt nhất vẫn build lại để chắc chắn:

```bash
docker compose up -d --build
```

Nếu muốn build sạch:

```bash
docker compose build --no-cache
docker compose up -d
```

## 11. Các lệnh hay dùng

Build:

```bash
docker compose build
```

Build sạch:

```bash
docker compose build --no-cache
```

Chạy:

```bash
docker compose up -d
```

Dừng:

```bash
docker compose down
```

Xem log:

```bash
docker compose logs -f
```

## 12. Lỗi thường gặp

### Không load được model

Kiểm tra:

- file model có thật trong [`backend/models`](/d:/Luận%20văn/backend/models)
- tên file đúng với [`backend/config.py`](/d:/Luận%20văn/backend/config.py)

### Mở `localhost:5000` không lên

Kiểm tra:

```bash
docker compose ps
docker compose logs -f
```

### Build quá lâu

Lần đầu là bình thường vì dependency ML lớn. Những lần sau sẽ nhanh hơn nếu cache còn.

### Port 5000 đã bị chiếm

Sửa trong [`docker-compose.yml`](/d:/Luận%20văn/docker-compose.yml):

```yml
ports:
  - "5001:5000"
```

Sau đó truy cập:

```text
http://localhost:5001
```

## 13. Ghi chú tối ưu

Cấu hình hiện tại đã tối ưu hơn bản cũ ở các điểm:

- không copy model vào image
- dùng `CPU-only PyTorch`
- loại nhiều thư mục thừa khỏi build context bằng [`.dockerignore`](/d:/Luận%20văn/.dockerignore)

Tuy vậy image vẫn còn khá nặng do:

- TensorFlow
- OpenCV
- Ultralytics

Nếu sau này cần nhẹ hơn nữa, hướng tiếp theo là:

- tối ưu lại dependencies riêng cho deploy
- giảm package hệ thống
- chuyển model sang runtime nhẹ hơn như ONNX
