from flask import Flask, render_template, request, session
app = Flask(__name__)


@app.route('/')
def index():
    if 'files[]' in request.files:
        file = request.files['files[]']
        file.save(file.filename)
        session['audiofile'] = file
        return redirect(url_for('uploaded'))
        # return render_template('uploaded.html')
    return render_template('fileUpload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    return render_template('uploaded.html')
                           
@app.route('/spoken')
def spoken():
    audio_to_text(100)
    return render_template('spoken.html', "The transcript is here.")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)