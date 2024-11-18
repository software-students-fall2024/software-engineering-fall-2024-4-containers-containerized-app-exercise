![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
![Machine Learning Client CI](https://github.com/software-students-fall2024/4-containers-four/actions/workflows/machine-learning-client.yml/badge.svg)
![Web App CI](https://github.com/software-students-fall2024/4-containers-four/actions/workflows/web-app.yml/badge.svg)

# Containerized App Exercise

Build a containerized app that uses machine learning. See [instructions](./instructions.md) for details.

## Description

The ASL interpreter app uses machine learning to recognize American Sign Language gestures from images.

Designed for accessibility and ease of use, it offers a seamless, containerized experience that runs across three subsystems: gesture recognition, a web interface, and a database.

## Team

[Safia Billah](https://github.com/safiabillah)

[Melanie Zhang](https://github.com/melanie-y-zhang)

[Chloe Han](https://github.com/jh7316)

[Fatima Villena](https://github.com/favils)

## Instructions to Run

### Virtual Environment Configuration

Make sure you have pipenv installed.

```bash
pip install pipenv
```

Then install dependencies.

```bash
pipenv install
```

And now you can run python scripts through the shell.

```bash
pipenv shell
```

### Setup

Build the app using docker compose.

```bash
docker-compose up --build
```

## Task Board

[Task Board](https://github.com/orgs/software-students-fall2024/projects/119/views/1)
