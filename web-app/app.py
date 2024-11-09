from flask import Flask, render_template, jsonify, request
import numpy as np
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def main_page():
   return render_template('main.html')


@app.route('/save_results', methods=['POST'])
def save_results_route():
    data = request.json
    intended_num = data['intendedNum']
    classified_num = data['classifiedNum']
    
    logger.info(f"Saving results - Intended: {intended_num}, Classified: {classified_num}")
    
    return '', 204


@app.route('/classify', methods=['POST'])
def classify():
    data = request.json
    
    image_array = np.array(data['image'], dtype=np.float32).reshape(28, 28)
    
    # Save to file with formatting
    with open('user_input.txt', 'w') as f:
        f.write("Image shape: {}\n".format(image_array.shape))
        f.write("Min value: {}\n".format(np.min(image_array)))
        f.write("Max value: {}\n".format(np.max(image_array)))
        f.write("\nImage array (28x28):\n")
        
        # Format each row with consistent spacing
        for row in image_array:
            # Format each number to have 3 decimal places and width of 8 characters
            f.write(" ".join("{:8.3f}".format(x) for x in row))
            f.write("\n")
    
    #expects this format output
    return({'classification': 5})
    
""" 
    SAMPLE API CALL
    response = requests.post(
        'http://localhost:8000/predict',  # Adjust URL/port as needed
        json={"image": data['image']}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Classification failed"}, 500
    
"""