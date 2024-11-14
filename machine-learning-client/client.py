"""
Flask application for predicting Rock-Paper-Scissors gestures using a TensorFlow model.
"""

from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import cv2
import numpy as np

app = Flask(__name__)

MODEL_PATH = 'model/rock_paper_scissors_model.h5'
model = load_model(MODEL_PATH)
CLASS_LABELS = ['Rock', 'Paper', 'Scissors']

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict the gesture in the uploaded image using the trained model.

    Returns:
        JSON response with the predicted gesture or error message.
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        if not hasattr(cv2, "imdecode") or not hasattr(cv2, "IMREAD_COLOR"):
            return jsonify({'error': 'cv2 module is missing required attributes.'}), 500

        image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
        processed_image = cv2.resize(image, (224, 224)) / 255.0
        processed_image = np.expand_dims(processed_image, axis=0)

        predictions = model.predict(processed_image)
        gesture = CLASS_LABELS[np.argmax(predictions)]

        return jsonify({'gesture': gesture})
    except KeyError as error:
        return jsonify({'error': f'Key error: {str(error)}'}), 400
    except ValueError as error:
        return jsonify({'error': f'Value error: {str(error)}'}), 400
    except RuntimeError as error:
        return jsonify({'error': f'Runtime error: {str(error)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    