from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal

class DailyEmployeeReport(BaseModel):
    employee_id: str
    employee_code: str
    employee_name: str
    designation: str
    date: date
    attendance_status: str
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    late_minutes: int = 0
    work_hours: Optional[Decimal] = None
    lunch_out_time: Optional[str] = None
    lunch_in_time: Optional[str] = None
    lunch_late_minutes: int = 0
    lunch_missing_in: bool = False
    work_entries: List[Dict[str, Any]] = []
    has_unresolved_correction: bool = False

class WeeklyEmployeeReport(BaseModel):
    employee_id: str
    employee_code: str
    employee_name: str
    designation: str
    week_start: date
    week_end: date
    scheduled_days: int
    present_days: int
    late_days: int
    weekly_off_days: int
    approved_leave_days: int
    total_work_hours: Decimal
    daily_records: List[Dict[str, Any]] = []
    has_unresolved_corrections: bool = False

class MonthlyEmployeeReport(BaseModel):
    employee_id: str
    employee_code: str
    employee_name: str
    designation: str
    month: int
    year: int
    scheduled_working_days: int
    present_days: int
    absences: int
    approved_leaves: int
    weekly_offs: int
    late_arrivals: int
    total_late_minutes: int
    lunch_delays: int
    total_working_hours: Decimal
    unresolved_corrections_count: int

class ManagementSummaryReport(BaseModel):
    date: date
    total_employees: int
    present_count: int
    late_count: int
    weekly_off_count: int
    on_leave_count: int
    absent_count: int
    pending_corrections_count: int
    lunch_delay_count: int
    daily_work_submitted_count: int
    employee_reports: List[DailyEmployeeReport] = []
