# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install Python dependencies from requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir flask

# Expose port 5000 for the Flask web server
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "web_server.py"]