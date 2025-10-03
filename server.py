from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
from enum import Enum
from typing import Optional
import numpy as np
from PIL import Image
import io

app = FastAPI()

class ModelType(str, Enum):
    CNN = "Mô hình CNN"
    VGG16 = "Mô hình VGG16"
    RESNET50 = "Mô hình ResNet50"

# Giả lập kết quả dự đoán (sau này sẽ thay bằng mô hình thực)
def predict_disease(image: Image.Image, model_type: ModelType) -> dict:
    return {
        "model": model_type,
        "disease": "Bệnh đạo ôn",
        "confidence": 0.95
    }

@app.post("/predict")
async def predict(model_type: ModelType, file: UploadFile = File(...)):
    # Đọc và kiểm tra ảnh
    if not file.content_type.startswith("image/"):
        return JSONResponse(
            status_code=400,
            content={"error": "File tải lên phải là ảnh"}
        )
    
    try:
        # Đọc ảnh
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Thực hiện dự đoán
        result = predict_disease(image, model_type)
        
        return JSONResponse(
            status_code=200,
            content={
                "model": result["model"],
                "disease": result["disease"],
                "confidence": result["confidence"]
            }
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Lỗi xử lý ảnh: {str(e)}"}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
