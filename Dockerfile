# Use the official slim Python 3.13 image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only Pipfile and Pipfile.lock first for dependency installation
COPY Pipfile Pipfile.lock /app/

# Ensure pip is up-to-date
RUN pip3 install --no-cache-dir --upgrade pip

# Install pipenv
RUN pip3 install pipenv

# Install all dependencies (including dev dependencies)
RUN pipenv install --system --deploy --dev

# Copy the rest of the application files into the container
COPY . /app

# Expose Flask's default port
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Run the Flask application
CMD ["flask", "run"]
