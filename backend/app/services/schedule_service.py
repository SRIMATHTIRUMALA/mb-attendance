from datetime import datetime, date, time
from typing import Optional, Tuple, Dict, Any, List
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.schedule import Shift, EmployeeSchedule, ScheduleOverride, Holiday
from app.models.profile import Profile
from app.core.config import settings

IST = ZoneInfo("Asia/Kolkata")

def get_now_ist() -> datetime:
    """Returns current server time converted to Asia/Kolkata timezone"""
    return datetime.now(IST)

def to_ist(dt: datetime) -> datetime:
    """Ensures datetime is localized to Asia/Kolkata"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(IST)
    return dt.astimezone(IST)

def get_employee_weekly_off_day(db: Session, employee_id: str, target_date: date) -> int:
    """
    Returns the weekly off day index (0=Mon...6=Sun) active for the employee on target_date.
    Checks effective-dated employee_schedules.
    Defaults to 6 (Sunday) if no schedule record exists.
    """
    schedule = db.query(EmployeeSchedule).filter(
        EmployeeSchedule.employee_id == employee_id,
        EmployeeSchedule.effective_from <= target_date,
        or_(
            EmployeeSchedule.effective_to.is_(None),
            EmployeeSchedule.effective_to >= target_date
        )
    ).order_by(EmployeeSchedule.effective_from.desc()).first()

    if schedule:
        return schedule.weekly_off_day
    return 6 # Sunday default

def check_day_status(db: Session, employee_id: str, target_date: date) -> Dict[str, Any]:
    """
    Determines if target_date is:
    - Official company holiday
    - Schedule override (swapped off or working on off)
    - Regular scheduled weekly off
    - Regular working day
    """
    # 1. Check official company holiday
    holiday = db.query(Holiday).filter(Holiday.holiday_date == target_date).first()
    if holiday:
        return {
            "is_working_day": False,
            "is_weekly_off": False,
            "is_holiday": True,
            "holiday_name": holiday.name,
            "reason": holiday.name
        }

    # 2. Check date-specific override
    override = db.query(ScheduleOverride).filter(
        ScheduleOverride.employee_id == employee_id,
        ScheduleOverride.override_date == target_date
    ).first()
    if override:
        return {
            "is_working_day": override.is_working_day,
            "is_weekly_off": not override.is_working_day,
            "is_holiday": False,
            "holiday_name": None,
            "reason": override.reason or ("Override: Working Day" if override.is_working_day else "Override: Weekly Off")
        }

    # 3. Check regular recurring weekly off
    weekly_off_day = get_employee_weekly_off_day(db, employee_id, target_date)
    is_off = (target_date.weekday() == weekly_off_day)

    return {
        "is_working_day": not is_off,
        "is_weekly_off": is_off,
        "is_holiday": False,
        "holiday_name": None,
        "reason": "Scheduled Weekly Off" if is_off else "Scheduled Working Day"
    }

def calculate_working_days(db: Session, employee_id: str, start_date: date, end_date: date) -> int:
    """
    Calculates actual scheduled working days between start_date and end_date (inclusive),
    taking into account the employee's specific weekly offs, overrides, and holidays.
    """
    from datetime import timedelta
    current = start_date
    working_days = 0
    while current <= end_date:
        status = check_day_status(db, employee_id, current)
        if status["is_working_day"]:
            working_days += 1
        current += timedelta(days=1)
    return working_days
