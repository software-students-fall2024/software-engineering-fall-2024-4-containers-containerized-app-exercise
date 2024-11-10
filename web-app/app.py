from flask import Flask, render_template, jsonify, request
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
    
    response = requests.post(
        'http://localhost:8000/predict',
        json=data
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Classification failed"}, 500
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)