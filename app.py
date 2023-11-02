from flask import Flask, render_template, request, redirect, send_file, jsonify
from werkzeug.utils import secure_filename
import os, subprocess, threading, time, shutil
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)


def clean_output(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

current_process = None
process_thread = None
filename = ""

def run_detection(video_path):
    global current_process
    current_process = subprocess.Popen(['python3', 'detect.py', '--source', video_path, '--exist-ok'])
    current_process.wait()

@app.route("/")
def hello_world():
    clean_output(app.config['OUTPUT_FOLDER'])
    return render_template('index.html')

@app.route("/detect", methods=['POST'])
def detect():
    global current_process, process_thread, filename
    if 'video' not in request.files:
        return "No video file provided" 

    video = request.files['video']

    if video is not None:
        if video.filename == '':
            return "No selected video file"
        filename = video.filename
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(video.filename))
        video.save(video_path)

        process_thread = threading.Thread(target=run_detection, args=(video_path,))
        process_thread.start()
        return redirect('/loader')
    else:
        return "No video file provided"

@app.route("/loader", methods=['GET'])
def loader():
    return render_template('loader.html')

@app.route("/download", methods=['GET'])
def download():
    current_process.terminate()
    time.sleep(3)
    return redirect('/return-files')

@app.route('/return-files')
def return_file():
    global filename
    obj_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    try:
        return send_file(obj_path, as_attachment=True)
    except Exception as e:
        print(e)
        return redirect('/loader')
    

if __name__ == '__main__':
    app.run(debug=True)
