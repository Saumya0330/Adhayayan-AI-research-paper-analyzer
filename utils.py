# utils.py - Utility functions for file handling
import os
import shutil

UPLOAD_DIR = "./data/uploads"

def save_uploaded_file(upload_file) -> str:
    """
    Save uploaded file from FastAPI UploadFile object.
    
    Args:
        upload_file: FastAPI UploadFile object
    
    Returns:
        str: Path to saved file
    """
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename to avoid conflicts
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    base_name = os.path.splitext(upload_file.filename)[0]
    ext = os.path.splitext(upload_file.filename)[1]
    
    filename = f"{base_name}_{unique_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    print(f"✅ Saved file: {filename}")
    return file_path

def cleanup_old_files(days: int = 7):
    """
    Clean up files older than specified days.
    """
    import time
    
    if not os.path.exists(UPLOAD_DIR):
        return
    
    now = time.time()
    cutoff = now - (days * 86400)  # days in seconds
    
    for filename in os.listdir(UPLOAD_DIR):
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(filepath):
            file_time = os.path.getmtime(filepath)
            if file_time < cutoff:
                try:
                    os.remove(filepath)
                    print(f"🗑️ Removed old file: {filename}")
                except Exception as e:
                    print(f"❌ Error removing {filename}: {e}")