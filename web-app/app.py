from flask import Flask, render_template, request
import requests
import random
from requests.exceptions import RequestException
import os
import time

def retry_request(url, files, retries=5, delay=2):
    for attempt in range(retries):
        try:
            response = requests.post(url, files=files)
            response.raise_for_status()
            return response
        except RequestException as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e

app = Flask(__name__)

@app.route('/')
def home():
    
    return render_template('title.html')

@app.route('/index')
def index():
    
    return render_template('index.html')

@app.route('/statistics')
def statistics():
    
    return render_template('statistics.html')

@app.route('/result', methods=['POST'])
def result():
    try:
        file = request.files['image']

        
        ML_CLIENT_URL = os.getenv("ML_CLIENT_URL", "http://machine-learning-client:5000")
        response = requests.post(f"{ML_CLIENT_URL}/predict", files={'image': file})
        user_gesture = response.json().get('gesture', 'Unknown')
    except Exception as e:
        return f"Error communicating with ML client: {str(e)}"

    
    ai_gesture = random.choice(['Rock', 'Paper', 'Scissors'])

    
    result = determine_winner(user_gesture, ai_gesture)
    return render_template('result.html', user=user_gesture, ai=ai_gesture, result=result)

def determine_winner(user, ai):
    if user == ai:
        return "It's a tie!"
    elif (user == 'Rock' and ai == 'Scissors') or \
         (user == 'Paper' and ai == 'Rock') or \
         (user == 'Scissors' and ai == 'Paper'):
        return "You win!"
    else:
        return "AI wins!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    