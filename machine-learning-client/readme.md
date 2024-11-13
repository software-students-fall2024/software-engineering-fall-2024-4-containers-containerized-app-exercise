### Setup Steps
- Ensure docker desktop installed, check with ```docker --version```
- Run the following commands to build and run a container for the ml-client
```
cd machine-learning-client
docker build -t ml-client .
docker run ml-client
```