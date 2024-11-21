![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

# Containerized App Exercise

Build a containerized app that uses machine learning. See [instructions](./instructions.md) for details.

## **Team Members**

- **Boming Zhang** (bz2196) [GitHub Profile](https://github.com/BomingZhang-coder)
- **Annabeth Gao** (mg6839) [GitHub Profile](https://github.com/bellinimoon)
- **Jack Zhang** (yz6973) [GitHub Profile](https://github.com/yz6973)

## Product Description
The **Online Focus Detection System** is a containerized application designed to monitor and analyze user focus during online courses. It consists of three interconnected subsystems:
- **Machine Learning Client**: Collects and analyzes data from sensors such as cameras and mouse movements to measure user engagement.
  - **Camera Data**: Determines whether the user is looking at their screen.
  - **Mouse Data**: Tracks mouse movements, clicks, and scrolls to gauge activity levels.
- **Web App**: Provides an interface to visualize collected data and display analytical results.
- **Database (MongoDB)**: Stores sensor data and analytical metadata for seamless integration.

## **System Setup and Configuration**

### **1. Prerequisites**
- **Docker** installed on your machine.
- **Python 3.10+** (if running without Docker).
- A MongoDB connection string for the database.


## **Task Boards**
- **Task Boards** [Task Boards](https://github.com/orgs/software-students-fall2024/projects/137)