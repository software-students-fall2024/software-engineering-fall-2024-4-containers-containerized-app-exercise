# Use Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies including ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Install system dependencies including FLAC
RUN apt-get update && \
    apt-get install -y flac && \
    rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . .

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flask app
EXPOSE 5000

# Start the app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app:app"]

