""" Flask server for machine-learning component - Project 4 """

import logging
from flask import Flask, jsonify, request
import numpy as np
from run_model import mnist_classify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def predict():
    """ process data passed from web-app and call the function to run through model """

    data = request.json
    image_array = np.array(data['image'], dtype=np.float32).reshape(28, 28)

    response = mnist_classify(image_array)
    return jsonify({'classification': int(response)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
