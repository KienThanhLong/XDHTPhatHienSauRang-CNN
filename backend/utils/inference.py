import cv2
import numpy as np
import tensorflow as tf
from ultralytics import YOLO
import os
import unicodedata
from config import (CNN_MODEL_PATH, YOLO_MODEL_PATH, CONFIDENCE_THRESHOLD,
                    IOU_THRESHOLD, TOOTH_CLASSES)
from utils.image_processing import preprocess_cnn, preprocess_yolo

def _normalize_to_ascii(text):
    if not isinstance(text, str):
        return text
    normalized = unicodedata.normalize('NFKD', text)
    return normalized.encode('ascii', 'ignore').decode('ascii')

class ToothAnalyzer:
    """Lớp xử lý phân tích răng bằng CNN + YOLO"""
    
    def __init__(self):
        self.cnn_model = None
        self.yolo_model = None
        self.load_models()
    
    def load_models(self):
        """Load các mô hình đã train"""
        try:
            # Load CNN model
            if os.path.exists(CNN_MODEL_PATH):
                self.cnn_model = tf.keras.models.load_model(CNN_MODEL_PATH)
                print(f"✓ Load CNN model thành công: {CNN_MODEL_PATH}")
            else:
                print(f"⚠ Không tìm thấy CNN model: {CNN_MODEL_PATH}")
            
            # Load YOLO model
            if os.path.exists(YOLO_MODEL_PATH):
                self.yolo_model = YOLO(YOLO_MODEL_PATH)
                print(f"✓ Load YOLO model thành công: {YOLO_MODEL_PATH}")
            else:
                print(f"⚠ Không tìm thấy YOLO model: {YOLO_MODEL_PATH}")
        
        except Exception as e:
            print(f"✗ Lỗi load model: {str(e)}")
    
    def detect_teeth(self, image):
        """YOLO: Phát hiện vị trí các răng"""
        if self.yolo_model is None:
            return []
        
        try:
            # Dự đoán
            results = self.yolo_model(image, conf=CONFIDENCE_THRESHOLD)
            
            detections = []
            for result in results:
                for box in result.boxes:
                    # convert numpy arrays to native Python types immediately
                    bbox_arr = box.xyxy[0].cpu().numpy()
                    detections.append({
                        'bbox': bbox_arr.tolist(),           # list is JSON-serializable
                        'confidence': float(box.conf[0].cpu().numpy()),
                        'class_id': int(box.cls[0].cpu().numpy())
                    })
            
            return detections
        except Exception as e:
            print(f"Lỗi detection: {str(e)}")
            return []
    
    def classify_tooth(self, tooth_image):
        """CNN: Phân loại mức độ sâu của một chiếc răng"""
        if self.cnn_model is None:
            return None
        
        try:
            # Tiền xử lý
            processed = preprocess_cnn(tooth_image)
            
            # Dự đoán
            prediction = self.cnn_model.predict(processed, verbose=0)

            # DEBUG: show raw probabilities for insight
            print("[debug] classify_tooth prediction:", prediction)
            pred = prediction[0]

            # handle binary vs multi-class outputs
            if pred.ndim == 0 or pred.shape[0] == 1:
                # binary output (e.g. sigmoid) -> probability of positive class
                prob = float(pred.squeeze())
                threshold = 0.3  # Lowered from 0.5 to be more sensitive to decay
                print(f"[debug] Binary classification: prob={prob:.4f}, threshold={threshold}")
                if prob >= threshold:
                    class_idx = 1
                    class_name = TOOTH_CLASSES.get(class_idx, "Sâu nhẹ")
                    confidence = prob
                else:
                    class_idx = 0
                    class_name = TOOTH_CLASSES.get(class_idx, "Khỏe mạnh")
                    confidence = 1 - prob
                probabilities = [1 - prob, prob]
                print(f"[debug] Result: class_idx={class_idx}, class_name={class_name}, confidence={confidence:.4f}")
            else:
                # multi‑class softmax
                class_idx = int(np.argmax(pred))
                confidence = float(pred[class_idx])
                class_name = TOOTH_CLASSES.get(class_idx, f"Class {class_idx}")
                probabilities = pred.tolist()
                print(f"[debug] Multi-class: class_idx={class_idx}, class_name={class_name}, confidence={confidence:.4f}, probs={probabilities}")

            # Ensure class_name is clear
            if class_idx == 0:
                class_name = TOOTH_CLASSES.get(0, "Khỏe mạnh")
            elif class_idx == 1:
                class_name = TOOTH_CLASSES.get(1, "Sâu nhẹ")
            elif class_idx == 2:
                class_name = TOOTH_CLASSES.get(2, "Sâu vừa")
            elif class_idx == 3:
                class_name = TOOTH_CLASSES.get(3, "Sâu nặng")
            else:
                class_name = TOOTH_CLASSES.get(class_idx, class_name)

            # Chuyển sang không dấu nếu font không hỗ trợ
            class_name_ascii = class_name if class_name.isascii() else _normalize_to_ascii(class_name)

            return {
                'class_id': class_idx,
                'class_name': class_name_ascii,
                'confidence': confidence,
                'probabilities': probabilities
            }
        except Exception as e:
            print(f"Lỗi phân loại: {str(e)}")
            return None
    
    def analyze_image(self, image):
        """Phân tích toàn bộ ảnh"""
        results = {
            'detections': [],
            'summary': {
                'total_teeth': 0,
                'healthy': 0,
                'light_decay': 0,
                'medium_decay': 0,
                'severe_decay': 0
            },
            'health_score': 0.0
        }
        
        try:
            # Bước 1: Phát hiện vị trí các răng (YOLO)
            detections = self.detect_teeth(image)
            
            # Bước 2: Phân loại mức độ sâu cho từng răng (CNN)
            print(f"[debug] detected {len(detections)} teeth")
            classified_count = 0
            for detection in detections:
                x1, y1, x2, y2 = map(int, detection['bbox'])
                
                # Crop hình ảnh từng chiếc răng
                tooth_image = image[y1:y2, x1:x2].copy()
                
                # Phân loại
                classification = self.classify_tooth(tooth_image)
                if classification:
                    classified_count += 1
                    detection['class_id'] = classification['class_id']
                    detection['class_name'] = classification['class_name']
                    detection['classification_confidence'] = classification['confidence']
                    detection['probabilities'] = classification['probabilities']
                    
                    results['detections'].append(detection)
                    
                    # Cập nhật thống kê
                    results['summary']['total_teeth'] += 1
                    class_name = classification['class_name']

                    if 'khỏe' in class_name.lower() or 'khong' in class_name.lower():
                        results['summary']['healthy'] += 1
                    elif 'sâu nhẹ' in class_name.lower():
                        results['summary']['light_decay'] += 1
                    elif 'sâu vừa' in class_name.lower():
                        results['summary']['medium_decay'] += 1
                    elif 'sâu nặng' in class_name.lower() or 'nặng' in class_name.lower():
                        results['summary']['severe_decay'] += 1
                    elif 'sâu' in class_name.lower():
                        results['summary']['medium_decay'] += 1
            print(f"[debug] classified {classified_count} teeth, total_teeth now {results['summary']['total_teeth']}")

            
            # Tính health score (0-100)
            if results['summary']['total_teeth'] > 0:
                healthy_ratio = results['summary']['healthy'] / results['summary']['total_teeth']
                results['health_score'] = round(healthy_ratio * 100, 2)
            
            return results
        
        except Exception as e:
            print(f"Lỗi phân tích: {str(e)}")
            return results
