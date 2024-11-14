FROM python:3.10-slim

# Install CMake, build-essential, and other dependencies, including libGL and libglib
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy Pipfile and Pipfile.lock and install dependencies with pipenv
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --deploy --ignore-pipfile --verbose

# Copy the application code
COPY . .

CMD ["python", "ml_client.py"]
