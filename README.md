
# Containerized App Exercise

A containerized app that performs speech-to-text conversion using machine learning, with a web interface to display results and a database for data storage.

# Badges
![Machine Learning Client Workflow Status](https://github.com/software-students-fall2024/4-containers-fivegum/actions/workflows/ml-client-tests.yml/badge.svg)
![Web App Workflow Status](https://github.com/software-students-fall2024/4-containers-fivegum/actions/workflows/testing.yml/badge.svg)

# About

The Speech-to-Text App consists of three main components:
1. **Machine Learning Client**: Processes audio data and converts speech to text.
2. **Web App**: Allows users to display processed text and upload audio files.
3. **Database**: A MongoDB database storing metadata and transcriptions. 

# Subsystems

## 1. Machine Learning Client

### Features:
- Captures and processes audio data.
- Performs speech-to-text conversion.
- Stores transcription results and metadata in MongoDB.

## 2. Web App

### Features:
- Allows users to upload audio files for transcription.
- Displays transcription results.
- Connects to MongoDB to fetch and store data.

## 3. Database

### Features:
- MongoDB instance running in a Docker container.
- Stores audio metadata and processed text.

### Setup:
Create a .env file with the following:
```
MONGODB_USERNAME=user
MONGODB_PASSWORD=pass
MONGODB_URI=mongodb://user:pass@mongodb:27017
SECRET=your-secret-key
```

To run MongoDB locally using Docker:
```
docker run --name mongodb -d -p 27017:27017 mongo
```

# Installation and Usage

### Steps to Run the Application:
1. Clone the repo:
   ```
   git clone https://github.com/software-students-fall2024/4-containers-fivegum.git
   cd 4-containers-fivegum
   ```
2. Start the containers using Docker Compose:
   ```
   docker-compose up --build
   ```

### Running Tests:
To run tests for individual subsystems:
1. Machine Learning Client:
   ```
   cd machine-learning-client
   pytest
   ```
2. Web App:
   ```
   cd web-app
   pytest
   ```

# Group Members
- Neha Magesh: [link](https://github.com/nehamagesh)
- Luca Ignatescu: [link](https://github.com/LucaIgnatescu)
- Tahsin Tawhid: [link](https://github.com/tahsintawhid)
- James Whitten: [link](https://github.com/jwhit0)