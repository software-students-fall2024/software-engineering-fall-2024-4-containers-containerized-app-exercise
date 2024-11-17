![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

# Containerized App Exercise

# Table of Contents

1. [Teammates](#teammates)  
2. [App Description: Emotion Recognition and Wellness Advisor](#app-description-emotion-recognition-and-wellness-advisor)  
   - [How It Works](#how-it-works)  
3. [How to Open](#how-to-open)  
   - [Ensure Connection to Mongo](#1-ensure-connection-to-mongo)  
   - [Create a New Virtual Environment](#2-create-a-new-virtual-environment)  
   - [Install Dependencies](#3-install-dependencies-if-not-already-installed)  
   - [Docker Compose](#4-docker-compose)  
   - [Open the Local Host Link](#5-open-the-local-host-link-for-web-app-and-enjoy)
   

# Teammates 

[Dasha Miroshnichenko](https://github.com/dm5198)

[Emily Huang](https://github.com/emilyjhuang)

[Jessie Kim](https://github.com/jessiekim0)

[Nick Burwell](https://github.com/nickburwell)

# App Description: Emotion Recognition and Wellness Advisor

Our Emotion Recognition and Wellness Advisor app uses cutting-edge emotion detection technology to help users enhance their mental well-being. By analyzing facial expressions in real-time, the app identifies emotions such as happiness, sadness, anger, and more. Based on the detected emotion, the app provides tailored wellness advice, like mindfulness exercises, motivational quotes, or self-care suggestions.

**How It Works:**

- **Emotion Detection:** Using a machine learning model, the app captures real-time images or videos and identifies the user’s current emotional state.
- **Personalized Advice:** Based on the recognized emotion, the app recommends activities or tips to help maintain or improve the user's mood. For example, if sadness is detected, the app might suggest calming meditation exercises or uplifting music.
- **Dashboard Display:** The web app presents a user-friendly dashboard where users can see their current and past emotions along with personalized advice.

The app aims to promote emotional awareness and provide quick, personalized guidance for mental well-being. Whether you’re looking to uplift your mood or enhance your mindfulness practice, this app supports you on your wellness journey.

## How to Open **

**1. Ensure Connection to Mongo**

Download the MongoDB for VSC extension and add the database url: mongodb+srv://nsb8225:thefixers2.1@cluster0.oqt4t.mongodb.net/ when prompted to connect to the database.


**2. Create a new virtual environment following the commands:**

```
python3 -m venv .venv

```

**Mac** 
```
source .venv/bin/activate`
```

**Windows**
```
.venv\Scripts\activate
```

**3. Install Dependencies if not already installed**

```
pip install opencv-python-headless
pip install requests
pip install pymongo
```

**4. Docker Compose**

To compose docker run the follwoig command

```
docker-compose up --build

```

**5. Open the local host link for web-app and enjoy!**

Thank you for the [Emotion Detection Model](https://www.kaggle.com/datasets/abhisheksingh016/machine-model-for-emotion-detection)!