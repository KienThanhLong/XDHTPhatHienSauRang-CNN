"""
Demo version - Shows UI without requiring trained models
For full functionality, add cnn_model.h5 and yolo_model.pt to backend/models/
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
import json
import base64
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Khởi tạo Flask app
app = Flask(__name__,
           template_folder='../frontend',
           static_folder='../frontend',
           static_url_path='')

app.config['SECRET_KEY'] = 'demo-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# CORS setup
CORS(app, origins=["*"])

# Tạo thư mục uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== Routes ====================

@app.route('/')
def index():
    """Trang chủ"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """Demo API - trả về mock data để test UI"""
    try:
        # Kiểm tra file
        if 'image' not in request.files:
            return jsonify({'error': 'Không tìm thấy file ảnh'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'Tên file rỗng'}), 400
        
        # Check file type
        ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ALLOWED:
            return jsonify({'error': 'Định dạng file không được phép'}), 400
        
        # Demo: Create fake result image (gradient)
        try:
            import cv2
            import numpy as np
            
            # Read uploaded image
            file_bytes = file.read()
            nparr = np.frombuffer(file_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                raise ValueError("Không thể đọc ảnh")
            
            # Add some demo rectangles (fake detections)
            h, w = img.shape[:2]
            
            # Draw demo bounding boxes
            detections = []
            
            def _load_vietnamese_font(size=16):
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

            def draw_label(img, text, x, y, box_color=(0, 0, 0), text_color=(255, 255, 255)):
                pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                draw = ImageDraw.Draw(pil_img)
                font = _load_vietnamese_font(16)

                raw_text = text
                text = raw_text if raw_text.isascii() else ''.join(
                    c for c in unicodedata.normalize('NFKD', raw_text) if unicodedata.category(c) != 'Mn'
                )

                # Bỏ hiển thị text, chỉ vẽ bounding box
                #if hasattr(draw, 'textbbox'):
                #    bbox = draw.textbbox((0, 0), text, font=font)
                #    text_w = bbox[2] - bbox[0]
                #    text_h = bbox[3] - bbox[1]
                #else:
                #    text_w, text_h = draw.textsize(text, font=font)

                #draw.rectangle([x-2, y-2, x+text_w+2, y+text_h+2], fill=box_color)
                #draw.text((x, y), text, font=font, fill=text_color)
                return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

            # Demo detection 1
            x1, y1, x2, y2 = int(w*0.1), int(h*0.1), int(w*0.35), int(h*0.4)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            img = draw_label(img, "Khỏe mạnh: 0.95", x1, y1-22, box_color=(0, 255, 0), text_color=(0, 0, 0))
            detections.append({
                'bbox': [float(x1), float(y1), float(x2), float(y2)],
                'confidence': 0.95,
                'class_id': 0,
                'class_name': 'Khỏe mạnh',
                'classification_confidence': 0.92
            })
            
            # Demo detection 2
            x1, y1, x2, y2 = int(w*0.4), int(h*0.15), int(w*0.65), int(h*0.5)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 165, 0), 2)
            img = draw_label(img, "Sâu nhẹ: 0.88", x1, y1-22, box_color=(0, 165, 255), text_color=(0, 0, 0))
            detections.append({
                'bbox': [float(x1), float(y1), float(x2), float(y2)],
                'confidence': 0.88,
                'class_id': 1,
                'class_name': 'Sâu nhẹ',
                'classification_confidence': 0.87
            })
            
            # Demo detection 3
            x1, y1, x2, y2 = int(w*0.65), int(h*0.2), int(w*0.9), int(h*0.55)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            img = draw_label(img, "Sâu nặng: 0.91", x1, y1-22, box_color=(0, 0, 255), text_color=(255, 255, 255))
            detections.append({
                'bbox': [float(x1), float(y1), float(x2), float(y2)],
                'confidence': 0.91,
                'class_id': 3,
                'class_name': 'Sâu nặng',
                'classification_confidence': 0.89
            })
            
            # Convert to base64
            _, buffer = cv2.imencode('.jpg', img)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Mock summary
            summary = {
                'total_teeth': 3,
                'healthy': 1,
                'light_decay': 1,
                'medium_decay': 0,
                'severe_decay': 1
            }
            
            health_score = (summary['healthy'] / summary['total_teeth']) * 100
            
            # Mock recommendations
            recommendations = [
                "⚠️ Phát hiện sâu nặng - Cần tư vấn nha sĩ ngay lập tức",
                "💡 Sâu nhẹ được phát hiện - Nên vệ sinh kỹ và kiểm tra định kỳ",
                "📋 Tình trạng răng: 1 khỏe - 1 sâu nhẹ - 1 sâu nặng"
            ]
            
            response = {
                'success': True,
                'data': {
                    'image': f"data:image/jpeg;base64,{img_base64}",
                    'filename': f"demo_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                    'detections': detections,
                    'summary': summary,
                    'health_score': health_score,
                    'recommendations': recommendations
                }
            }
            
            return jsonify(response), 200
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return jsonify({
                'success': False,
                'error': 'Lỗi xử lý ảnh (Demo mode)'
            }), 500
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test-models', methods=['GET'])
def test_models():
    """Demo status"""
    return jsonify({
        'cnn_loaded': False,
        'yolo_loaded': False,
        'status': 'demo-mode-no-models-needed',
        'message': 'Demo mode - Giao diện test, thêm models để dùng thực'
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'mode': 'demo',
        'timestamp': datetime.now().isoformat()
    }), 200

# ==================== Error Handlers ====================

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File quá lớn (max 16MB)'}), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Không tìm thấy'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Lỗi máy chủ'}), 500

# ==================== Main ====================

if __name__ == '__main__':
    host = os.getenv('APP_HOST', '127.0.0.1')
    port = int(os.getenv('APP_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'

    print("""
    ╔════════════════════════════════════════════════════════╗
    ║  HỆ THỐNG CHẨN ĐOÁN SÂU RĂNG - DEMO MODE               ║
    ║  (Giao diện test - Mô phỏng kết quả Analysis)          ║
    ║                                                        ║
    ║  Để dùng đầy đủ: Thêm models vào backend/models/       ║
    ║  Rồi chạy: python app.py (thay vì app_demo.py)        ║
    ╚════════════════════════════════════════════════════════╝
    """)
    app.run(debug=debug, host=host, port=port)
