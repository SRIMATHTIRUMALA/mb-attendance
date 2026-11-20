from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime, time

class EmployeeBase(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    designation: str
    role: str = "employee" # 'admin' or 'employee'
    joining_date: Optional[date] = None
    is_active: bool = True
    phone: Optional[str] = None
    weekly_off_day: int = 6 # Default Sunday (0=Mon, 6=Sun)

class EmployeeCreate(EmployeeBase):
    password: Optional[str] = "MBSolar@2026" # Initial temporary password if registering

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    designation: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    phone: Optional[str] = None
    weekly_off_day: Optional[int] = None

class ScheduleResponse(BaseModel):
    id: str
    employee_id: str
    weekly_off_day: int
    effective_from: date
    effective_to: Optional[date] = None

    class Config:
        from_attributes = True

class ScheduleOverrideResponse(BaseModel):
    id: str
    employee_id: str
    override_date: date
    is_working_day: bool
    reason: Optional[str] = None

    class Config:
        from_attributes = True

class EmployeeResponse(BaseModel):
    id: str
    employee_id: str
    full_name: str
    email: str
    designation: str
    role: str
    joining_date: date
    is_active: bool
    phone: Optional[str] = None
    current_weekly_off: Optional[int] = 6
    created_at: datetime

    class Config:
        from_attributes = True
