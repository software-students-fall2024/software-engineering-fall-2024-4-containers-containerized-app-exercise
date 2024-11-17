FROM python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安装 Python 依赖
RUN pip install --no-cache-dir \
    flask==3.1.0 \
    flask-cors==5.0.0 \
    pymongo==4.10.1 \
    tensorflow==2.15.0 \
    tf-keras==2.15.0 \
    deepface==0.0.93 \
    opencv-python==4.10.0.84

COPY . .

EXPOSE 5001

ENV PYTHONUNBUFFERED=1

CMD ["python", "api.py"]