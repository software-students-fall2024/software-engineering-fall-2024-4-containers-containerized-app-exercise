# Use the official slim Python 3.13 image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Update and install necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    linux-headers-generic \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install pipenv
RUN pip3 install --no-cache-dir --upgrade pip pipenv

# Copy Pipfiles and install dependencies
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --dev --skip-lock

# Copy the source code
COPY . .

# Expose any necessary ports (if required for ML APIs)
EXPOSE 8000

# Define the default command to run your ML client (adjust as needed)
CMD ["python", "mouse_tracker.py"]