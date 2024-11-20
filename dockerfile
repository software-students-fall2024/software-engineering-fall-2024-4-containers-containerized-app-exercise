# Use the official slim Python 3.13 image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Update and install necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    linux-headers-generic \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install pipenv
RUN pip3 install --no-cache-dir --upgrade pip pipenv

# Install dependencies for machine-learning-client
WORKDIR /app/machine-learning-client
COPY machine-learning-client/Pipfile machine-learning-client/Pipfile.lock ./
RUN pipenv install --system --deploy --dev --skip-lock \
    && pip3 install opencv-python-headless

# Install dependencies for web-app
WORKDIR /app/web-app
COPY web-app/Pipfile web-app/Pipfile.lock ./
RUN pipenv install --system --deploy --dev --skip-lock

# Copy application source code
COPY machine-learning-client /app/machine-learning-client
COPY web-app /app/web-app

# Set environment variables for Flask and Xvfb
ENV DISPLAY=:99
ENV FLASK_APP=/app/web-app/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Expose Flask's default port
EXPOSE 5000

# Start Xvfb and Flask application
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x16 & flask run"]
