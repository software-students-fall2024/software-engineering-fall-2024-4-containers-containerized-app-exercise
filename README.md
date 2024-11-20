![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
[![Machine Learning Client CI](https://github.com/software-students-fall2024/4-containers-financiers/actions/workflows/ml-client.yml/badge.svg)](https://github.com/software-students-fall2024/4-containers-financiers/actions/workflows/ml-client.yml)
[![Web App CI](https://github.com/software-students-fall2024/4-containers-financiers/actions/workflows/web-app.yml/badge.svg)](https://github.com/software-students-fall2024/4-containers-financiers/actions/workflows/web-app.yml)

# Containerized Real-time Object Detection App

## Description

This project is a containerized web application designed for real-time object detection using machine learning. The system is built with [Flask](https://github.com/pallets/flask) for the frontend, a [YOLOv5-based](https://github.com/ultralytics/yolov5) ML client for object detection, and [MongoDB](https://www.mongodb.com/) for backend data storage. This project demonstrates the power of Dockerized microservices for deploying scalable and modular systems.

## Team members

|Reyhan Abdul Quayum|Rashed Alneyadi|Sia Chen|Yu Zhang|
|:--:|:--:|:--:|:--:|
|<a href='https://github.com/reyhanquayum'><img src='https://avatars.githubusercontent.com/u/115737572?v=4' width='40px'/></a>|<a href='https://github.com/brshood'><img src='https://avatars.githubusercontent.com/u/133962779?v=4' width='40px'/></a>|<a href='https://github.com/MambiChen'><img src='https://avatars.githubusercontent.com/u/122314736?v=4' width='40px'/></a>|<a href='https://github.com/yz7669'><img src='https://avatars.githubusercontent.com/u/180553323?v=4' width='40px'/></a>|<a

## Architecture

```plaintext
               +------------------+
               |   User Uploads   |
               +------------------+
                        |
                        v
+------------------+  HTTP  +---------------------+
|   Flask Web App  |<------>|  ML Client (YOLOv5) |
+------------------+         +---------------------+
        |                               |
        |                               v
        +-----------------> MongoDB <---+
                         Store & Retrieve
```

## Folder Structure
```
4-containers-financiers/
├── machine-learning-client/   # ML Client Service
│   ├── app.py                 # Flask app for YOLOv5 processing
│   ├── Dockerfile             # Docker configuration
│   └── requirements.txt       # Python dependencies
├── web-app/                   # Flask Web App
│   ├── app.py                 # Web interface and API endpoints
│   ├── test_app.py            # Pytest test suite
│   ├── Dockerfile             # Docker configuration
│   ├── templates/             # HTML templates
│   └── requirements.txt       # Python dependencies
├── docker-compose.yml         # Multi-container setup
└── README.md                  # Project documentation
```

## Setup Instructions

### Prerequisites
* Docker Desktop

### Installation
1. Clone the repo:
```bash
git clone https://github.com/software-students-fall2024/4-containers-financiers.git
cd 4-containers-financiers
```
2. Build and start the containers with Docker Compose
```
docker-compose up --build
```
3. Access the Web App.

 You should be able to locally access web-app running on http://127.0.0.1:5000/

## Thank you!