from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime, time
from decimal import Decimal

from app.db.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.profile import Profile
from app.models.request import LeaveRequest, CorrectionRequest
from app.models.attendance import AttendanceRecord, LunchRecord
from app.models.schedule import ScheduleOverride
from app.schemas.request import (
    LeaveRequestCreate,
    CorrectionRequestCreate,
    RequestReview,
    LeaveRequestResponse,
    CorrectionRequestResponse
)
from app.services.schedule_service import get_now_ist, IST

router = APIRouter(prefix="/requests", tags=["Requests & Approvals"])

@router.get("/leave", response_model=List[LeaveRequestResponse])
def list_leave_requests(
    status_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    query = db.query(LeaveRequest)
    if current_user.role != "admin":
        query = query.filter(LeaveRequest.employee_id == current_user.id)
    if status_filter:
        query = query.filter(LeaveRequest.status == status_filter)

    items = query.order_by(LeaveRequest.created_at.desc()).all()
    res = []
    for item in items:
        emp = db.query(Profile).filter(Profile.id == item.employee_id).first()
        res.append(LeaveRequestResponse(
            id=item.id,
            employee_id=item.employee_id,
            employee_name=emp.full_name if emp else None,
            leave_type=item.leave_type,
            start_date=item.start_date,
            end_date=item.end_date,
            reason=item.reason,
            status=item.status,
            reviewed_by=item.reviewed_by,
            review_notes=item.review_notes,
            reviewed_at=item.reviewed_at,
            created_at=item.created_at
        ))
    return res

@router.post("/leave", response_model=LeaveRequestResponse)
def create_leave_request(
    payload: LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    leave = LeaveRequest(
        employee_id=current_user.id,
        leave_type=payload.leave_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason=payload.reason.strip(),
        status="pending"
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)

    return LeaveRequestResponse(
        id=leave.id,
        employee_id=leave.employee_id,
        employee_name=current_user.full_name,
        leave_type=leave.leave_type,
        start_date=leave.start_date,
        end_date=leave.end_date,
        reason=leave.reason,
        status=leave.status,
        created_at=leave.created_at
    )

@router.get("/corrections", response_model=List[CorrectionRequestResponse])
def list_correction_requests(
    status_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    query = db.query(CorrectionRequest)
    if current_user.role != "admin":
        query = query.filter(CorrectionRequest.employee_id == current_user.id)
    if status_filter:
        query = query.filter(CorrectionRequest.status == status_filter)

    items = query.order_by(CorrectionRequest.created_at.desc()).all()
    res = []
    for item in items:
        emp = db.query(Profile).filter(Profile.id == item.employee_id).first()
        res.append(CorrectionRequestResponse(
            id=item.id,
            employee_id=item.employee_id,
            employee_name=emp.full_name if emp else None,
            attendance_id=item.attendance_id,
            request_type=item.request_type,
            target_date=item.target_date,
            requested_time=item.requested_time,
            requested_off_day=item.requested_off_day,
            reason=item.reason,
            status=item.status,
            reviewed_by=item.reviewed_by,
            review_notes=item.review_notes,
            reviewed_at=item.reviewed_at,
            created_at=item.created_at
        ))
    return res

@router.post("/corrections", response_model=CorrectionRequestResponse)
def create_correction_request(
    payload: CorrectionRequestCreate,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    # Check for existing attendance record if any
    att = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == current_user.id,
        AttendanceRecord.work_date == payload.target_date
    ).first()

    req = CorrectionRequest(
        employee_id=current_user.id,
        attendance_id=att.id if att else None,
        request_type=payload.request_type,
        target_date=payload.target_date,
        requested_time=payload.requested_time,
        requested_off_day=payload.requested_off_day,
        reason=payload.reason.strip(),
        status="pending"
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    return CorrectionRequestResponse(
        id=req.id,
        employee_id=req.employee_id,
        employee_name=current_user.full_name,
        attendance_id=req.attendance_id,
        request_type=req.request_type,
        target_date=req.target_date,
        requested_time=req.requested_time,
        requested_off_day=req.requested_off_day,
        reason=req.reason,
        status=req.status,
        created_at=req.created_at
    )

@router.patch("/leave/{id}/review")
def review_leave_request(
    id: str,
    payload: RequestReview,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(require_admin)
):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave.status = payload.status
    leave.review_notes = payload.review_notes
    leave.reviewed_by = current_user.id
    leave.reviewed_at = datetime.utcnow()

    db.commit()
    return {"status": "success", "request_status": leave.status}

@router.patch("/corrections/{id}/review")
def review_correction_request(
    id: str,
    payload: RequestReview,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(require_admin)
):
    req = db.query(CorrectionRequest).filter(CorrectionRequest.id == id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Correction request not found")

    req.status = payload.status
    req.review_notes = payload.review_notes
    req.reviewed_by = current_user.id
    req.reviewed_at = datetime.utcnow()

    # If approved, apply the correction to attendance!
    if payload.status == "approved":
        rec = db.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == req.employee_id,
            AttendanceRecord.work_date == req.target_date
        ).first()

        req_time = req.requested_time or datetime.combine(req.target_date, time(9, 0)).replace(tzinfo=IST)

        if req.request_type == "check_in":
            if not rec:
                rec = AttendanceRecord(
                    employee_id=req.employee_id,
                    work_date=req.target_date,
                    check_in_time=req_time,
                    status="present",
                    late_minutes=0,
                    check_in_mode="correction_approved"
                )
                db.add(rec)
            else:
                rec.check_in_time = req_time
                rec.status = "present"
                rec.late_minutes = 0
                rec.check_in_mode = "correction_approved"
        elif req.request_type == "check_out":
            if rec:
                rec.check_out_time = req_time
                rec.check_out_mode = "correction_approved"
                if rec.check_in_time:
                    cin = rec.check_in_time.replace(tzinfo=IST) if rec.check_in_time.tzinfo is None else rec.check_in_time
                    diff_hours = (req_time - cin).total_seconds() / 3600.0
                    rec.work_hours = Decimal(str(round(diff_hours, 2)))
        elif req.request_type == "schedule_change" and req.requested_off_day is not None:
            # Add schedule override for date
            override = ScheduleOverride(
                employee_id=req.employee_id,
                override_date=req.target_date,
                is_working_day=False,
                reason=f"Approved correction: {req.reason}",
                approved_by=current_user.id
            )
            db.add(override)

    db.commit()
    return {"status": "success", "request_status": req.status}
