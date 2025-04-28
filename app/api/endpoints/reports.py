import os
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.security import get_current_active_user
from app.models.report import ReportGenerationRequest, ReportMetadata, ReportStatus
from app.models.user import User
from app.services.report_service import generate_report, get_report_metadata

router = APIRouter()


@router.post("/generate", response_model=ReportMetadata)
async def create_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
) -> ReportMetadata:
    """
    Generate a new report.
    
    Args:
        request: The report generation request
        background_tasks: FastAPI background tasks
        current_user: The current user
    
    Returns:
        ReportMetadata: Metadata about the generated report
    """
    report_metadata = generate_report(request, current_user.username)
    return report_metadata


@router.get("/{report_id}", response_model=ReportMetadata)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user)
) -> ReportMetadata:
    """
    Get metadata for a specific report.
    
    Args:
        report_id: The ID of the report
        current_user: The current user
    
    Returns:
        ReportMetadata: Metadata about the report
    """
    report = get_report_metadata(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")
    return report


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user)
) -> FileResponse:
    """
    Download a specific report.
    
    Args:
        report_id: The ID of the report
        current_user: The current user
    
    Returns:
        FileResponse: The report file
    """
    report = get_report_metadata(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")
    
    if report.status != ReportStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Report is not ready for download. Current status: {report.status}"
        )
    
    file_path = os.path.join(settings.REPORTS_DIR, report.output_file)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        path=file_path,
        filename=report.output_file,
        media_type="application/octet-stream"
    )
