# backend/Dockerfile

# Use a Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install dependencies from requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that Flask will run on
EXPOSE 3000

# Run the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--port=3000"]
