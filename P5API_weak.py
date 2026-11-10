import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()
UPLOAD_DIR = Path("uploads")


@app.post("/upload/")
async def save_upload_file(file: UploadFile = File(...)):
    # Ensure directory exists
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Sanitize filename (Path.name strips paths)
    safe_filename = Path(file.filename).name
    file_path = UPLOAD_DIR / safe_filename

    try:
        # Stream file to disk in chunks
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        await file.close()

    return {"filename": safe_filename, "path": str(file_path.resolve())}