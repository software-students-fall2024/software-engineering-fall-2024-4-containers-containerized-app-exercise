# Base image on previously created image
FROM python:3.8-slim-buster

# Set the working directory in image
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# how we add fules from local machine to docker image
#cop ycurr dir into container at /app
ADD . .

#default 5000
EXPOSE 5000

# Run the application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
