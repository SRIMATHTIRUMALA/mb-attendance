from datetime import datetime, date, time, timedelta
from typing import Optional, Dict, Any, Tuple
from decimal import Decimal
from zoneinfo import ZoneInfo
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.attendance import AttendanceRecord, LunchRecord
from app.models.request import CorrectionRequest
from app.models.profile import Profile
from app.services.schedule_service import get_now_ist, to_ist, check_day_status, IST

def process_check_in(
    db: Session,
    employee: Profile,
    custom_time: Optional[datetime] = None
) -> AttendanceRecord:
    """
    Handles employee check-in according to MB Solar Hub business rules.
    - Window opens at 8:45 AM IST
    - Window closes at 10:00 AM IST
    - 8:45 AM - 9:00 AM: On time
    - 9:00 AM - 10:00 AM: Late (late_minutes tracked)
    - After 10:00 AM: Direct check-in locked. Late correction request required.
    """
    now = custom_time if custom_time else get_now_ist()
    if now.tzinfo is None:
        now = now.replace(tzinfo=IST)
    else:
        now = now.astimezone(IST)

    today = now.date()

    # 1. Prevent duplicate check-in
    existing = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee.id,
        AttendanceRecord.work_date == today
    ).first()

    if existing and existing.check_in_time is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You have already checked in today at {existing.check_in_time.astimezone(IST).strftime('%I:%M %p')}."
        )

    # 2. Check time window
    time_val = now.time()
    window_open = time(8, 45)
    work_start = time(9, 0)
    window_close = time(10, 0)

    if time_val < window_open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Check-in window opens at 8:45 AM IST. Current time is {time_val.strftime('%I:%M %p')}."
        )

    if time_val > window_close:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Normal check-in window closed at 10:00 AM IST. Please submit a Late Check-In Correction Request."
        )

    # 3. Calculate punctuality
    late_minutes = 0
    attendance_status = "present"

    if time_val > work_start:
        attendance_status = "late"
        # Calculate diff from 9:00 AM
        today_work_start = datetime.combine(today, work_start).replace(tzinfo=IST)
        diff = now - today_work_start
        late_minutes = max(0, int(diff.total_seconds() // 60))

    # 4. Create or update record
    if not existing:
        record = AttendanceRecord(
            employee_id=employee.id,
            work_date=today,
            check_in_time=now,
            status=attendance_status,
            late_minutes=late_minutes,
            check_in_mode="normal"
        )
        db.add(record)
    else:
        existing.check_in_time = now
        existing.status = attendance_status
        existing.late_minutes = late_minutes
        existing.check_in_mode = "normal"
        record = existing

    db.commit()
    db.refresh(record)
    return record

def process_check_out(
    db: Session,
    employee: Profile,
    custom_time: Optional[datetime] = None
) -> AttendanceRecord:
    """
    Handles employee checkout according to MB Solar Hub business rules:
    - Opens at 6:00 PM IST
    - Closes at 7:00 PM IST
    - Before 6:00 PM: Blocked
    - After 7:00 PM: Blocked, correction request required
    """
    now = custom_time if custom_time else get_now_ist()
    if now.tzinfo is None:
        now = now.replace(tzinfo=IST)
    else:
        now = now.astimezone(IST)

    today = now.date()

    record = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee.id,
        AttendanceRecord.work_date == today
    ).first()

    if not record or not record.check_in_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not checked in today. Please check in first or submit an attendance request."
        )

    if record.check_out_time is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You have already checked out today at {record.check_out_time.astimezone(IST).strftime('%I:%M %p')}."
        )

    time_val = now.time()
    window_open = time(18, 0)
    window_close = time(19, 0)

    if time_val < window_open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Check-out window opens at 6:00 PM IST. Current time is {time_val.strftime('%I:%M %p')}."
        )

    if time_val > window_close:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Normal check-out window closed at 7:00 PM IST. Please submit a Checkout Correction Request."
        )

    # Calculate working hours
    check_in_dt = record.check_in_time
    if check_in_dt.tzinfo is None:
        check_in_dt = check_in_dt.replace(tzinfo=IST)
    else:
        check_in_dt = check_in_dt.astimezone(IST)

    total_seconds = (now - check_in_dt).total_seconds()
    hours = Decimal(str(round(total_seconds / 3600.0, 2)))

    record.check_out_time = now
    record.work_hours = hours
    record.check_out_mode = "normal"

    db.commit()
    db.refresh(record)
    return record

def process_lunch_out(
    db: Session,
    employee: Profile,
    notes: Optional[str] = None,
    custom_time: Optional[datetime] = None
) -> LunchRecord:
    """
    Lunch Out: for employees physically leaving the office for lunch.
    Validates check-in exists and no open lunch record.
    """
    now = custom_time if custom_time else get_now_ist()
    if now.tzinfo is None:
        now = now.replace(tzinfo=IST)
    else:
        now = now.astimezone(IST)

    today = now.date()

    attendance = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee.id,
        AttendanceRecord.work_date == today
    ).first()

    if not attendance or not attendance.check_in_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot record lunch exit without active check-in."
        )

    if attendance.check_out_time is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot record lunch after checking out for the day."
        )

    # Check for existing open lunch
    open_lunch = db.query(LunchRecord).filter(
        LunchRecord.attendance_id == attendance.id,
        LunchRecord.lunch_in_time.is_(None)
    ).first()

    if open_lunch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are currently marked as out for lunch. Please punch Lunch In upon return."
        )

    lunch = LunchRecord(
        attendance_id=attendance.id,
        employee_id=employee.id,
        work_date=today,
        lunch_out_time=now,
        notes=notes
    )
    db.add(lunch)
    db.commit()
    db.refresh(lunch)
    return lunch

def process_lunch_in(
    db: Session,
    employee: Profile,
    custom_time: Optional[datetime] = None
) -> LunchRecord:
    """
    Lunch In: marks return from lunch.
    - If return is after 2:00 PM IST (14:00), calculates late return minutes.
      E.g., return at 2:15 PM = 15 late minutes.
    - Prevents lunch in without lunch out.
    """
    now = custom_time if custom_time else get_now_ist()
    if now.tzinfo is None:
        now = now.replace(tzinfo=IST)
    else:
        now = now.astimezone(IST)

    today = now.date()

    attendance = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee.id,
        AttendanceRecord.work_date == today
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No attendance record found for today."
        )

    open_lunch = db.query(LunchRecord).filter(
        LunchRecord.attendance_id == attendance.id,
        LunchRecord.lunch_in_time.is_(None)
    ).first()

    if not open_lunch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active Lunch Out record found. You must punch Lunch Out before Lunch In."
        )

    # Calculate duration
    out_time = open_lunch.lunch_out_time
    if out_time.tzinfo is None:
        out_time = out_time.replace(tzinfo=IST)
    else:
        out_time = out_time.astimezone(IST)

    duration = int((now - out_time).total_seconds() // 60)

    # Check late return: lunch ends at 2:00 PM (14:00 IST)
    lunch_end = datetime.combine(today, time(14, 0)).replace(tzinfo=IST)
    late_minutes = 0
    if now > lunch_end:
        late_minutes = int((now - lunch_end).total_seconds() // 60)

    open_lunch.lunch_in_time = now
    open_lunch.duration_minutes = max(0, duration)
    open_lunch.late_minutes = max(0, late_minutes)
    open_lunch.missing_lunch_in = False

    db.commit()
    db.refresh(open_lunch)
    return open_lunch

def get_employee_today_status(db: Session, employee: Profile) -> Dict[str, Any]:
    """Returns today's current live attendance state and available actions"""
    now = get_now_ist()
    today = now.date()
    time_val = now.time()

    day_info = check_day_status(db, employee.id, today)

    record = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee.id,
        AttendanceRecord.work_date == today
    ).first()

    current_state = "not_checked_in"
    can_check_in = False
    can_check_out = False
    can_lunch_out = False
    can_lunch_in = False

    # Check-in window is 08:45 to 10:00
    is_in_checkin_window = (time(8, 45) <= time_val <= time(10, 0))
    # Check-out window is 18:00 to 19:00
    is_in_checkout_window = (time(18, 0) <= time_val <= time(19, 0))

    if not record or not record.check_in_time:
        current_state = "not_checked_in"
        can_check_in = is_in_checkin_window
    elif record.check_out_time is not None:
        current_state = "checked_out"
    else:
        # Checked in and not checked out
        # Check lunch status
        open_lunch = db.query(LunchRecord).filter(
            LunchRecord.attendance_id == record.id,
            LunchRecord.lunch_in_time.is_(None)
        ).first()

        if open_lunch:
            current_state = "on_lunch"
            can_lunch_in = True
        else:
            current_state = "checked_in"
            can_lunch_out = True
            can_check_out = is_in_checkout_window

    has_unresolved_correction = False
    if record:
        unresolved = db.query(CorrectionRequest).filter(
            CorrectionRequest.employee_id == employee.id,
            CorrectionRequest.target_date == today,
            CorrectionRequest.status == "pending"
        ).count()
        has_unresolved_correction = (unresolved > 0)

    return {
        "work_date": today,
        "is_scheduled_work_day": day_info["is_working_day"],
        "is_weekly_off": day_info["is_weekly_off"],
        "is_holiday": day_info["is_holiday"],
        "holiday_name": day_info["holiday_name"],
        "attendance": record,
        "current_state": current_state,
        "can_check_in": can_check_in,
        "can_check_out": can_check_out,
        "can_lunch_out": can_lunch_out,
        "can_lunch_in": can_lunch_in,
        "server_time_ist": now.strftime("%Y-%m-%d %I:%M:%S %p %Z"),
        "has_unresolved_correction": has_unresolved_correction
    }
