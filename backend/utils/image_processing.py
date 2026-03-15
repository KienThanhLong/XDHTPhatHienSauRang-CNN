import cv2
import numpy as np
from PIL import Image
import io
from config import IMAGE_SIZE, ALLOWED_EXTENSIONS

def allowed_file(filename):
    """Kiểm tra file có hợp lệ không"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_image(image_data):
    """Đọc ảnh từ file bytes"""
    try:
        image = Image.open(io.BytesIO(image_data))
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        raise ValueError(f"Lỗi đọc ảnh: {str(e)}")

def preprocess_cnn(image):
    """Tiền xử lý ảnh cho CNN"""
    # Resize
    image = cv2.resize(image, IMAGE_SIZE)
    
    # Normalize
    image = image.astype('float32') / 255.0
    
    # Add batch dimension
    image = np.expand_dims(image, 0)
    
    return image

def preprocess_yolo(image):
    """Tiền xử lý ảnh cho YOLO"""
    # Resize giữ tỉ lệ
    height, width = image.shape[:2]
    scale = min(640 / height, 640 / width)
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    image = cv2.resize(image, (new_width, new_height))
    
    # Pad to 640x640
    top = (640 - new_height) // 2
    bottom = 640 - new_height - top
    left = (640 - new_width) // 2
    right = 640 - new_width - left
    
    image = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114))
    
    return image

def draw_results(image, detections, labels=None):
    """Vẽ kết quả detection lên ảnh"""
    result_image = image.copy()
    
    colors = {
        "Khỏe mạnh": (0, 255, 0),      # Green
        "Sâu nhẹ": (255, 255, 0),       # Yellow
        "Sâu vừa": (0, 165, 255),       # Orange
        "Sâu nặng": (0, 0, 255)         # Red
    }
    
    for det in detections:
        x1, y1, x2, y2 = map(int, det['bbox'])
        label = det.get('class_name', 'Unknown')
        confidence = det.get('confidence', 0)
        
        color = colors.get(label, (0, 255, 0))
        
        # Draw rectangle
        cv2.rectangle(result_image, (x1, y1), (x2, y2), color, 2)
        
        # Draw label
        text = f"{label}: {confidence:.2f}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        
        cv2.rectangle(result_image, 
                     (x1, y1 - text_size[1] - 10),
                     (x1 + text_size[0] + 5, y1),
                     color, -1)
        
        cv2.putText(result_image, text, (x1 + 2, y1 - 5),
                   font, font_scale, (255, 255, 255), thickness)
    
    return result_image

def image_to_base64(image):
    """Chuyển ảnh thành base64 string"""
    _, buffer = cv2.imencode('.jpg', image)
    import base64
    return base64.b64encode(buffer).decode('utf-8')

def save_image(image, filename):
    """Lưu ảnh"""
    cv2.imwrite(filename, image)
