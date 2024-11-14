# Use an official Python image as the base
FROM python:3.10-slim

# Set the working directory
WORKDIR /machine_learning_client

# Upgrade pip and install pipenv
RUN python -m pip install --upgrade pip && pip install pipenv

# Copy Pipfile and Pipfile.lock for dependency installation
COPY Pipfile Pipfile.lock ./

# Install dependencies with pipenv, specifying the Python version
RUN pipenv install --python $(which python3) --deploy --ignore-pipfile

# Copy the rest of the application code into the container
COPY . .

# Expose the port (change to 5000 if the machine learning client is set up for that port)
EXPOSE 5000

# Set the command to run the ML client
CMD ["pipenv", "run", "python", "ml_client.py"]
