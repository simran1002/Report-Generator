from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class FileFormat(str, Enum):
    CSV = "csv"
    EXCEL = "xlsx"
    JSON = "json"


class FileUploadResponse(BaseModel):
    filename: str
    file_type: str
    file_size: int
    upload_time: datetime
    status: str = "success"


class TransformationRule(BaseModel):
    output_field: str
    expression: str
    description: Optional[str] = None


class TransformationRuleSet(BaseModel):
    rules: List[TransformationRule]
    version: str = "1.0"
    updated_at: datetime = Field(default_factory=datetime.now)


class ScheduleType(str, Enum):
    CRON = "cron"
    INTERVAL = "interval"
    ONE_TIME = "one_time"


class Schedule(BaseModel):
    id: str
    name: str
    schedule_type: ScheduleType
    expression: str
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ReportGenerationRequest(BaseModel):
    input_file: Optional[str] = None 
    reference_file: Optional[str] = None  
    output_format: FileFormat = FileFormat.CSV
    rule_set_id: Optional[str] = None 


class ReportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportMetadata(BaseModel):
    id: str
    input_file: str
    reference_file: str
    output_file: str
    output_format: FileFormat
    rule_set_id: str
    status: ReportStatus
    error_message: Optional[str] = None
    rows_processed: int = 0
    start_time: datetime
    end_time: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None
    created_by: str
    
    class Config:
        orm_mode = True


class ReportListResponse(BaseModel):
    reports: List[ReportMetadata]
    total: int
