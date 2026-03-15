import cv2
import numpy as np
import tensorflow as tf
from ultralytics import YOLO
import os
from config import (CNN_MODEL_PATH, YOLO_MODEL_PATH, CONFIDENCE_THRESHOLD,
                    IOU_THRESHOLD, TOOTH_CLASSES)
from utils.image_processing import preprocess_cnn, preprocess_yolo

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
                # TEMP: lower threshold to 0.3 to test if model can detect decay
                threshold = 0.3  # adjust this value as needed
                if prob >= threshold:
                    # positive/decay
                    class_name = "Có sâu răng"
                    class_idx = 1
                    confidence = prob
                else:
                    class_name = "Không có sâu răng"
                    class_idx = 0
                    confidence = 1 - prob
                probabilities = [1 - prob, prob]  # [healthy, decay]
            else:
                # multi‑class softmax
                class_idx = int(np.argmax(pred))
                confidence = float(pred[class_idx])
                class_name = TOOTH_CLASSES.get(class_idx, f"Class {class_idx}")
                probabilities = pred.tolist()

            return {
                'class_id': class_idx,
                'class_name': class_name,
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
                    
                    if class_name == "Không có sâu răng":
                        results['summary']['healthy'] += 1
                    elif class_name == "Có sâu răng":
                        results['summary']['light_decay'] += 1  # using light_decay for decay count
            print(f"[debug] classified {classified_count} teeth, total_teeth now {results['summary']['total_teeth']}")

            
            # Tính health score (0-100)
            if results['summary']['total_teeth'] > 0:
                healthy_ratio = results['summary']['healthy'] / results['summary']['total_teeth']
                results['health_score'] = round(healthy_ratio * 100, 2)
            
            return results
        
        except Exception as e:
            print(f"Lỗi phân tích: {str(e)}")
            return results
