# Use the official slim Python 3.13 image
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy application files into the container
COPY . /app

# Ensure pip is up-to-date
RUN pip3 install --no-cache-dir --upgrade pip

# Install dependencies from requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose Flask's default port
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Run the Flask application
CMD ["flask", "run"]
