# ml-client/Dockerfile
FROM python:3.9

# Set working directory inside the container
WORKDIR /app

# Install dependencies (TensorFlow, PyTorch, or other ML libraries)
RUN pip3 install --no-cahe-dir  Z Z

# Copy your machine learning code
COPY . .

# Expose the port (if your ML client exposes any services)
EXPOSE 5001

# Start the ML client (adjust as needed)
CMD ["python3", "speech_to_text.py"]