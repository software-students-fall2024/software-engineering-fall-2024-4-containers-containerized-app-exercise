FROM python:3.10-slim

# Install CMake, build-essential, and other dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --deploy --ignore-pipfile --verbose

COPY . .

CMD ["python", "ml_client.py"]