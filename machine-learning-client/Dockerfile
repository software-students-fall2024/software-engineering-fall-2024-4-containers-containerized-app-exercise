# Use a base Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy Pipfile and Pipfile.lock to the container
COPY Pipfile Pipfile.lock /app/

# Install pipenv and dependencies
RUN pip install pipenv && pipenv install --system --deploy

# Copy the rest of the application code into the container
COPY . /app

# Define the default command to run the client
CMD ["python", "client.py"]
