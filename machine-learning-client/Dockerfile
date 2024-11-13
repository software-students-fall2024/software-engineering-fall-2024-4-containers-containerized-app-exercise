# in Docker, it is common to base a new image on a previously-created image
FROM python:3.8-slim-buster

# Set the working directory in the image
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# install dependencies into the image 
COPY requirements.txt ./
COPY training_data ./training_data
RUN pip3 install --no-cache-dir -r requirements.txt


# the ADD command is how you add files from your local machine into a Docker image
# Copy the current directory contents into the container at /app
COPY . .

# expose the port that the Flask app is running on...
EXPOSE 5001

# Run main.py when the container launches
CMD [ "python3", "main.py"]