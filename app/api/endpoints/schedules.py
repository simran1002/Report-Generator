from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_active_user
from app.models.report import ReportGenerationRequest, Schedule, ScheduleType
from app.models.user import User
from app.services.schedule_service import (create_schedule, delete_schedule,
                                          get_schedule, get_schedules,
                                          update_schedule)

router = APIRouter()


@router.get("", response_model=List[Schedule])
async def list_schedules(
    current_user: User = Depends(get_current_active_user)
) -> List[Schedule]:
    """
    List all schedules.
    
    Args:
        current_user: The current user
    
    Returns:
        List[Schedule]: A list of schedules
    """
    return get_schedules()


@router.get("/{schedule_id}", response_model=Schedule)
async def get_schedule_by_id(
    schedule_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Schedule:
    """
    Get a schedule by ID.
    
    Args:
        schedule_id: The ID of the schedule
        current_user: The current user
    
    Returns:
        Schedule: The schedule
    """
    schedule = get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail=f"Schedule not found: {schedule_id}")
    return schedule


@router.post("", response_model=Schedule)
async def create_new_schedule(
    name: str,
    schedule_type: ScheduleType,
    expression: str,
    report_request: ReportGenerationRequest,
    current_user: User = Depends(get_current_active_user)
) -> Schedule:
    """
    Create a new schedule.
    
    Args:
        name: The name of the schedule
        schedule_type: The type of schedule (cron, interval, or one_time)
        expression: The schedule expression
        report_request: The report generation request
        current_user: The current user
    
    Returns:
        Schedule: The created schedule
    """
    try:
        return create_schedule(name, schedule_type, expression, report_request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create schedule: {str(e)}")


@router.put("/{schedule_id}", response_model=Schedule)
async def update_existing_schedule(
    schedule_id: str,
    name: Optional[str] = None,
    schedule_type: Optional[ScheduleType] = None,
    expression: Optional[str] = None,
    enabled: Optional[bool] = None,
    report_request: Optional[ReportGenerationRequest] = None,
    current_user: User = Depends(get_current_active_user)
) -> Schedule:
    """
    Update an existing schedule.
    
    Args:
        schedule_id: The ID of the schedule
        name: The name of the schedule
        schedule_type: The type of schedule (cron, interval, or one_time)
        expression: The schedule expression
        enabled: Whether the schedule is enabled
        report_request: The report generation request
        current_user: The current user
    
    Returns:
        Schedule: The updated schedule
    """
    schedule = update_schedule(
        schedule_id,
        name,
        schedule_type,
        expression,
        enabled,
        report_request
    )
    if not schedule:
        raise HTTPException(status_code=404, detail=f"Schedule not found: {schedule_id}")
    return schedule


@router.delete("/{schedule_id}", response_model=dict)
async def delete_existing_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Delete a schedule.
    
    Args:
        schedule_id: The ID of the schedule
        current_user: The current user
    
    Returns:
        dict: Success message
    """
    success = delete_schedule(schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Schedule not found: {schedule_id}")
    return {"message": "Schedule deleted successfully"}
