# Use Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /main

# Install system dependencies including FLAC
RUN apt-get update && \
    apt-get install -y gcc libsndfile1 flac && \
    rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . .

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Set the Python path to include the `src` directory
ENV PYTHONPATH=/main/src

# Expose port 5001 for the Flask app
EXPOSE 5001

# Start the app
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "src.main:app"]

