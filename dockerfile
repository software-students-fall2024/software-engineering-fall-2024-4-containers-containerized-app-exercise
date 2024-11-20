# Use the official slim Python 3.13 image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Update the package manager and install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    linux-headers-generic \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Ensure pip is up-to-date
RUN pip3 install --no-cache-dir --upgrade pip

# Install pipenv globally
RUN pip3 install pipenv

# Install machine-learning-client dependencies
WORKDIR /app/machine-learning-client
COPY machine-learning-client/Pipfile machine-learning-client/Pipfile.lock ./
RUN pipenv install --system --deploy --dev --skip-lock \
    && pip3 install opencv-python-headless

# Install web-app dependencies
WORKDIR /app/web-app
COPY web-app/Pipfile web-app/Pipfile.lock ./
RUN pipenv install --system --deploy --dev --skip-lock

# Copy the machine-learning-client and web-app source code into the container
COPY machine-learning-client /app/machine-learning-client
COPY web-app /app/web-app

# Expose Flask's default port
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=/app/web-app/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Set the working directory for Flask
WORKDIR /app/web-app

# Run the Flask application
CMD ["flask", "run"]
