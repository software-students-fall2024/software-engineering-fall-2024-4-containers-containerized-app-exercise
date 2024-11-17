from flask import Flask, request, jsonify
from flask_cors import CORS
from db_handler import DatabaseHandler

app = Flask(__name__)
CORS(app)
db_handler = DatabaseHandler()

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