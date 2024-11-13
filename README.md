![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

# Containerized App Exercise

Build a containerized app that uses machine learning. See [instructions](./instructions.md) for details.

## Description

Our project is an audio-based recognition system for activity. It's designed to analyze various sound events, such as clapping, snapping, and hitting a desk and classify them accordingly. The system leverages Docker for scalability, and operates in a containerized environment, as per the instructions.

## Configuration Instructions

TODO

## Environment Vars and Data Import Instructions

TODO

## .env File Creation (If Necessary)

TODO

## Team members

- [Darren Zou](https://github.com/darrenzou)
- [Peter D'Angelo](https://github.com/dangelo729)
- [Gene Park](https://github.com/geneparkmcs)
- [Joseph Chege](https://github.com/JosephChege4)

# Acknowledgements

- The structure of docker-compose.yaml and our Dockerfile are based on the examples we were given in class (https://knowledge.kitchen/content/courses/software-engineering/notes/containers/)
- When writing the tests, these sources were helpful to figure out mocking, Flask config testing, and mostly just how the assertions should look 
    - (https://librosa.org/doc/0.8.1/index.html#id1)
    - (https://discuss.pytorch.org/t/mfcc-extracterted-by-librosa-pytorch/161180)-
    - (https://realpython.com/python-mock-library/)
    - (https://testdriven.io/blog/flask-pytest/)
    - (https://flask.palletsprojects.com/en/stable/config/)