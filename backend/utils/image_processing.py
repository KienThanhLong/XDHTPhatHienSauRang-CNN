import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import unicodedata
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

def _load_vietnamese_font(size=18):
    fonts = [
        "DejaVuSans-Bold.ttf",
        "DejaVuSans.ttf",
        "Arial.ttf",
        "arial.ttf",
        "arialuni.ttf",
        "NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/Arial.ttf",
        "C:/Windows/Fonts/arialuni.ttf",
        "C:/Windows/Fonts/NotoSans-Regular.ttf",
    ]
    for font_path in fonts:
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _normalize_to_ascii(text):
    if not isinstance(text, str):
        return text
    normalized = unicodedata.normalize('NFKD', text)
    ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
    return ascii_text


def draw_results(image, detections, labels=None):
    """Vẽ kết quả detection lên ảnh"""
    result_image = image.copy()
    
    colors = {
        "Khỏe mạnh": (0, 255, 0),      # Green
        "Sâu nhẹ": (255, 255, 0),       # Yellow
        "Sâu vừa": (0, 165, 255),       # Orange
        "Sâu nặng": (0, 0, 255)         # Red
    }

    # Dùng PIL để hỗ trợ Unicode cho Tiếng Việt (tránh lỗi font OpenCV không hỗ trợ dấu)
    pil_image = Image.fromarray(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)

    font = _load_vietnamese_font(18)

    for det in detections:
        x1, y1, x2, y2 = map(int, det['bbox'])
        label = det.get('class_name', 'Unknown')
        confidence = det.get('confidence', 0)

        color = colors.get(label, (0, 255, 0))

        # Draw rectangle
        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)

        # Draw label with background
        raw_text = f"{label}: {confidence:.2f}"
        # Nếu chứa ký tự không phải ASCII, chuyển về không dấu để tránh hiện ?
        text = raw_text if raw_text.isascii() else _normalize_to_ascii(raw_text)

        if hasattr(draw, 'textbbox'):
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width, text_height = draw.textsize(text, font=font)

        # Nếu muốn bỏ luôn text, không vẽ label, chỉ giữ bounding box
        # text_bg_top = max(y1 - text_height - 6, 0)
        # text_bg_bottom = y1
        # draw.rectangle(
        #    [x1, text_bg_top, x1 + text_width + 6, text_bg_bottom],
        #    fill=color
        # )
        # draw.text((x1 + 3, text_bg_top + 1), text, fill=(255, 255, 255), font=font)

    result_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    return result_image

def image_to_base64(image):
    """Chuyển ảnh thành base64 string"""
    _, buffer = cv2.imencode('.jpg', image)
    import base64
    return base64.b64encode(buffer).decode('utf-8')

def save_image(image, filename):
    """Lưu ảnh"""
    cv2.imwrite(filename, image)
