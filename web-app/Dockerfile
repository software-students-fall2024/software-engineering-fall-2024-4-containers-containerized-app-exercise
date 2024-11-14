# Use an official Python image as the base
FROM python:3.10-slim

WORKDIR /web-app

RUN python -m pip install --upgrade pip && pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies with pipenv
RUN pipenv install --python $(which python3) --deploy --ignore-pipfile


# Copy the entire application code to the container
COPY . .

# Expose the port the web app will run on (match the docker-compose port)
EXPOSE 8000

# Set the command to run the web app
CMD ["python", "app.py"] 
