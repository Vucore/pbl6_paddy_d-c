# 🌾 Hệ Thống Nhận Diện Bệnh Lúa với AI

Dự án sử dụng Deep Learning để nhận diện và phân loại các bệnh trên cây lúa thông qua hình ảnh, tích hợp với Telegram Bot để người dùng có thể dễ dàng sử dụng.

## 📋 Mục Lục

- [Tính Năng](#-tính-năng)
- [Công Nghệ Sử Dụng](#-công-nghệ-sử-dụng)
- [Cài Đặt](#-cài-đặt)
- [Sử Dụng](#-sử-dụng)
- [API Documentation](#-api-documentation)
- [Deploy với Docker](#-deploy-với-docker)
- [Cấu Trúc Dự Án](#-cấu-trúc-dự-án)
- [Mô Hình AI](#-mô-hình-ai)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Tính Năng

### 🤖 Telegram Bot
- **Giao diện thân thiện**: Tương tác qua Telegram Bot
- **Chọn mô hình**: Hỗ trợ 3 loại mô hình AI khác nhau
- **Điều chỉnh độ tin cậy**: Tùy chỉnh threshold từ 0.1-0.9
- **Upload ảnh**: Gửi ảnh trực tiếp để phân tích

### 🧠 AI Models
- **ConViT Model**: Mô hình phân loại sử dụng Convolutional Vision Transformer
- **YOLO Model**: Mô hình phát hiện và định vị bệnh trên ảnh
- **CNN Model**: Mô hình Convolutional Neural Network cơ bản

### 🔍 Nhận Diện Bệnh
Hệ thống có thể nhận diện 8 loại bệnh phổ biến trên lúa:
1. **Bacterial Leaf Blight** - Bệnh cháy lá do vi khuẩn
2. **Bacterial Panicle Blight** - Bệnh cháy bông do vi khuẩn  
3. **Blast** - Bệnh đạo ôn
4. **Brown Spot** - Bệnh đốm nâu
5. **Leaf Roller** - Sâu cuốn lá
6. **Normal** - Lúa khỏe mạnh
7. **Stem Borer** - Sâu đục thân
8. **Tungro** - Bệnh vàng lá lùn

## 🛠️ Công Nghệ Sử Dụng

### Backend
- **FastAPI**: Web framework hiệu suất cao
- **PyTorch**: Framework deep learning
- **Ultralytics YOLO**: Object detection
- **OpenCV**: Computer vision
- **Pillow**: Image processing

### Bot
- **python-telegram-bot**: Telegram Bot API
- **Requests**: HTTP client
- **python-dotenv**: Environment management

### DevOps
- **Docker**: Containerization
- **Uvicorn**: ASGI server

## 📦 Cài Đặt

### Yêu Cầu Hệ Thống
- Python 3.8+
- CUDA (tùy chọn, để tăng tốc GPU)
- 4GB RAM (tối thiểu)
- 2GB dung lượng trống

### 1. Clone Repository
```bash
git clone https://github.com/Vucore/pbl6_paddy_d-c.git
cd pbl6_paddy_d-c
```

### 2. Tạo Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu Hình Environment
Tạo file `.env` từ `.env.example`:
```bash
copy .env.example .env
```

Chỉnh sửa file `.env`:
```env
TOKEN_TELE=your_telegram_bot_token_here
```

### 5. Tải Model Files
Đảm bảo các file model sau có trong thư mục gốc:
- `best_model_ConViT_v4.pth`
- `yolov8_best_v3.pt`

## 🎯 Sử Dụng

### Khởi Động Backend Server
```bash
python model_server.py
```
Server sẽ chạy tại: `http://localhost:8000`

### Khởi Động Telegram Bot
```bash
python bot_tele.py
```

### Sử Dụng Telegram Bot

1. **Bắt đầu**: Gửi `/start` để xem hướng dẫn
2. **Chọn mô hình**: Sử dụng `/select` để chọn mô hình AI
3. **Điều chỉnh độ tin cậy**: Dùng `/conf 0.5` để set threshold
4. **Upload ảnh**: Dùng `/upload` và gửi ảnh bệnh lúa

### Ví Dụ Workflow
```
/start → /select → Chọn "Mô hình ConVit" → /conf 0.6 → /upload → Gửi ảnh
```

## 📖 API Documentation

### Endpoints

#### POST `/predict`
Nhận diện bệnh từ ảnh upload

**Parameters:**
- `model_type`: Loại mô hình (`"Mô hình ConVit"` hoặc `"Mô hình YOLO"`)
- `conf`: Độ tin cậy (0.1-0.9, mặc định: 0.4)
- `file`: File ảnh (JPG, PNG)

**Response:**
```json
{
    "model": "Mô hình ConVit",
    "disease": "blast",
    "confidence": 0.856,
    "image": "base64_encoded_result_image"
}
```

### Swagger UI
Truy cập: `http://localhost:8000/docs`

## 🐳 Deploy với Docker

### 1. Build Docker Image
```bash
docker build -t rice-disease-api .
```

### 2. Run Container
```bash
docker run -p 8000:8000 rice-disease-api
```

### 3. Docker Compose (Recommended)
```bash
docker-compose up -d
```

## 📁 Cấu Trúc Dự Án

```
pbl6_paddy_d-c/
├── 📄 bot_tele.py              # Telegram Bot
├── 📄 model_server.py          # FastAPI Backend
├── 📄 model.py                 # Model definitions
├── 📄 requirements.txt         # Dependencies
├── 📄 .env                     # Environment variables
├── 📄 .gitignore              # Git ignore rules
├── 📄 README.md               # Documentation
├── 🗂️ models/                  # AI Model files
│   ├── best_model_ConViT_v4.pth
│   └── yolov8_best_v3.pt
├── 🗂️ tests/                   # Test images
│   ├── test.jpg
│   ├── test2.jpg
│   └── ...
└── 🗂️ docker/                  # Docker configurations
    ├── Dockerfile
    └── docker-compose.yml
```

## 🧠 Mô Hình AI

### ConViT (Convolutional Vision Transformer)
- **Architecture**: Hybrid CNN + Vision Transformer  
- **Input Size**: 224x224x3
- **Classes**: 8 bệnh lúa
- **Accuracy**: ~92% trên test set

### YOLO v8
- **Purpose**: Object detection + localization
- **Input Size**: 640x640x3  
- **Output**: Bounding boxes + class predictions
- **mAP**: ~0.85

### Model Pipeline
1. **Detection**: YOLO phát hiện vùng bệnh
2. **Classification**: ConViT phân loại loại bệnh
3. **Visualization**: Vẽ bounding box + confidence score

## 🔧 Troubleshooting

### Lỗi Thường Gặp

**1. CUDA Out of Memory**
```bash
# Giảm batch size hoặc chạy trên CPU
export CUDA_VISIBLE_DEVICES=""
```

**2. Model File Not Found**
```bash
# Kiểm tra đường dẫn model files
ls -la *.pth *.pt
```

**3. Telegram Bot Token Invalid**
```bash
# Kiểm tra .env file và bot token
cat .env
```

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📊 Performance

### Benchmarks
- **Response time**: ~2-5 giây/ảnh
- **Accuracy**: 90-95% (tùy loại bệnh)
- **Memory usage**: ~2GB GPU / 4GB RAM
- **Throughput**: ~20 requests/phút

## 🔐 Security

- Environment variables cho sensitive data
- Input validation cho file uploads  
- Rate limiting trên API endpoints
- Secure Docker container configuration

## 📈 Future Roadmap

- [ ] Thêm mô hình ensemble
- [ ] Hỗ trợ video input
- [ ] Mobile app companion
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration với IoT sensors

## 📞 Support

- **Email**: support@ricedisease.ai
- **Telegram**: @RiceDiseaseBot
- **Issues**: [GitHub Issues](https://github.com/Vucore/pbl6_paddy_d-c/issues)

## 📄 License

Dự án được phân phối dưới MIT License. Xem `LICENSE` để biết thêm thông tin.

---

**Made with ❤️ by PBL6 Team**