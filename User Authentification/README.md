# Login & Signup Application

This is a simple web application that allows users to sign up and log in. The frontend is built using HTML, CSS, and JavaScript, while the backend is powered by Node.js with MongoDB for data storage. The application includes user authentication with password hashing and JSON Web Token (JWT) for secure login.

## Features:
- User Sign Up
- User Login
- Password hashing with bcrypt
- JWT-based Authentication
- Success/Error messages displayed in a user-friendly way
- Form switching between login and signup

---

## Table of Contents
- [Installation](#installation)
- [Prerequisites](#prerequisites)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Running the Application](#running-the-application)
- [Message System](#message-system)
- [File Structure](#file-structure)
- [License](#license)

---

## Installation

### 1. Clone the Repository
Clone the repository to your local machine using Git:

bash
git clone https://github.com/yourusername/login-signup-app.git
cd login-signup-app


### 2. Install Backend Dependencies
First, navigate to the backend directory and install the required dependencies using npm.

```bash
cd backend
npm install
```

### 3. Install Frontend Dependencies
The frontend doesn't require any third-party libraries, as it is plain HTML, CSS, and JavaScript. However, if you plan to use build tools like Webpack or Gulp for the frontend, you can initialize your package and install dependencies:

```bash
cd frontend
```

---

## Prerequisites

Before running the application, ensure you have the following installed on your machine:

1. *Node.js*: To run the backend server and JavaScript code.
   - Download and install it from [Node.js Official Website](https://nodejs.org/).

2. *MongoDB*: The backend uses MongoDB for data storage.
   - You can either run MongoDB locally or use a cloud-based solution like [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
   - Follow the [MongoDB installation guide](https://www.mongodb.com/docs/manual/installation/) if you prefer local installation.

---

## Backend Setup

### 1. Run the Backend Server
Start the backend server by running:

bash
cd backend
npm start


This will start a local Node.js server at http://localhost:3000, which handles user authentication and stores data in the MongoDB database.

---

## Frontend Setup

### 1. HTML, CSS, and JavaScript
The frontend consists of a simple index.html file where users can sign up and log in. The associated styles.css provides basic styling, and script.js handles the logic for showing success/error messages and form switching.

- *index.html*: The main HTML file containing the forms for login and signup.
- *styles.css*: The CSS file for styling the forms and message container.
- *script.js*: The JavaScript file that handles form submissions, message display, and form transitions.

Make sure your frontend is connected to the correct backend URL (http://localhost:3000) for the API requests.

---

## Running the Application

1. *Start the Backend Server*:
   - Run npm start inside the backend directory to start the server.

2. *Open the Frontend in Your Browser*:
   - Open the index.html file in your browser to see the login and signup forms.

The application allows users to:
- *Sign Up*: Enter a name, email, and password to create an account.
- *Log In*: Enter an email and password to authenticate and receive a JWT token.

---

## Message System

The application displays success and error messages in a message container rather than using alert(). These messages are styled to provide clear feedback to the user about the success or failure of an action.

- *Success Messages*: Green background with white text (.success class).
- *Error Messages*: Red background with white text (.error class).
- Messages are automatically hidden after 4 seconds, or the user can close them manually.

### Example Messages:
- *Success*: "Account created successfully!"
- *Error*: "Invalid credentials!"

---

## File Structure

Here is the structure of the project:

```bash
login-signup-app/
│
├── backend/
│   ├── models/
│   │   ├── User.js              # Mongoose model for User
│   ├── routes/
│   │   ├── auth.js              # Authentication routes (Login, Signup)
│   ├── server.js                   # Main Node.js application logic
│   └── package.json             # Backend dependencies and scripts
│
├── frontend/
│   ├── index.html               # Main HTML file for login/signup
│   ├── styles.css               # CSS file for styling
│   ├── script.js                   # JavaScript for form handling and messages
│                                # Frontend dependencies (if applicable)
│
└── README.md                    # This README file

```
---
