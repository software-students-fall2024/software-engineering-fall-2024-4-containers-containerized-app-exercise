![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
[![log github events](https://github.com/software-students-fall2024/4-containers-its-over-again/actions/workflows/event-logger.yml/badge.svg)](https://github.com/software-students-fall2024/4-containers-its-over-again/actions/workflows/event-logger.yml)

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

```bash
    git clone https://github.com/software-students-fall2024/4-containers-its-over-again.git
    cd 4-containers-its-over-again
```
### **3. Environment Setup**

Create a `.env` file in the root directory with the following content:

```env
    MONGO_DBNAME=itsOver
    MONGO_URI=mongodb+srv://itsOver:itsOver@itsover.bx305.mongodb.net/?retryWrites=true&w=majority&appName=itsOver
    FLASK_APP=app.py
    FLASK_ENV=development
    FLASK_PORT=5000
    SECRET_KEY=itsOver
    PYTHONPATH=$(pwd) pytest web-app/tests
```
    This .env file will configure the connection to your MongoDB instance.
### **4. Run Using Docker**

1. **Build the Docker Image**
   
   Navigate to the root directory and run the following command to build the Docker image and run:

   ```bash 
    docker-compose up --build
   ```
2. **Access the Application**
    After successfully running the Docker container, you can access the application using the following URLs:

    - **Home Page**: [http://localhost:5001/](http://localhost:5001/)
    - **API Endpoint**: [http://localhost:5001/api/data](http://localhost:5001/api/data)

3. **Play with the Web**
    After accessing the Home Page, you can sign up and login to use the mouse tracking functionality. You can also view your past tracking records. Our camera tracker is temporily disabled.

### **5. Local Development Without Docker**
#### **Setup Instructions**
1. Clone the repository:
   ```bash
   git clone https://github.com/software-students-fall2024/4-containers-its-over-again.git
   cd ../machine-learning-client
   ```

2. Create and activate a virtual environment:
   ```bash
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```

3. Install relevant dependencies

4. Set up the .env file:
    Create a .env file in the project root and add the following:
    ```dotenv
    MONGO_DBNAME=itsOver
    MONGO_URI=mongodb+srv://itsOver:itsOver@itsover.bx305.mongodb.net/?retryWrites=true&w=majority
    FLASK_RUN_PORT=5000
    ```

5. Run the Camera Tracker:
   ```bash
    python camera_tracker.py
    ```

6. Test the camera tracker:
Ensure your camera is operational.
Monitor the console logs to confirm face detection and MongoDB updates.

### **6. MongoDB Setup**
To connect your application to MongoDB, follow these steps:

#### **Step 1: Install MongoDB**
If MongoDB is not already installed on your machine, you can use Docker to set up the `mongosh` client. Run the following command:

```bash
docker pull mongodb/mongosh
```

Step 2: Connect to MongoDB
Use the provided connection string to connect to your MongoDB instance. The following command connects to the cluster using the mongosh client:

```bash
    docker run -it mongodb/mongosh "mongodb+srv://bellinimoon:itsOver@itsover.bx305.mongodb.net/?retryWrites=true&w=majority&appName=itsOver"
```
This command connects to the database cluster hosted at itsover.bx305.mongodb.net.

Step 3: Verify Connection
Once connected, you should see a MongoDB shell prompt. You can run the following command to verify the databases available:

```javascript
show dbs
````
Ensure the itsOver database (or your desired database) is listed.

Step 4: Update .env File

Make sure your .env file is updated with the correct MongoDB connection string so the application can connect to the database automatically. Add the following line to your .env file:

```plaintext
MONGO_URI=mongodb+srv://bellinimoon:itsOver@itsover.bx305.mongodb.net/?retryWrites=true&w=majority&appName=itsOver
MONGO_DBNAME=itsOver
```
Step 5: Test the Integration

Run the application and check if the MongoDB connection is established. The app will interact with the database using the credentials and connection string provided.

By following these steps, you'll successfully set up MongoDB and integrate it with your application for local or Docker-based development.

## **Task Boards**
- **Task Boards** [Task Boards](https://github.com/orgs/software-students-fall2024/projects/137)