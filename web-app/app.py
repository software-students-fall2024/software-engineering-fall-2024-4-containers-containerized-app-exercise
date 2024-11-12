from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import uuid
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download the VADER lexicon for sentiment analysis
nltk.download('vader_lexicon')

app = Flask(__name__)

# Connect to MongoDB (make sure MongoDB is running)
client = MongoClient('mongodb://localhost:27017/')  # Adjust the connection string if necessary
db = client['sentiment_db']  # Database name
collection = db['sentiments']  # Collection name

# Initialize the sentiment analyzer
sia = SentimentIntensityAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/checkSentiment', methods=['POST'])
def check_sentiment():
    data = request.get_json()
    sentence = data.get('sentence')

    # Generate a unique request_id
    request_id = str(uuid.uuid4())

    # Perform sentiment analysis
    analysis = sia.polarity_scores(sentence)

    # Create the data structure
    document = {
        "request_id": request_id,
        "sentences": [
            {
                "sentence": sentence,
                "status": "analyzed",
                "analysis": analysis
            }
        ],
        "overall_status": "analyzed",
        
    }

    # Insert into MongoDB
    collection.insert_one(document)

    # Return the analysis to the client
    return jsonify({'analysis': analysis})

if __name__ == '__main__':
    app.run(debug=True)
