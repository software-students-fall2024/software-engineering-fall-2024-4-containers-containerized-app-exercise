from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Set up MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client['traffic_db']
traffic_data_collection = db['traffic_data']

@app.route('/')
def dashboard():
    # Example data for vehicle counts and congestion level
    vehicle_counts = {'cars': 12, 'trucks': 3, 'buses': 1}
    congestion_level = "Moderate"

    # Determine color based on congestion level
    color = "orange" if congestion_level == "Moderate" else "green" if congestion_level == "Low" else "red"
    
    return render_template('dashboard.html', vehicle_counts=vehicle_counts, congestion_level=congestion_level, color=color)

if __name__ == '__main__':
    app.run(debug=True)


