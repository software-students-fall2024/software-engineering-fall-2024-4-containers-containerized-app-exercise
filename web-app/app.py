from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/checkSentiment', methods=['POST'])
def check_sentiment():
    data = request.get_json()
    sentence = data.get('sentence')
    
    sentiment = sentence
    return jsonify({'sentiment': sentiment})

if __name__ == '__main__':
    app.run(debug=True)
