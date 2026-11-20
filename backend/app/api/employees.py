from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.db.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.profile import Profile
from app.models.schedule import EmployeeSchedule
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.services.schedule_service import get_employee_weekly_off_day

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("", response_model=List[EmployeeResponse])
def list_employees(
    db: Session = Depends(get_db),
    current_user: Profile = Depends(require_admin)
):
    employees = db.query(Profile).order_by(Profile.employee_id).all()
    result = []
    today = date.today()
    for emp in employees:
        off_day = get_employee_weekly_off_day(db, emp.id, today)
        resp = EmployeeResponse(
            id=emp.id,
            employee_id=emp.employee_id,
            full_name=emp.full_name,
            email=emp.email,
            designation=emp.designation,
            role=emp.role,
            joining_date=emp.joining_date,
            is_active=emp.is_active,
            phone=emp.phone,
            current_weekly_off=off_day,
            created_at=emp.created_at
        )
        result.append(resp)
    return result

@router.post("", response_model=EmployeeResponse)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(require_admin)
):
    # Check duplicate ID or Email
    if db.query(Profile).filter(Profile.employee_id == payload.employee_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee ID '{payload.employee_id}' is already registered."
        )

    if db.query(Profile).filter(Profile.email == payload.email.lower()).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{payload.email}' is already in use."
        )

    new_emp = Profile(
        employee_id=payload.employee_id.strip().upper(),
        full_name=payload.full_name.strip(),
        email=payload.email.strip().lower(),
        designation=payload.designation.strip(),
        role=payload.role,
        joining_date=payload.joining_date or date.today(),
        is_active=payload.is_active,
        phone=payload.phone
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)

    # Create schedule record
    schedule = EmployeeSchedule(
        employee_id=new_emp.id,
        weekly_off_day=payload.weekly_off_day,
        effective_from=payload.joining_date or date.today(),
        created_by=current_user.id
    )
    db.add(schedule)
    db.commit()

    return EmployeeResponse(
        id=new_emp.id,
        employee_id=new_emp.employee_id,
        full_name=new_emp.full_name,
        email=new_emp.email,
        designation=new_emp.designation,
        role=new_emp.role,
        joining_date=new_emp.joining_date,
        is_active=new_emp.is_active,
        phone=new_emp.phone,
        current_weekly_off=payload.weekly_off_day,
        created_at=new_emp.created_at
    )

@router.get("/{id}", response_model=EmployeeResponse)
def get_employee(
    id: str,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    # Verify permission: Admin can view any, employee only their own
    if current_user.role != "admin" and current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to other employee records."
        )

    emp = db.query(Profile).filter(Profile.id == id).first()
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    off_day = get_employee_weekly_off_day(db, emp.id, date.today())
    return EmployeeResponse(
        id=emp.id,
        employee_id=emp.employee_id,
        full_name=emp.full_name,
        email=emp.email,
        designation=emp.designation,
        role=emp.role,
        joining_date=emp.joining_date,
        is_active=emp.is_active,
        phone=emp.phone,
        current_weekly_off=off_day,
        created_at=emp.created_at
    )

@router.patch("/{id}", response_model=EmployeeResponse)
def update_employee(
    id: str,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(require_admin)
):
    emp = db.query(Profile).filter(Profile.id == id).first()
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    if payload.full_name is not None:
        emp.full_name = payload.full_name.strip()
    if payload.designation is not None:
        emp.designation = payload.designation.strip()
    if payload.role is not None:
        emp.role = payload.role
    if payload.is_active is not None:
        emp.is_active = payload.is_active
    if payload.phone is not None:
        emp.phone = payload.phone

    if payload.weekly_off_day is not None:
        # Create effective new schedule
        new_sched = EmployeeSchedule(
            employee_id=emp.id,
            weekly_off_day=payload.weekly_off_day,
            effective_from=date.today(),
            created_by=current_user.id
        )
        db.add(new_sched)

    db.commit()
    db.refresh(emp)

    off_day = get_employee_weekly_off_day(db, emp.id, date.today())
    return EmployeeResponse(
        id=emp.id,
        employee_id=emp.employee_id,
        full_name=emp.full_name,
        email=emp.email,
        designation=emp.designation,
        role=emp.role,
        joining_date=emp.joining_date,
        is_active=emp.is_active,
        phone=emp.phone,
        current_weekly_off=off_day,
        created_at=emp.created_at
    )
