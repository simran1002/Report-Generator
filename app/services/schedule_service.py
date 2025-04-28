import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import yaml
from croniter import croniter

from app.core.config import settings
from app.models.report import ReportGenerationRequest, Schedule, ScheduleType


def get_schedules() -> List[Schedule]:
    """
    Get all schedules.
    """
    # If no schedules file exists, create an empty one
    if not os.path.exists(settings.SCHEDULES_FILE):
        with open(settings.SCHEDULES_FILE, "w") as f:
            yaml.dump({}, f)
    
    # Load schedules
    with open(settings.SCHEDULES_FILE, "r") as f:
        schedules_data = yaml.safe_load(f) or {}
    
    # Convert to models
    schedules = []
    for schedule_id, data in schedules_data.items():
        schedule = Schedule(
            id=schedule_id,
            name=data["name"],
            schedule_type=data["schedule_type"],
            expression=data["expression"],
            enabled=data["enabled"],
            last_run=data.get("last_run"),
            next_run=data.get("next_run"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
        
        # Update next run time if it's a cron schedule
        if schedule.schedule_type == ScheduleType.CRON and schedule.enabled:
            base_time = schedule.last_run or datetime.now()
            try:
                cron = croniter(schedule.expression, base_time)
                schedule.next_run = cron.get_next(datetime)
            except Exception:
                # Invalid cron expression
                schedule.enabled = False
        
        schedules.append(schedule)
    
    return schedules


def get_schedule(schedule_id: str) -> Optional[Schedule]:
    """
    Get a schedule by ID.
    """
    schedules = get_schedules()
    for schedule in schedules:
        if schedule.id == schedule_id:
            return schedule
    return None


def create_schedule(
    name: str,
    schedule_type: ScheduleType,
    expression: str,
    report_request: ReportGenerationRequest
) -> Schedule:
    """
    Create a new schedule.
    """
    # Validate cron expression if it's a cron schedule
    if schedule_type == ScheduleType.CRON:
        try:
            croniter(expression, datetime.now())
        except Exception as e:
            raise ValueError(f"Invalid cron expression: {str(e)}")
    
    # Create new schedule
    schedule_id = str(uuid.uuid4())
    now = datetime.now()
    
    schedule = Schedule(
        id=schedule_id,
        name=name,
        schedule_type=schedule_type,
        expression=expression,
        enabled=True,
        created_at=now,
        updated_at=now
    )
    
    # Calculate next run time
    if schedule_type == ScheduleType.CRON:
        cron = croniter(expression, now)
        schedule.next_run = cron.get_next(datetime)
    elif schedule_type == ScheduleType.INTERVAL:
        # Expression is interval in seconds
        interval_seconds = int(expression)
        schedule.next_run = now.timestamp() + interval_seconds
    elif schedule_type == ScheduleType.ONE_TIME:
        # Expression is ISO datetime
        schedule.next_run = datetime.fromisoformat(expression)
    
    # Save schedule
    _save_schedule(schedule, report_request)
    
    return schedule


def update_schedule(
    schedule_id: str,
    name: Optional[str] = None,
    schedule_type: Optional[ScheduleType] = None,
    expression: Optional[str] = None,
    enabled: Optional[bool] = None,
    report_request: Optional[ReportGenerationRequest] = None
) -> Optional[Schedule]:
    """
    Update an existing schedule.
    """
    # Get existing schedule
    schedule = get_schedule(schedule_id)
    if not schedule:
        return None
    
    # Update fields
    if name is not None:
        schedule.name = name
    if schedule_type is not None:
        schedule.schedule_type = schedule_type
    if expression is not None:
        schedule.expression = expression
    if enabled is not None:
        schedule.enabled = enabled
    
    # Update next run time
    if schedule.enabled and (schedule_type is not None or expression is not None):
        if schedule.schedule_type == ScheduleType.CRON:
            try:
                cron = croniter(schedule.expression, datetime.now())
                schedule.next_run = cron.get_next(datetime)
            except Exception:
                # Invalid cron expression
                schedule.enabled = False
        elif schedule.schedule_type == ScheduleType.INTERVAL:
            # Expression is interval in seconds
            interval_seconds = int(schedule.expression)
            schedule.next_run = datetime.now().timestamp() + interval_seconds
        elif schedule.schedule_type == ScheduleType.ONE_TIME:
            # Expression is ISO datetime
            schedule.next_run = datetime.fromisoformat(schedule.expression)
    
    # Update timestamp
    schedule.updated_at = datetime.now()
    
    # Save schedule
    _save_schedule(schedule, report_request)
    
    return schedule


def delete_schedule(schedule_id: str) -> bool:
    """
    Delete a schedule.
    """
    # Load schedules
    if not os.path.exists(settings.SCHEDULES_FILE):
        return False
    
    with open(settings.SCHEDULES_FILE, "r") as f:
        schedules_data = yaml.safe_load(f) or {}
    
    # Check if schedule exists
    if schedule_id not in schedules_data:
        return False
    
    # Delete schedule
    del schedules_data[schedule_id]
    
    # Save schedules
    with open(settings.SCHEDULES_FILE, "w") as f:
        yaml.dump(schedules_data, f)
    
    return True


def _save_schedule(schedule: Schedule, report_request: Optional[ReportGenerationRequest] = None) -> None:
    """
    Save a schedule to the schedules file.
    """
    # Load existing schedules
    if os.path.exists(settings.SCHEDULES_FILE):
        with open(settings.SCHEDULES_FILE, "r") as f:
            schedules_data = yaml.safe_load(f) or {}
    else:
        schedules_data = {}
    
    # Update or add schedule
    schedules_data[schedule.id] = {
        "name": schedule.name,
        "schedule_type": schedule.schedule_type,
        "expression": schedule.expression,
        "enabled": schedule.enabled,
        "last_run": schedule.last_run.isoformat() if schedule.last_run else None,
        "next_run": schedule.next_run.isoformat() if schedule.next_run else None,
        "created_at": schedule.created_at.isoformat(),
        "updated_at": schedule.updated_at.isoformat()
    }
    
    # Add report request if provided
    if report_request:
        schedules_data[schedule.id]["report_request"] = report_request.dict()
    
    # Save to file
    with open(settings.SCHEDULES_FILE, "w") as f:
        yaml.dump(schedules_data, f)
