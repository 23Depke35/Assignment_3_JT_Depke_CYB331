import os
from pathlib import Path
from werkzeug.utils import secure_filename


def save_uploaded_file(
    file_bytes: bytes, original_filename: str, upload_folder: str = "uploads"
) -> str:
    """Saves raw file bytes to the specified server directory.

    Returns the absolute path to the saved file.
    """
    # Create the directory if it does not exist
    os.makedirs(upload_folder, exist_ok=True)

    # Sanitize the filename to prevent path traversal attacks (e.g., ../../filename)
    safe_name = secure_filename(original_filename)
    if not safe_name:
        raise ValueError("Invalid filename provided.")

    file_path = Path(upload_folder) / safe_name

    # Write binary data to disk
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return str(file_path.resolve())