from flask import Flask, jsonify, request
import numpy as np
from run_model import mnist_classify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/predict', methods=['POST'])  # Added methods=['POST']
def predict():
    try:
        data = request.json
        image_array = np.array(data['image'], dtype=np.float32).reshape(28, 28)

        response = mnist_classify(image_array)
        return jsonify({'classification': int(response)})

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
