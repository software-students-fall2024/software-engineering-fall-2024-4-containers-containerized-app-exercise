# Use a base Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Copy Pipfile and Pipfile.lock to the container
COPY Pipfile Pipfile.lock /app/

# Install Python dependencies from Pipfile using pipenv
RUN pipenv install --deploy --ignore-pipfile  
# --ignore-pipfile ensures it uses the Pipfile.lock

# Copy the rest of the application code into the container
COPY . /app

# Define the default command to run the client
CMD ["pipenv", "run", "python", "client.py"]
