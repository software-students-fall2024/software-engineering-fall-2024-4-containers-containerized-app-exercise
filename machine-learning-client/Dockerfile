# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies (e.g., for PyTorch and Flask)
RUN apt-get update && apt-get install -y \
    libatlas-base-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies from requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port that Flask will run on
EXPOSE 3000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Command to run the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=3000"]
