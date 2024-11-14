# Use an official Python runtime as a base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install pipenv to manage dependencies
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock to the container
COPY Pipfile Pipfile.lock ./

# Install Python dependencies using pipenv
RUN pipenv install --deploy --ignore-pipfile

# Copy the rest of the application code to the working directory
COPY . .

# Expose port 5000 if needed for your app (optional)
EXPOSE 5000

# Run the application
CMD ["pipenv", "run", "python", "app.py"]
