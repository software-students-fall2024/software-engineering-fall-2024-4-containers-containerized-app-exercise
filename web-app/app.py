from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Set up MongoDB connection (update with your MongoDB details)
client = MongoClient("mongodb://localhost:27017/")
db = client['traffic_db']
traffic_data_collection = db['traffic_data']

@app.route('/')
def dashboard():
    # Fetch initial data (this will be replaced with live data in a real app)
    vehicle_counts = {'cars': 12, 'trucks': 3, 'buses': 1}
    congestion_level = "Moderate"
    return render_template('dashboard.html', vehicle_counts=vehicle_counts, congestion_level=congestion_level)

@app.route('/historical', methods=['POST'])
def get_historical_data():
    # Extract date range from the request
    start_date = request.form.get("startDate")
    end_date = request.form.get("endDate")
    
    # Convert dates to datetime objects for querying
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # Query MongoDB for data within date range
    historical_data = list(traffic_data_collection.find({
        "timestamp": {"$gte": start, "$lte": end}
    }))

    # Format data for Chart.js
    data = {
        "dates": [entry["timestamp"].strftime("%Y-%m-%d %H:%M") for entry in historical_data],
        "vehicle_counts": [entry["vehicle_count"] for entry in historical_data]
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
