import os
import shutil
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.models.report import FileFormat, FileUploadResponse


async def save_uploaded_file(
    file: UploadFile, 
    file_type: str
) -> FileUploadResponse:
    """
    Save an uploaded file to the upload directory.
    
    Args:
        file: The uploaded file
        file_type: The type of file (input or reference)
    
    Returns:
        FileUploadResponse: Metadata about the uploaded file
    """
    # Validate file type
    if file_type not in ["input", "reference"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Must be 'input' or 'reference'")
    
    # Validate file extension
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ["csv", "xlsx", "json"]:
        raise HTTPException(status_code=400, detail="Invalid file format. Must be CSV, XLSX, or JSON")
    
    # Create a unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{file_type}_{timestamp}.{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    return FileUploadResponse(
        filename=filename,
        file_type=file_type,
        file_size=file_size,
        upload_time=datetime.now(),
        status="success"
    )


def get_file_path(filename: str) -> str:
    """
    Get the full path to a file.
    
    Args:
        filename: The name of the file
    
    Returns:
        str: The full path to the file
    """
    # Determine the directory based on the filename prefix
    if filename.startswith("input_") or filename.startswith("reference_"):
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
    elif filename.startswith("report_"):
        file_path = os.path.join(settings.REPORTS_DIR, filename)
    else:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Check if the file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    
    return file_path


def list_files(file_type: Optional[str] = None) -> List[dict]:
    """
    List all files of a specific type.
    
    Args:
        file_type: The type of file to list (input, reference, or report)
    
    Returns:
        List[dict]: A list of file metadata
    """
    files = []
    
    # Determine the directory to scan
    if file_type in ["input", "reference"]:
        directory = settings.UPLOAD_DIR
        prefix = f"{file_type}_"
    elif file_type == "report":
        directory = settings.REPORTS_DIR
        prefix = "report_"
    else:
        # List all files
        input_files = list_files("input")
        reference_files = list_files("reference")
        report_files = list_files("report")
        return input_files + reference_files + report_files
    
    # Scan the directory
    for filename in os.listdir(directory):
        if filename.startswith(prefix):
            file_path = os.path.join(directory, filename)
            files.append({
                "filename": filename,
                "file_type": file_type,
                "file_size": os.path.getsize(file_path),
                "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                "updated_at": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            })
    
    # Sort by creation time (newest first)
    files.sort(key=lambda f: f["created_at"], reverse=True)
    
    return files
