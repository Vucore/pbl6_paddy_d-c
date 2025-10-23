import torchvision.transforms as transforms
from ultralytics import YOLO

def load_model_detection_yolo(MODEL_DETECTION_NAME, device):
    model_dt = YOLO(MODEL_DETECTION_NAME)
    model_dt.to(device)
    model_dt.eval()
    return model_dt

def transform_image_yolo():
    transform_yolo = transforms.Compose([
        transforms.Resize((640, 640)),  # YOLO input size
        transforms.ToTensor(),
    ])
    return transform_yolo