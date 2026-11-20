from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime, time
from decimal import Decimal

class LunchRecordResponse(BaseModel):
    id: str
    attendance_id: str
    employee_id: str
    work_date: date
    lunch_out_time: datetime
    lunch_in_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    late_minutes: int = 0
    missing_lunch_in: bool = False
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class AttendanceResponse(BaseModel):
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    employee_code: Optional[str] = None
    work_date: date
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    status: str
    late_minutes: int = 0
    work_hours: Optional[Decimal] = None
    check_in_mode: str = "normal"
    check_out_mode: Optional[str] = "normal"
    lunch_records: List[LunchRecordResponse] = []
    has_unresolved_correction: bool = False

    class Config:
        from_attributes = True

class CheckInRequest(BaseModel):
    # Optional override timestamp for server mock/tests; if omitted backend uses server time
    timestamp: Optional[datetime] = None

class CheckOutRequest(BaseModel):
    timestamp: Optional[datetime] = None

class LunchOutRequest(BaseModel):
    timestamp: Optional[datetime] = None
    notes: Optional[str] = None

class LunchInRequest(BaseModel):
    timestamp: Optional[datetime] = None

class TodayStatusResponse(BaseModel):
    work_date: date
    is_scheduled_work_day: bool
    is_weekly_off: bool
    is_holiday: bool
    holiday_name: Optional[str] = None
    attendance: Optional[AttendanceResponse] = None
    current_state: str # 'not_checked_in', 'checked_in', 'on_lunch', 'returned_from_lunch', 'checked_out'
    can_check_in: bool
    can_check_out: bool
    can_lunch_out: bool
    can_lunch_in: bool
    server_time_ist: str
