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

### **2. Clone the Repository**
    ```shell
    git clone https://github.com/software-students-fall2024/4-containers-its-over-again.git
    cd 4-containers-its-over-again
    ```
### **3. Environment Setup**
Create a .env file in the root directory with the following content:
    ```shell
    MONGO_DBNAME=itsOver
    MONGO_URI=mongodb+srv://itsOver:itsOver@itsover.bx305.mongodb.net/?retryWrites=true&w=majority
    FLASK_RUN_PORT=5000
    ```
This .env file will configure the connection to your MongoDB instance.
### **4. Run Using Docker**

1. **Build the Docker Image**
   
   Navigate to the directory containing your `Dockerfile` (e.g., `machine-learning-client` or `web-app`) and run the following command to build the Docker image:

   ```bash
   docker build -t flask-app .

2. **Run the Docker Container**
    ```bash
    docker run -p 5001:5000 --env-file .env flask-app

3. **Access the Application**
    After successfully running the Docker container, you can access the application using the following URLs:

    - **Home Page**: [http://localhost:5001/](http://localhost:5001/)
    - **API Endpoint**: [http://localhost:5001/api/data](http://localhost:5001/api/data)

### **5. Local Development Without Docker**

### **6. MongoDB Setup**


## **Task Boards**
- **Task Boards** [Task Boards](https://github.com/orgs/software-students-fall2024/projects/137)