from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class LeaveRequestCreate(BaseModel):
    leave_type: str # 'casual', 'sick', 'earned', 'unpaid', 'schedule_change'
    start_date: date
    end_date: date
    reason: str

class CorrectionRequestCreate(BaseModel):
    request_type: str # 'check_in', 'check_out', 'lunch_in', 'lunch_out', 'schedule_change'
    target_date: date
    requested_time: Optional[datetime] = None
    requested_off_day: Optional[int] = None
    reason: str

class RequestReview(BaseModel):
    status: str # 'approved', 'rejected'
    review_notes: Optional[str] = None

class LeaveRequestResponse(BaseModel):
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    status: str
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CorrectionRequestResponse(BaseModel):
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    attendance_id: Optional[str] = None
    request_type: str
    target_date: date
    requested_time: Optional[datetime] = None
    requested_off_day: Optional[int] = None
    reason: str
    status: str
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
