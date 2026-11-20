from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel

from app.db.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.profile import Profile
from app.models.schedule import Shift, EmployeeSchedule, ScheduleOverride, Holiday
from app.schemas.employee import ScheduleResponse, ScheduleOverrideResponse
from app.services.schedule_service import get_employee_weekly_off_day, check_day_status

router = APIRouter(prefix="/schedules", tags=["Schedules & Holidays"])

class ScheduleAssignRequest(BaseModel):
    employee_id: str
    weekly_off_day: int # 0=Mon, 6=Sun
    effective_from: date

class OverrideRequest(BaseModel):
    employee_id: str
    override_date: date
    is_working_day: bool
    reason: Optional[str] = None

class HolidayCreate(BaseModel):
    holiday_date: date
    name: str
    description: Optional[str] = None

@router.get("", response_model=List[ScheduleResponse])
def get_schedules(
    employee_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    query = db.query(EmployeeSchedule)
    if employee_id:
        if current_user.role != "admin" and employee_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        query = query.filter(EmployeeSchedule.employee_id == employee_id)
    else:
        if current_user.role != "admin":
            query = query.filter(EmployeeSchedule.employee_id == current_user.id)

    return query.order_by(EmployeeSchedule.effective_from.desc()).all()

@router.post("", response_model=ScheduleResponse)
def assign_schedule(
    payload: ScheduleAssignRequest,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(require_admin)
):
    # Close any active open schedule for this employee
    active_sched = db.query(EmployeeSchedule).filter(
        EmployeeSchedule.employee_id == payload.employee_id,
        EmployeeSchedule.effective_to.is_(None)
    ).first()
    if active_sched:
        active_sched.effective_to = payload.effective_from

    sched = EmployeeSchedule(
        employee_id=payload.employee_id,
        weekly_off_day=payload.weekly_off_day,
        effective_from=payload.effective_from,
        created_by=current_user.id
    )
    db.add(sched)
    db.commit()
    db.refresh(sched)
    return sched

@router.post("/override", response_model=ScheduleOverrideResponse)
def set_schedule_override(
    payload: OverrideRequest,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(require_admin)
):
    existing = db.query(ScheduleOverride).filter(
        ScheduleOverride.employee_id == payload.employee_id,
        ScheduleOverride.override_date == payload.override_date
    ).first()

    if existing:
        existing.is_working_day = payload.is_working_day
        existing.reason = payload.reason
        existing.approved_by = current_user.id
        db.commit()
        db.refresh(existing)
        return existing

    override = ScheduleOverride(
        employee_id=payload.employee_id,
        override_date=payload.override_date,
        is_working_day=payload.is_working_day,
        reason=payload.reason,
        approved_by=current_user.id
    )
    db.add(override)
    db.commit()
    db.refresh(override)
    return override

@router.get("/holidays")
def list_holidays(db: Session = Depends(get_db)):
    return db.query(Holiday).order_by(Holiday.holiday_date.asc()).all()

@router.post("/holidays")
def create_holiday(
    payload: HolidayCreate,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(require_admin)
):
    existing = db.query(Holiday).filter(Holiday.holiday_date == payload.holiday_date).first()
    if existing:
        raise HTTPException(status_code=400, detail="Holiday already exists on this date")

    holiday = Holiday(
        holiday_date=payload.holiday_date,
        name=payload.name,
        description=payload.description
    )
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    return holiday
