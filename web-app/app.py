"""
This is the Flask web application that serves as the interface for
the machine learning model.
"""

from flask import Flask, render_template, request, jsonify
from pydub import AudioSegment
import io
import requests

def create_app():
    """
    Create and configure the Flask application
    Returns: app: the Falsk application object
    """
    app = Flask(__name__)
    print("hello world!")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/record",methods=["POST"])
    def record():
        audio_data = request.files["audio"]
        if audio_data:
            try:
                audio = AudioSegment.from_file(audio_data)
                audio = audio.set_channels(1).set_sample_width(2).set_frame_rate(16000)
                buffer = io.BytesIO()
                audio.export(buffer, format="wav")
                buffer.seek(0)
                response = requests.post("http://ml-client:5000/transcribe", files={'audio': ('audio.wav', buffer, 'audio/wav')})
                if response.json().get("status")=="success":
                    return jsonify({'status': 'success','text':response.json().get("text")})
            except ValueError:
                return jsonify({'status': 'error','text':"ValueError happens"})
        return jsonify({'status': 'error','text':response.json().get("text")})
    return app


if __name__ == "__main__":
    web_app = create_app()
    web_app.run(host="0.0.0.0")
