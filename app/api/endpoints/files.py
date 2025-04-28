import os
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.security import get_current_active_user
from app.models.report import FileUploadResponse
from app.models.user import User
from app.services.file_service import get_file_path, list_files, save_uploaded_file

router = APIRouter()


@router.post("/upload/{file_type}", response_model=FileUploadResponse)
async def upload_file(
    file_type: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
) -> FileUploadResponse:
    """
    Upload a file (input or reference).
    
    Args:
        file_type: The type of file (input or reference)
        file: The file to upload
    
    Returns:
        FileUploadResponse: Metadata about the uploaded file
    """
    return await save_uploaded_file(file, file_type)


@router.get("/download/{filename}")
async def download_file(
    filename: str,
    current_user: User = Depends(get_current_active_user)
) -> FileResponse:
    """
    Download a file by filename.
    
    Args:
        filename: The name of the file to download
    
    Returns:
        FileResponse: The file content
    """
    file_path = get_file_path(filename)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )


@router.get("/list/{file_type}", response_model=List[dict])
async def list_files_by_type(
    file_type: str,
    current_user: User = Depends(get_current_active_user)
) -> List[dict]:
    """
    List all files of a specific type.
    
    Args:
        file_type: The type of file to list (input, reference, or report)
    
    Returns:
        List[dict]: A list of file metadata
    """
    return list_files(file_type)


@router.get("/list", response_model=List[dict])
async def list_all_files(
    current_user: User = Depends(get_current_active_user)
) -> List[dict]:
    """
    List all files.
    
    Returns:
        List[dict]: A list of file metadata
    """
    return list_files()
