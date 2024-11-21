![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
![Machine-Learning CI/CD](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/build-ml.yml/badge.svg)
![Web App CI/CD](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/build-web-app.yml/badge.svg)

# Containerized App Exercise

# Description

Sonus is a a speech-to-text application that allows the user to input speech through access to a microphone, as well as with an audio file. By providing more input, the application should become more accuracte wit its translation, as the machine learning client analyzes and keeps track of background noise!

# Team Members

[Lucia Song](https://github.com/lys7942) <br>
[Chelsea Hodgson](https://github.com/Chelsea-Hodgson) <br>
[Yeshni Savadatti](https://github.com/yeshnii) <br>
[Alan Zhao](https://github.com/Alan3562) <br>

# How to Run the Application

1. Make sure to install, run, and login to Docker Destop on your local machine. You can do so with this [link](https://www.docker.com/products/docker-desktop/). <br>

2. Make sure to have docker-compose installed. <br>

3. Clone the repository by using the command: <br>
```git clone git@github.com:software-students-fall2024/4-containers-scoobygang2.git``` <br>

4. Navigate into the project root folder.

5. To run the app, use the command: <br>
```docker-compose up --build``` <br>

Or run in detatched mode: <br>
```docker-compose up -d``` <br>

6. To view the app, go to http://localhost:3000/. <br>

7. To shut down the containers, run the command: <br>
```docker-compose down``` <br>

# How to Run Tests the Machine Learning Client

1. Navigate into the machine-learning-client directory by using the command: <br>
```cd machine-learning-client``` <br>

2. Set up a virtual environment, by using the commands:
```pip3 install pipenv OR pip install pipenv``` <br>

3. Activate the virtual environment: <br>
```pipenv shell``` <br>

4. To run tests, use the command:
```python3 -m pytest```

# How to Run Tests the Web Application
1. Navigate into web-app directory by using the command: <br>
```cd web-app``` <br>

2. Set up a virtual environment, by using the commands:
```pip3 install pipenv OR pip install pipenv``` <br>

3. Activate the virtual environment: <br>
```pipenv shell``` <br>

4. To run tests, use the command:
```python3 -m pytest```

# How to Contribute to the Project
We welcome contributions! Here’s how you can help:
1. **Fork the Repository**: Start by forking the repository and cloning your fork to your local machine.
2. **Create and Set up Virtual Environment**: Set up a virtual environment with pipenv, using: <br>
```pip install pipenv OR pip3 install pipenv``` <br>
and then: <br>
```pipenv shell``` <br>
3. **Install Dependencies**: Make sure you have the necessary dependencies installed if pipenv was not used: <br>
```pip install -r requirements.txt OR pip3 install -r requirements.txt``` <br>
4. **Create a New Branch**: Create a branch for your feature or bug fix.
5. **Make Changes and Write Tests**: Make your changes, ensuring that you add or update tests as needed in the tests directory. To run tests, use the command: <br>
```python -m pytest OR python3 -m pytest``` <br>
6. **Commit and Push Your Changes**: After finishing your work on local machine, commit and push your changes to git.
7. **Create a Pull Request**: Go to the original repository and create a pull request for your changes.

Please ensure your codes come with meaningful commit messages and follow the PEP 8 standard, which can be found in detail [here](https://peps.python.org/pep-0008/).