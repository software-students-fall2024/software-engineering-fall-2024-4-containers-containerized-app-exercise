from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, make_response
import os
import pymongo
from werkzeug.utils import secure_filename

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

    connection = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = connection[os.getenv("MONGO_DBNAME")]

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        if request.method == 'POST':
            file = request.files.get('plant_image')
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join('uploads', filename) 
                file.save(filepath)

                db.identifications.insert_one({
                    "filename": filename,
                    "filepath": filepath
                })
                
                return redirect(url_for('results', filename=filename))
            else:
                return make_response("No file uploaded", 400)

        return render_template('upload.html')

    @app.route('/results/<filename>')
    def results(filename):
        result = db.identifications.find_one({"filename": filename})
        if result:
            return render_template('results.html', result=result)
        else:
            return make_response("Result not found", 404)

    @app.route('/history')
    def history():
        all_results = list(db.identifications.find())
        return render_template('history.html', all_results=all_results)

    return app

if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    app = create_app()
    app.run(port=FLASK_PORT)
