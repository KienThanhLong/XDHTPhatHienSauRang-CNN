import os
from pathlib import Path

# Đường dẫn cơ bản
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = os.path.join(BASE_DIR, 'models')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Flask config
DEBUG = True
SECRET_KEY = 'your-secret-key-change-me'

# CORS
CORS_ORIGINS = ["*"]

# Models path
CNN_MODEL_PATH = os.path.join(MODELS_DIR, 'cnn_caries_model.h5')
YOLO_MODEL_PATH = os.path.join(MODELS_DIR, 'best.pt')  # File YOLO của bạn

# Image config
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
IMAGE_SIZE = (224, 224)

# Detection config
CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.45

# Tooth classes (simplified to binary: healthy vs decay)
TOOTH_CLASSES = {
    0: "Không có sâu răng",
    1: "Có sâu răng"
}
