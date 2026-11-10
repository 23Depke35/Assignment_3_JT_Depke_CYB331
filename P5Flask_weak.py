import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "txt"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# Set maximum allowed payload size (e.g., 16 MB)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Ensure directory exists
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        destination = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(destination)

        return (
            jsonify(
                {"message": "File uploaded successfully", "path": destination}
            ),
            200,
        )

    return jsonify({"error": "File type not allowed"}), 400