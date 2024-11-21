# Use the official slim Python 3.13 image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Update and install necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install pipenv
RUN pip3 install --no-cache-dir --upgrade pip pipenv gunicorn opencv-python-headless

# Copy Pipfiles and install dependencies
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --dev --skip-lock

# Copy the source code
COPY . .

# Set environment variables for Flask and Xvfb
ENV DISPLAY=:99
ENV FLASK_APP=/app/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Expose Flask's new port
EXPOSE 5000

# Start Xvfb (for GUI support, if needed) and run Flask
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
