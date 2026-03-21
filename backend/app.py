from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import traceback

from config import (UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE,
                    SECRET_KEY, CORS_ORIGINS)
from utils.image_processing import (allowed_file, read_image, draw_results,
                                   image_to_base64, save_image)
from utils.inference import ToothAnalyzer

# Khởi tạo Flask app
app = Flask(__name__,
           template_folder='../frontend',
           static_folder='../frontend',
           static_url_path='')

app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# CORS setup
CORS(app, origins=CORS_ORIGINS)

# Tạo thư mục uploads nếu chưa có
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Khởi tạo analyzer
analyzer = ToothAnalyzer()

# ==================== Routes ====================

@app.route('/')
def index():
    """Trang chủ"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """API phân tích ảnh"""
    try:
        # Kiểm tra file
        if 'image' not in request.files:
            return jsonify({'error': 'Không tìm thấy file ảnh'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'Tên file rỗng'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Định dạng file không được phép'}), 400
        
        # Lấy thông tin bệnh nhân từ form
        patient_info = {
            'name': request.form.get('patient_name', '').strip(),
            'dob': request.form.get('patient_dob', '').strip(),
            'gender': request.form.get('patient_gender', '').strip(),
            'address': request.form.get('patient_address', '').strip(),
        }

        # Đọc ảnh
        image_data = file.read()
        image = read_image(image_data)
        
        # Phân tích
        results = analyzer.analyze_image(image)

        # make sure all returned values are JSON-friendly (no numpy objects)
        # bbox arrays already converted in inference, but be safe in case other numpy types slip through
        for det in results.get('detections', []):
            if isinstance(det.get('bbox'), np.ndarray):
                det['bbox'] = det['bbox'].tolist()

        # Vẽ kết quả
        result_image = draw_results(image, results['detections'])
        
        # Lưu ảnh
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"result_{timestamp}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        save_image(result_image, filepath)
        
        # Chuyển ảnh thành base64
        result_image_base64 = image_to_base64(result_image)
        
        # Build response dict
        response = {
            'success': True,
            'data': {
                'patient_info': patient_info,
                'analysis_date': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'image': f"data:image/jpeg;base64,{result_image_base64}",
                'filename': filename,
                'detections': results['detections'],
                'summary': results['summary'],
                'health_score': results['health_score'],
                'recommendations': get_recommendations(results['summary'])
            }
        }

        # convert any numpy types deep within the response so jsonify won't fail
        response = convert_numpy(response)
        return jsonify(response), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test-models', methods=['GET'])
def test_models():
    """Kiểm tra trạng thái các mô hình"""
    return jsonify({
        'cnn_loaded': analyzer.cnn_model is not None,
        'yolo_loaded': analyzer.yolo_model is not None,
        'status': 'ready' if (analyzer.cnn_model and analyzer.yolo_model) else 'incomplete'
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    }), 200

# ==================== Helper Functions ====================


def convert_numpy(obj):
    """Recursively convert numpy data types to native Python types.
    This handles arrays, scalars (int64/float32/...), and nested lists/dicts.
    """
    import numpy as _np

    if isinstance(obj, _np.ndarray):
        return obj.tolist()
    if isinstance(obj, (_np.integer,)):
        return int(obj)
    if isinstance(obj, (_np.floating,)):
        return float(obj)
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_numpy(v) for v in obj]
    return obj


def get_recommendations(summary):
    """Tạo khuyến cáo dựa trên kết quả phân tích (binary: healthy vs decay)"""
    recommendations = []
    
    total = summary['total_teeth']
    if total == 0:
        return ["Vui lòng tải lên ảnh răng để phân tích"]
    
    decay_teeth = total - summary['healthy']
    decay_percentage = (decay_teeth / total) * 100
    
    if decay_teeth > 0:
        recommendations.append("⚠️ Phát hiện có sâu răng - Nên tư vấn nha sĩ sớm")
        if decay_percentage > 50:
            recommendations.append("🦷 Tình trạng sâu răng cao - Cần điều trị toàn diện")
        else:
            recommendations.append("💡 Hãy vệ sinh kỹ và khám định kỳ")
    else:
        recommendations.append("✨ Tuyệt vời! Toàn bộ răng khỏe mạnh - Tiếp tục duy trì")
    
    return recommendations

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
    ║   HỆtoast CHẨN ĐOÁN SÂU RĂNG BẰNG CNN + YOLO          ║
    ║   Khởi chạy máy chủ...                                 ║
    ╚════════════════════════════════════════════════════════╝
    """)
    app.run(debug=debug, host=host, port=port)
