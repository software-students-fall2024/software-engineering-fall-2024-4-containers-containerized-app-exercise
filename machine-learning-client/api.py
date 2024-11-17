from flask import Flask, request, jsonify
from flask_cors import CORS
from db_handler import DatabaseHandler
from emotion_detector import EmotionDetector
import cv2
import numpy as np
import uuid

app = Flask(__name__)
CORS(app)
db_handler = DatabaseHandler()
detector = EmotionDetector()

@app.route('/')
def index():
    return jsonify({
        'status': 'running',
        'service': 'Emotion Detection ML Client',
        'endpoints': {
            '/detect': 'POST - Detect emotions in uploaded image'
        }
    })

@app.route('/detect', methods=['POST'])
def detect_emotion():
    """
    Process uploaded image and detect emotions
    Expects image data in request.files['image']
    """
    try:
        if 'image' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No image file provided'
            }), 400

        image_file = request.files['image']
        if not image_file:
            return jsonify({
                'status': 'error',
                'message': 'Empty file'
            }), 400

        # Read image data
        image_data = image_file.read()
        
        # Convert bytes to numpy array for OpenCV
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({
                'status': 'error',
                'message': 'Invalid image format'
            }), 400

        # Get user_id from request if available
        user_id = request.form.get('user_id')
        
        # Generate unique ID
        image_id = str(uuid.uuid4())
        
        # Detect emotions
        result = detector.detect_emotion(img)
        
        if "status" in result and result["status"] == "success":
            # Save results to database with user_id if provided
            db_handler.save_detection_result(image_id, result["emotions"], user_id)
            
            return jsonify({
                'status': 'success',
                'image_id': image_id,
                'emotions': result["emotions"]
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result.get("error", "Unknown error occurred")
            }), 500

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/get-detection/<image_id>', methods=['GET'])
def get_detection(image_id):
    try:
        result = db_handler.get_detection_result(image_id)
        
        if result is None:
            return jsonify({
                'status': 'error',
                'message': 'Image ID not found'
            }), 404
            
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)