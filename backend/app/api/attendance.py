from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.profile import Profile
from app.models.attendance import AttendanceRecord
from app.schemas.attendance import (
    CheckInRequest,
    CheckOutRequest,
    AttendanceResponse,
    TodayStatusResponse
)
from app.services.attendance_service import (
    process_check_in,
    process_check_out,
    get_employee_today_status
)

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.get("/today", response_model=TodayStatusResponse)
def get_today_status(
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    status_data = get_employee_today_status(db, current_user)
    return status_data

@router.post("/check-in", response_model=AttendanceResponse)
def check_in(
    payload: CheckInRequest = None,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    ts = payload.timestamp if payload else None
    record = process_check_in(db, current_user, custom_time=ts)
    return record

@router.post("/check-out", response_model=AttendanceResponse)
def check_out(
    payload: CheckOutRequest = None,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    ts = payload.timestamp if payload else None
    record = process_check_out(db, current_user, custom_time=ts)
    return record

@router.get("/history", response_model=List[AttendanceResponse])
def get_attendance_history(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    employee_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    query = db.query(AttendanceRecord)

    # Permission check: if employee_id specified and not current user, must be admin
    if employee_id:
        if current_user.role != "admin" and employee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to view other employees' records."
            )
        query = query.filter(AttendanceRecord.employee_id == employee_id)
    else:
        # Default: if admin and no employee specified, show all; if employee, show only own
        if current_user.role != "admin":
            query = query.filter(AttendanceRecord.employee_id == current_user.id)

    if start_date:
        query = query.filter(AttendanceRecord.work_date >= start_date)
    if end_date:
        query = query.filter(AttendanceRecord.work_date <= end_date)

    records = query.order_by(AttendanceRecord.work_date.desc()).all()
    return records
