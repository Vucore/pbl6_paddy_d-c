import cv2
import torch
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from enum import Enum
import io
import gc
from typing import List
import torch
import base64
import numpy as np
import uvicorn
import logging
from model_cls import load_model_classifier_conVit, load_model_classifier_plantVit, transform_image_cls, get_class_name
from model_yolo import load_model_detection_yolo, transform_image_yolo

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(torch.__version__)
print(torch.version.cuda)
print(torch.cuda.is_available())
if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))

MODEL_CONVIT_CLASSIFIER_NAME = "best_model_ConViT_v51.pth"
MODEL_PLANTVIT_CLASSIFIER_NAME = "PlantXVit_best.pth"
MODEL_DETECTION_NAME = "yolov8_best_v3.pt"

class ModelType(str, Enum):
    convit = "Model ConVit"
    planvit = "Model PlantVit"


model_convit_cls = load_model_classifier_conVit(MODEL_CONVIT_CLASSIFIER_NAME, device)
model_plantvit_cls = load_model_classifier_plantVit(MODEL_PLANTVIT_CLASSIFIER_NAME, device)
transform = transform_image_cls()

model_yolo_dt = load_model_detection_yolo(MODEL_DETECTION_NAME, device)
transform_yolo = transform_image_yolo()

def detect_disease(image: Image.Image, conf: float):
    # Convert to RGB
    image = image.convert("RGB")
    
    # Apply transforms
    img_tensor = transform_yolo(image).unsqueeze(0).to(device)
    results = model_yolo_dt.predict(source=img_tensor, conf=conf, save=False, show=False)
    # Giải phóng tensor
    del img_tensor
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return results

def predict_disease(image, model_type: ModelType):
    logger.debug(f"Starting prediction with model type: {model_type.value}")
    if model_type == ModelType.convit:
        model_cls = model_convit_cls
    elif model_type == ModelType.planvit:
        model_cls = model_plantvit_cls
    else:
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
        predicted_class = get_class_name(pred.item())
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
    boxes = getattr(result_detect[0], "boxes", [])
    if len(boxes) == 0:
        result_cls = predict_disease(image, model_type)
        
        # Vẽ box bao quanh toàn bộ ảnh
        cv2.rectangle(orig_img, (5, 5), (w-5, h-5), (0, 0, 255), 3)      
               
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
    # Kiểm tra xem có detection không
    # if result_detect is None or len(result_detect[0].boxes) == 0:
    #     # Không có detection, resize toàn bộ ảnh và đưa vào mô hình phân loại
    #     result_cls = predict_disease(image, model_type)
        
    #     # Vẽ box bao quanh toàn bộ ảnh
    #     cv2.rectangle(orig_img, (5, 5), (w-5, h-5), (0, 0, 255), 3)      
               
    #     _, buffer = cv2.imencode('.jpg', orig_img)
    #     img_base64 = base64.b64encode(buffer).decode('utf-8')

    #      # Giải phóng bộ nhớ
    #     del buffer, orig_img, result_detect, result_cls
    #     gc.collect()
    #     if torch.cuda.is_available():
    #         torch.cuda.empty_cache()
    #     return {
    #         "model": model_type.value,
    #         "disease": result_cls['disease'],
    #         "confidence": round(result_cls['confidence'], 3),
    #         "image": img_base64
    #     }

    # Có detection, xử lý như bình thường
    result_cls = None
    # for box in result_detect[0].boxes:
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        # Crop object
        crop = orig_img[y1:y2, x1:x2]

        # Resize 224x224 và chuyển sang tensor
        crop_pil = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
        result_cls = predict_disease(crop_pil, model_type)

        # Vẽ nhãn dự đoán lên ảnh gốc
        cv2.rectangle(orig_img, (x1, y1), (x2, y2), (0, 0, 255), 3)

        # Giải phóng bộ nhớ crop
        del crop, crop_pil

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
async def predict(model_type: List[ModelType] = Form(["Model ConVit", "Model PlantVit"]), conf: float = Form(0.3), file: UploadFile = File(...)):
    # Đọc và kiểm tra ảnh
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File tải lên phải là ảnh"
        )
    result = []
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        for mt in model_type:
            response = run_pipeline(image, mt, conf)
            result.append(response)
         
        # Giải phóng bộ nhớ
        del image_data, image
        gc.collect()
        return JSONResponse(
            status_code=200,
            content=result
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