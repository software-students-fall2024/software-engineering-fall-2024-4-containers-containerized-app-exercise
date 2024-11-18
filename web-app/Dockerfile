# Use the official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-dev gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv using pip
RUN pip install --upgrade pip && pip install pipenv

# Copy Pipfile and Pipfile.lock into the container
COPY Pipfile Pipfile.lock ./

# Install Python dependencies using Pipenv
RUN pipenv install --system --deploy

# Copy the rest of the application code
COPY . .

# Expose the port your Flask app will run on
EXPOSE 3000

# Set environment variable for Flask
ENV FLASK_ENV=production

# Run the application
CMD ["python", "app.py"]
