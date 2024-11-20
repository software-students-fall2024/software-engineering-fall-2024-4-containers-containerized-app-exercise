# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install system dependencies for camera access
RUN apt-get update && apt-get install -y \
    ffmpeg libsm6 libxext6 && \
    apt-get clean

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the web server
EXPOSE 5000

# Command to run the web server
CMD ["python", "web_server.py"]
