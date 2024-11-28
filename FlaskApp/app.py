from flask import Flask, render_template, request, send_from_directory
import os
import xxhash

app = Flask(__name__)

upload_folder = './uploads'
app.config['UPLOAD_FOLDER'] = upload_folder

if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No files in request'
    file = request.files['file']
    if file.filename == '':
        return 'No file selected'
    if file:
        extension = file.filename.split('.')[-1]
        file_hash = xxhash.xxh3_64(file.read()).hexdigest()
        # Reset file pointer to beginning of file
        file.seek(0)
        new_filename = f'{file_hash}.{extension}'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(filepath)
        return f'File successfully uploaded to {filepath}'


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


app.run()
