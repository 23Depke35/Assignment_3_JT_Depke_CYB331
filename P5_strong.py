import os
import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = '/srv/uploads'
MAX_FILE_SIZE_MB = 10  # Set maximum content length limit (e.g., 10MB)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024

# Ensure the upload directory exists with appropriate permissions
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# CWE-434 Defense: Whitelist of allowed extensions to prevent malicious executable uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt', 'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    # Verify file part exists in request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    # Reject empty filename requests
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    # Check if the uploaded file is empty by inspecting stream length
    file.stream.seek(0, os.SEEK_END)
    file_length = file.stream.tell()
    file.stream.seek(0)  # Reset stream pointer back to beginning
    
    if file_length == 0:
        return jsonify({"error": "Uploaded file is empty"}), 400

    # CWE-434 Defense: Validate file type via allowed extension whitelist
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    # CWE-22 Defense & Filename Ignored:
    # Completely ignore the user-supplied filename. Generate a cryptographically 
    # secure random UUID filename while retaining the validated extension.
    ext = file.filename.rsplit('.', 1)[1].lower()
    safe_filename = f"{uuid.uuid4()}.{ext}"
    
    # Construct the absolute path and ensure it strictly resides within UPLOAD_FOLDER
    abs_upload_folder = os.path.abspath(UPLOAD_FOLDER)
    destination_path = os.path.abspath(os.path.join(abs_upload_folder, safe_filename))
    
    if not destination_path.startswith(abs_upload_folder + os.sep):
        return jsonify({"error": "Invalid file path detected"}), 400

    try:
        file.save(destination_path)
    except Exception as e:
        return jsonify({"error": "Failed to save file securely"}), 500

    return jsonify({
        "message": "File successfully uploaded",
        "saved_filename": safe_filename
    }), 201

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File exceeds the maximum allowed size limit"}), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)