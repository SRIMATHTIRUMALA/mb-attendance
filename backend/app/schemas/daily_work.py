from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime, time

class DailyWorkBase(BaseModel):
    work_date: date
    work_description: str
    work_details: Optional[str] = None # e.g. "24 calls made, 7 interested, 5 follow-ups required"
    start_time: Optional[time] = None
    end_time: Optional[time] = None

class DailyWorkCreate(DailyWorkBase):
    is_submitted: Optional[bool] = False

class DailyWorkUpdate(BaseModel):
    work_description: Optional[str] = None
    work_details: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_submitted: Optional[bool] = None

class DailyWorkResponse(DailyWorkBase):
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    employee_code: Optional[str] = None
    is_submitted: bool
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
