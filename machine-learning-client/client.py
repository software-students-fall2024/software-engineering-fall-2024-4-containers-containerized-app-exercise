from flask import Flask, request, jsonify
import tensorflow as tf
from tensorflow.keras.models import load_model
import cv2
import numpy as np

app = Flask(__name__)


MODEL_PATH = 'model/rock_paper_scissors_model.h5'
model = load_model(MODEL_PATH)
CLASS_LABELS = ['Rock', 'Paper', 'Scissors']

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        
        file = request.files['image']
        image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

        
        processed_image = cv2.resize(image, (224, 224)) / 255.0
        processed_image = np.expand_dims(processed_image, axis=0)

        
        predictions = model.predict(processed_image)
        gesture = CLASS_LABELS[np.argmax(predictions)]

        
        return jsonify({'gesture': gesture})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)