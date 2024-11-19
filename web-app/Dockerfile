FROM python:3.10

# Install pipenv
RUN pip install pipenv

# Set the working directory to the project root
WORKDIR /project

# Copy Pipfile and install dependencies
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

# Copy the entire project (including the `app` folder)
COPY . .

# Expose the Flask app port
EXPOSE 8080

# Set the FLASK_APP environment variable to point to the Flask app in the `app` folder
ENV FLASK_APP=src/app.py

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
