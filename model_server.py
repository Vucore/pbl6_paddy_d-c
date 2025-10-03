import cv2
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from enum import Enum
import io
import gc
import torch
import base64
from io import BytesIO
import numpy as np
import uvicorn
import logging
from ultralytics import YOLO

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(torch.__version__)
print(torch.version.cuda)
print(torch.cuda.is_available())
if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))

MODEL_CLASSIFIER_NAME = "best_model_ConViT_v4.pth"
MODEL_DETECTION_NAME = "yolov8_best_v3.pt"

class ModelType(str, Enum):
    convit = "Mô hình ConVit"

class ViTBlock(nn.Module):
    def __init__(self, dim=1024, depth=2, heads=4, mlp_dim=4096):
        super(ViTBlock, self).__init__()
        self.encoder = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=dim,
                nhead=heads,
                dim_feedforward=mlp_dim,
                dropout=0.1,
                batch_first=True
            ) for _ in range(depth)
        ])
    def forward(self, x):
        for enc in self.encoder:
            x = enc(x)
        return x

class ConViT(nn.Module):
    def __init__(self, num_classes=8):
        super(ConViT, self).__init__()
        base_model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        self.feature_extractor = nn.Sequential(*list(base_model.children())[:-3])
        self.vit1 = ViTBlock(dim=1024, depth=2, heads=4)
        self.reduce = nn.AdaptiveAvgPool2d((7,7))
        self.vit2 = ViTBlock(dim=1024, depth=1, heads=4)
        self.pool = nn.AdaptiveAvgPool2d((1,1))
        self.fc = nn.Linear(1024, num_classes)

    def forward(self, x):
        feat = self.feature_extractor(x)
        b, c, h, w = feat.shape
        tokens = feat.flatten(2).permute(0,2,1)
        tokens = self.vit1(tokens)
        feat = tokens.permute(0,2,1).view(b,c,h,w)
        feat_reduced = self.reduce(feat)
        tokens = feat_reduced.flatten(2).permute(0,2,1)
        tokens = self.vit2(tokens)
        feat = tokens.permute(0,2,1).view(b,c,7,7)
        pooled = self.pool(feat).view(b, -1)
        out = self.fc(pooled)
        return out

class_names = ['bacterial_leaf_blight', 'bacterial_panicle_blight', 'blast', 
               'brown_spot', 'leaf_roller', 'normal', 'stem_borer', 'tungro']

# Load model
model_cls = ConViT(num_classes=8)
model_cls.load_state_dict(torch.load(MODEL_CLASSIFIER_NAME, map_location=device, weights_only=True))
model_cls.to(device)
model_cls.eval()
# Load detection model

model_dt = YOLO(MODEL_DETECTION_NAME)
model_dt.to(device)
model_dt.eval()

# Image transformation
transform = transforms.Compose([
    transforms.Resize((224, 224)), 
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],
                        [0.229,0.224,0.225])
])
# Transform riêng cho YOLO detection model
transform_yolo = transforms.Compose([
    transforms.Resize((640, 640)),  # YOLO input size
    transforms.ToTensor(),
])
def detect_disease(image: Image.Image, conf: float):
    # Convert to RGB
    image = image.convert("RGB")
    
    # Apply transforms
    img_tensor = transform_yolo(image).unsqueeze(0).to(device)
    results = model_dt.predict(source=img_tensor, conf=conf, save=False, show=False)
    # Giải phóng tensor
    del img_tensor
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return results

def predict_disease(image, model_type: ModelType):
    logger.debug(f"Starting prediction with model type: {model_type.value}")
    if model_type != ModelType.convit:
        raise ValueError(f"Model type {model_type} not supported")
    
    # Convert to RGB
    image = image.convert("RGB")
    
    # Apply transforms
    img_tensor = transform(image).unsqueeze(0).to(device)
    
    # Make prediction
    with torch.no_grad():
        outputs = model_cls(img_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, pred = torch.max(probabilities, 1)
        predicted_class = class_names[pred.item()]
        confidence_value = confidence.item()
     # Giải phóng tensor
    del img_tensor, outputs, probabilities
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    return {
        "model": model_type.value,
        "disease": predicted_class,
        "confidence": round(confidence_value, 3)
    }

def run_pipeline(image: Image.Image, model_type: ModelType, conf: float):
    result_detect = detect_disease(image, conf)
    
    # Convert PIL image to numpy array for cv2
    orig_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    h, w, _ = orig_img.shape

     # Kiểm tra xem có detection không
    if len(result_detect[0].boxes) == 0:
        # Không có detection, resize toàn bộ ảnh và đưa vào mô hình phân loại
        result_cls = predict_disease(image, model_type)
        
        # Vẽ box bao quanh toàn bộ ảnh
        cv2.rectangle(orig_img, (5, 5), (w-5, h-5), (0, 255, 0), 3)
        
        # Vẽ kết quả phân loại
        pred_class = f"{result_cls['disease']} ({result_cls['confidence']*100:.1f}%)"
        cv2.putText(orig_img, pred_class, (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Vẽ threshold info
        conf_text = f"Threshold: {conf} - Full image classification"
        cv2.putText(orig_img, conf_text, (10, 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(orig_img, conf_text, (10, 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        _, buffer = cv2.imencode('.jpg', orig_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

         # Giải phóng bộ nhớ
        del buffer, orig_img, result_detect, result_cls
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return {
            "model": model_type.value,
            "disease": result_cls['disease'],
            "confidence": round(result_cls['confidence'], 3),
            "image": img_base64
        }

    # Có detection, xử lý như bình thường
    result_cls = None
    for box in result_detect[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        # Crop object
        crop = orig_img[y1:y2, x1:x2]

        # Resize 224x224 và chuyển sang tensor
        crop_pil = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
        result_cls = predict_disease(crop_pil, model_type)
        pred_class = f"{result_cls['disease']} ({result_cls['confidence']*100:.1f}%)"

        # Vẽ nhãn dự đoán lên ảnh gốc
        cv2.rectangle(orig_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(orig_img, pred_class, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        # Giải phóng bộ nhớ crop
        del crop, crop_pil
    
    # Vẽ confidence threshold lên góc trên bên trái ảnh
    conf_text = f"Threshold: {conf}"
    cv2.putText(orig_img, conf_text, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(orig_img, conf_text, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    
    # Convert processed image to base64
    _, buffer = cv2.imencode('.jpg', orig_img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    

    response_data = {
        "model": model_type.value,
        "disease": result_cls['disease'] if result_cls else "unknown",
        "confidence": round(result_cls['confidence'], 3) if result_cls else 0.0,
        "image": img_base64
    }
    # Giải phóng bộ nhớ
    del buffer, orig_img, result_detect, result_cls
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return response_data
@app.post("/predict")
async def predict(model_type: ModelType, conf: float = 0.4, file: UploadFile = File(...)):
    # Đọc và kiểm tra ảnh
    # print(f"Received request with model_type: {model_type}, filename: {file.filename}, content_type: {file.content_type}")
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File tải lên phải là ảnh"
        )
    
    try:
        # Đọc ảnh
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Thực hiện dự đoán
        # result = predict_disease(image, model_type)
        response = run_pipeline(image, model_type, conf)
         # Giải phóng bộ nhớ
        del image_data, image
        gc.collect()
        return JSONResponse(
            status_code=200,
            content=response
        )
    except Exception as e:
        # Giải phóng bộ nhớ khi có lỗi
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi trong quá trình dự đoán: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)