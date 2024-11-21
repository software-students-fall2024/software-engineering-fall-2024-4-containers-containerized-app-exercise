"""
Flask app for Hello Kitty AI application.
Handles user authentication, connection to MongoDB, and basic routes.
"""

from pydub import AudioSegment
from pydub.utils import which
import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from characterai import pycai, sendCode, authUser
import pymongo
from bson import ObjectId
import certifi
import requests

AudioSegment.converter = "/usr/local/bin/ffmpeg"
AudioSegment.ffprobe = "/usr/local/bin/ffprobe"

def create_app():
    """Creates and configures the Flask application."""
    load_dotenv()
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # Load environment variables
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise ValueError("SECRET_KEY is missing. Add it to your .env file.")
    ml_client_url = os.getenv("ML_CLIENT_URL")
    if not ml_client_url:
        raise ValueError("ML_CLIENT_URL is missing in the .env file")

    # MongoDB setup
    mongo_cli = pymongo.MongoClient(mongo_uri, tlsCAFile=certifi.where())
    try:
        mongo_cli.admin.command("ping")
        logging.info("Successfully connected to MongoDB!")
    except pymongo.errors.PyMongoError as error:
        logging.error(f"Failed to connect to MongoDB: {error}")
        raise

    db = mongo_cli["hellokittyai_db"]
    users = db["users"]

    # Flask setup
    app = Flask(__name__)
    app.secret_key = secret_key
    app.config["UPLOAD_FOLDER"] = "uploads"
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Session security settings
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = True

    # Logging setup
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


    # Routes
    @app.route("/", methods=["GET", "POST"])
    def login():
        """
        Handles user login and code sending.
        Creates a new user if they don't exist.
        """
        if request.method == "POST":
            email = request.form.get("email")
            if not email:
                return "Email address is required", 400

            session["email"] = email
            user = users.find_one({"email": email})
            if not user:
                user_id = str(ObjectId())
                users.insert_one(
                    {"user_id": user_id, "email": email, "chat_history": [], "audio_analysis": []}
                )
                logging.info(f"New user created: {email}")

            session["code"] = sendCode(email)
            return render_template("auth.html", address=email)

        return render_template("index.html")

    @app.route("/authenticate", methods=["POST"])
    def auth():
        """
        Authenticates the user using the link provided and saves the client instance.
        """
        link = request.form.get("link")
        if not link:
            return "Authentication link is required", 400

        email = session.get("email")
        code = session.get("code")
        if not email or not code:
            return "Session expired. Please log in again.", 403

        try:
            logging.info(f"Authenticating user {email}")
            token = authUser(link, email)
            session["token"] = token
            return redirect(url_for("chat_with_character"))
        except Exception as e:
            logging.error(f"Authentication failed for {email}: {e}")
            return jsonify({"error": "Authentication failed"}), 500

    @app.route("/chat", methods=["GET", "POST"])
    def chat_with_character():
        """Handles chatting with a specific character."""
        character_id = "7xhfgdiu2oj2NIRnQQRx42Q2cwr0sFIRu7xZeRZYWn0"

        if request.method == "GET":
            return render_template("chat.html")

        token = session.get("token")
        email = session.get("email")
        if not token or not email:
            return jsonify({"error": "Client is not authenticated. Please log in."}), 403

        try:
            client = pycai.Client(token)
            me = client.get_me()

            with client.connect() as chat:
                new, _ = chat.new_chat(character_id, me.id)
                user_message = request.json.get("message")
                if not user_message:
                    return jsonify({"error": "No message provided"}), 400

                response = chat.send_message(character_id, new.chat_id, user_message)

                # Store the conversation in MongoDB
                users.update_one(
                    {"email": email},
                    {
                        "$push": {
                            "chat_history": {
                                "timestamp": datetime.utcnow(),
                                "message": user_message,
                                "response": response.text,
                            }
                        }
                    },
                )
                logging.info(f"Chat saved for {email}: {user_message} -> {response.text}")
                return jsonify(
                    {"character_name": response.name, "character_message": response.text}
                )
        except Exception as e:
            logging.error(f"Error during chat for {email}: {e}")
            return jsonify({"error": "Chat failed"}), 500

    @app.route("/convert-to-wav", methods=["POST"])
    def convert_to_wav():
        if "audio" not in request.files:
            return jsonify({"error": "No audio file uploaded"}), 400

        audio_file = request.files["audio"]
        original_filename = secure_filename(audio_file.filename)
        original_file_path = os.path.join(app.config["UPLOAD_FOLDER"], original_filename)

        # Save the uploaded audio file
        try:
            audio_file.save(original_file_path)
        except Exception as e:
            logging.error(f"Failed to save audio file: {e}")
            return jsonify({"error": f"Failed to save audio file: {e}"}), 500

        try:
            # Convert the uploaded audio to WAV format
            audio = AudioSegment.from_file(original_file_path)
            wav_file_path = os.path.splitext(original_file_path)[0] + ".wav"

            # Pass explicit parameters to ffmpeg
            audio.export(
                wav_file_path,
                format="wav",
                parameters=["-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1"]
            )

            logging.info(f"File successfully converted to WAV: {wav_file_path}")

            return jsonify({
                "message": "File successfully converted to WAV",
                "wav_file_path": wav_file_path
            }), 200
        except Exception as e:
            logging.error(f"Failed to process audio: {e}")
            return jsonify({"error": f"Failed to process audio: {e}"}), 500
        
    @app.route("/process-audio", methods=["POST"])
    def process_audio():
        """Process an audio file and save its transcript."""
        file = request.files.get("audio")
        if not file:
            return jsonify({"error": "No audio file provided"}), 400

        # Ensure the file is a .wav file
        if not file.filename.endswith(".wav"):
            return jsonify({"error": "Only .wav files are supported"}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            converted_filepath = convert_to_linear16(filepath)
            transcript = transcribe_audio(converted_filepath)

            if transcript:
                document_id = save_transcript_to_db(transcript)
                return jsonify({"transcript": transcript, "id": document_id})
            return jsonify({"error": "No speech recognized"}), 400
        except RuntimeError as error:
            print(f"Error during processing: {error}")
            return jsonify({"error": str(error)}), 500
        #finally:
            # Clean up the original file
            #if os.path.exists(original_file_path):
               # os.remove(original_file_path)
                    
    return app  # Ensure the app instance is returned

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000)