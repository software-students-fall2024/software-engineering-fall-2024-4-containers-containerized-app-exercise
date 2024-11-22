FROM python:3.10-slim

# Install system dependencies for pocketsphinx and swig
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    swig \
    portaudio19-dev \
    libpulse-dev \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "app.py"]
