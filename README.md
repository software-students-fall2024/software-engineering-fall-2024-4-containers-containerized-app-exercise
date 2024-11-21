![Machine Learning Client](https://github.com/software-students-fall2024/4-containers-rawf/actions/workflows/ml-client-ci.yml/badge.svg)

![Web App](https://github.com/software-students-fall2024/4-containers-rawf/actions/workflows/web-app-ci.yml/badge.svg)

![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)


# CONTAINERIZED APP EXERCISE

Build a containerized app that uses machine learning. See [instructions](./instructions.md) for details.

## TABLE OF CONTENTS
1. [Description](#description)
2. [Configuration](#configuration-steps)
3. [Setup Steps](#setup-steps)
4. [Team Members](#team-members)
5. [Task Board](https://github.com/orgs/software-students-fall2024/projects/120)

## DESCRIPTION

Our containerized web application is designed to play an interactive game of *Rock-Paper-Scissors* with the user by utilizing machine learning for image recognition. Built with scalability and modularity in mind, the app leverages Docker to containerize the application, making deployment and management straightforward across different environments.

***Key Features:***

**1. Image Recognition with Machine Learning:**

- Uses a pre-trained machine learning model to recognize hand gestures (rock, paper, scissors) via the user's webcam or uploaded image
- Processes images in real-time to identify the user's choice 
- Compares predicted user choice with computer's randomly generated choice to determine the winner of current round
 
**2. Web-Based User Interface:**

- Provides an intuitive and responsive web interface that guides users through the game
- Easily play the game directly from your web browser without needing to install any additional software
- Provides real-time feedback, with visual cues showing the user's move, computer's move, and outcome of each round

## CONFIGURATION STEPS

**1. Install Docker and Docker Compose**
- Ensure Docker is installed on your system
- Install Docker Compose to manage multiple containers

**2. Setup MongoDB Database:** ```docker run --name mongodb -d -p 27017:27017 mongo```

**3. Configure Machine-Learning Client:** Navigate to the machine-learning-client directory...
- *Install Dependencies:* ```pipenv install```
- *Format and Lint:*
   ```
   black .
   pyling .
   ```
- *Run Unit Tests:* ```pytest --cov=machine-learning-client```

**4. Configure Web App:** Navigate to the web-app directory...
- *Install Dependencies:* ```pipenv install```
- *Format and Lint:*
   ```
   black .
   pylint .
   ```
- *Run Unit Tests:* ```pytest --cov=web-app```

## SETUP STEPS

**1. Clone the Repository**
```
git clone <[repository-url](https://github.com/software-students-fall2024/4-containers-rawf)>
cd <4-containers-rawf>
```

**2. Build & Run Containers**
- *For Machine Learning Client:*
   ```
   docker build -t ml-client ./machine-learning-client
   docker run -d --name ml-client ml-client
   ```
  
- *For Web App:*
   ```
   docker build -t web-app ./web-app
   docker run -d -p 5000:5000 --name web-app web-app
   ```

**3. Integrate with Docker Compose:** ```docker-compose up```

**4. Play!:** access our web app ([here](http://localhost:5000)! 


## TEAM MEMBERS

- ***Wenli Shi:*** ([WenliShi2332](https://github.com/WenliShi2332))
- ***Alex Hsu:*** ([hsualexotake](https://github.com/hsualexotake))
- ***Reese Burns:*** ([reeseburns](https://github.com/reeseburns))
- ***Finn Eskeland:*** ([finn1003](https://github.com/finn1003))
