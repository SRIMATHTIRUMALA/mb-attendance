from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.profile import Profile
from app.models.daily_work import DailyWorkEntry
from app.models.report import AuditLog
from app.schemas.daily_work import DailyWorkCreate, DailyWorkUpdate, DailyWorkResponse
from app.services.schedule_service import get_now_ist

router = APIRouter(prefix="/work", tags=["Daily Work Management"])

@router.get("", response_model=List[DailyWorkResponse])
def list_daily_work(
    work_date: Optional[date] = Query(None),
    employee_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    query = db.query(DailyWorkEntry)

    if employee_id:
        if current_user.role != "admin" and employee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to view other employees' daily work entries."
            )
        query = query.filter(DailyWorkEntry.employee_id == employee_id)
    else:
        if current_user.role != "admin":
            query = query.filter(DailyWorkEntry.employee_id == current_user.id)

    if work_date:
        query = query.filter(DailyWorkEntry.work_date == work_date)

    entries = query.order_by(DailyWorkEntry.work_date.desc(), DailyWorkEntry.created_at.asc()).all()
    
    # Enrich response
    result = []
    for e in entries:
        emp = db.query(Profile).filter(Profile.id == e.employee_id).first()
        result.append(DailyWorkResponse(
            id=e.id,
            employee_id=e.employee_id,
            employee_name=emp.full_name if emp else None,
            employee_code=emp.employee_id if emp else None,
            work_date=e.work_date,
            work_description=e.work_description,
            work_details=e.work_details,
            start_time=e.start_time,
            end_time=e.end_time,
            is_submitted=e.is_submitted,
            submitted_at=e.submitted_at,
            created_at=e.created_at,
            updated_at=e.updated_at
        ))
    return result

@router.post("", response_model=DailyWorkResponse)
def create_daily_work(
    payload: DailyWorkCreate,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    entry = DailyWorkEntry(
        employee_id=current_user.id,
        work_date=payload.work_date,
        work_description=payload.work_description.strip(),
        work_details=payload.work_details.strip() if payload.work_details else None,
        start_time=payload.start_time,
        end_time=payload.end_time,
        is_submitted=payload.is_submitted or False,
        submitted_at=datetime.utcnow() if payload.is_submitted else None
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Log audit
    audit = AuditLog(
        actor_id=current_user.id,
        action="CREATE_WORK_ENTRY",
        target_entity="daily_work_entries",
        target_id=entry.id,
        changes={"description": entry.work_description, "is_submitted": entry.is_submitted}
    )
    db.add(audit)
    db.commit()

    return DailyWorkResponse(
        id=entry.id,
        employee_id=entry.employee_id,
        employee_name=current_user.full_name,
        employee_code=current_user.employee_id,
        work_date=entry.work_date,
        work_description=entry.work_description,
        work_details=entry.work_details,
        start_time=entry.start_time,
        end_time=entry.end_time,
        is_submitted=entry.is_submitted,
        submitted_at=entry.submitted_at,
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )

@router.patch("/{id}", response_model=DailyWorkResponse)
def update_daily_work(
    id: str,
    payload: DailyWorkUpdate,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    entry = db.query(DailyWorkEntry).filter(DailyWorkEntry.id == id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily work entry not found")

    if current_user.role != "admin" and entry.employee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot edit another employee's daily work."
        )

    was_submitted = entry.is_submitted
    changes_record = {}

    if payload.work_description is not None:
        changes_record["work_description"] = {"old": entry.work_description, "new": payload.work_description}
        entry.work_description = payload.work_description.strip()
    if payload.work_details is not None:
        changes_record["work_details"] = {"old": entry.work_details, "new": payload.work_details}
        entry.work_details = payload.work_details.strip()
    if payload.start_time is not None:
        entry.start_time = payload.start_time
    if payload.end_time is not None:
        entry.end_time = payload.end_time
    if payload.is_submitted is not None:
        entry.is_submitted = payload.is_submitted
        if payload.is_submitted and not entry.submitted_at:
            entry.submitted_at = datetime.utcnow()

    # If modifying an already submitted entry, preserve explicit audit trail!
    if was_submitted:
        audit = AuditLog(
            actor_id=current_user.id,
            action="EDIT_SUBMITTED_WORK_ENTRY",
            target_entity="daily_work_entries",
            target_id=entry.id,
            changes=changes_record
        )
        db.add(audit)

    db.commit()
    db.refresh(entry)

    emp = db.query(Profile).filter(Profile.id == entry.employee_id).first()
    return DailyWorkResponse(
        id=entry.id,
        employee_id=entry.employee_id,
        employee_name=emp.full_name if emp else None,
        employee_code=emp.employee_id if emp else None,
        work_date=entry.work_date,
        work_description=entry.work_description,
        work_details=entry.work_details,
        start_time=entry.start_time,
        end_time=entry.end_time,
        is_submitted=entry.is_submitted,
        submitted_at=entry.submitted_at,
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )

@router.delete("/{id}")
def delete_daily_work(
    id: str,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    entry = db.query(DailyWorkEntry).filter(DailyWorkEntry.id == id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily work entry not found")

    if current_user.role != "admin" and entry.employee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete another employee's entry.")

    db.delete(entry)
    db.commit()
    return {"status": "success", "message": "Work entry deleted"}
