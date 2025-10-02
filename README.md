# Rice Disease Detection Project

This project is a FastAPI application for detecting rice diseases using machine learning models. It provides an API for uploading images of rice plants and receiving predictions about potential diseases.

## Project Structure

```
rice-disease-detection-docker
├── docker
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── app
│   ├── model_server.py
│   ├── models
│   │   ├── best_model_ConViT_v4.pth
│   │   └── yolov8_best_v3.pt
│   └── __init__.py
├── scripts
│   ├── build.sh
│   ├── run.sh
│   └── stop.sh
├── .dockerignore
├── .env.example
└── README.md
```

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd rice-disease-detection-docker
   ```

2. Build the Docker image:
   ```
   cd docker
   ./build.sh
   ```

3. Run the application:
   ```
   ./run.sh
   ```

### Usage

- Send a POST request to the `/predict` endpoint with an image file to receive predictions about rice diseases.
- You can adjust the confidence threshold and select different models using the API.

### Stopping the Application

To stop the application, run:
```
./stop.sh
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.