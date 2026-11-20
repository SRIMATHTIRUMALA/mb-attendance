from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.db.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.profile import Profile
from app.models.attendance import AttendanceRecord, LunchRecord
from app.models.daily_work import DailyWorkEntry
from app.models.request import LeaveRequest, CorrectionRequest
from app.services.report_service import (
    get_employee_daily_data,
    get_employee_range_data,
    generate_weekly_excel_report,
    generate_pdf_report
)
from app.services.email_service import trigger_scheduled_management_report
from app.services.schedule_service import get_now_ist, check_day_status

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])

@router.get("/summary")
def get_dashboard_summary(
    target_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Profile = Depends(require_admin)
):
    """Admin dashboard stats overview"""
    today = target_date or get_now_ist().date()
    total_employees = db.query(Profile).filter(Profile.is_active == True).count()
    employees = db.query(Profile).filter(Profile.is_active == True).all()

    present_count = 0
    late_count = 0
    weekly_off_count = 0
    on_leave_count = 0
    absent_count = 0
    lunch_delays_count = 0
    missing_lunch_in_count = 0
    work_submitted_count = 0

    for emp in employees:
        d_status = check_day_status(db, emp.id, today)
        att = db.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == emp.id,
            AttendanceRecord.work_date == today
        ).first()

        if d_status["is_weekly_off"]:
            weekly_off_count += 1
        elif d_status["is_holiday"]:
            pass
        elif att and att.check_in_time:
            present_count += 1
            if att.late_minutes > 0:
                late_count += 1
        else:
            # Check if on approved leave
            leave = db.query(LeaveRequest).filter(
                LeaveRequest.employee_id == emp.id,
                LeaveRequest.status == "approved",
                LeaveRequest.start_date <= today,
                LeaveRequest.end_date >= today
            ).first()
            if leave:
                on_leave_count += 1
            else:
                absent_count += 1

        # Lunch checks
        lunches = db.query(LunchRecord).filter(
            LunchRecord.employee_id == emp.id,
            LunchRecord.work_date == today
        ).all()
        for l in lunches:
            if l.late_minutes > 0:
                lunch_delays_count += 1
            if l.missing_lunch_in:
                missing_lunch_in_count += 1

        # Daily work submission
        works = db.query(DailyWorkEntry).filter(
            DailyWorkEntry.employee_id == emp.id,
            DailyWorkEntry.work_date == today,
            DailyWorkEntry.is_submitted == True
        ).count()
        if works > 0:
            work_submitted_count += 1

    pending_corrections = db.query(CorrectionRequest).filter(CorrectionRequest.status == "pending").count()
    pending_leaves = db.query(LeaveRequest).filter(LeaveRequest.status == "pending").count()

    return {
        "date": today,
        "total_employees": total_employees,
        "present_count": present_count,
        "late_count": late_count,
        "weekly_off_count": weekly_off_count,
        "on_leave_count": on_leave_count,
        "absent_count": absent_count,
        "lunch_delays_count": lunch_delays_count,
        "missing_punches_count": missing_lunch_in_count,
        "work_submitted_count": work_submitted_count,
        "pending_corrections_count": pending_corrections,
        "pending_leaves_count": pending_leaves,
        "pending_approvals_total": pending_corrections + pending_leaves
    }

@router.get("/daily")
def get_daily_report(
    target_date: Optional[date] = Query(None),
    employee_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    d_val = target_date or get_now_ist().date()
    
    # If specific employee requested
    target_emp_id = employee_id or current_user.id
    if current_user.role != "admin" and target_emp_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot access other employee's report")

    emp = db.query(Profile).filter(Profile.id == target_emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    return get_employee_daily_data(db, emp, d_val)

@router.get("/weekly")
def get_weekly_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    employee_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    now = get_now_ist().date()
    # Default to current week (Monday to Sunday)
    s_date = start_date or (now - timedelta(days=now.weekday()))
    e_date = end_date or (s_date + timedelta(days=6))

    target_emp_id = employee_id or current_user.id
    if current_user.role != "admin" and target_emp_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot access other employee's report")

    emp = db.query(Profile).filter(Profile.id == target_emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    return get_employee_range_data(db, emp, s_date, e_date)

@router.get("/download/excel")
def download_weekly_excel(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    employee_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    """
    Downloads Excel report for the employee.
    Used by employees to share their weekly activity report via WhatsApp!
    """
    now = get_now_ist().date()
    s_date = start_date or (now - timedelta(days=now.weekday()))
    e_date = end_date or (s_date + timedelta(days=6))

    target_emp_id = employee_id or current_user.id
    if current_user.role != "admin" and target_emp_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot download other employee's report")

    emp = db.query(Profile).filter(Profile.id == target_emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    stream = generate_weekly_excel_report(db, emp, s_date, e_date)
    filename = f"MB_Solar_Hub_Report_{emp.employee_id}_{s_date.strftime('%Y%m%d')}.xlsx"
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/download/pdf")
def download_pdf(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    employee_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    now = get_now_ist().date()
    s_date = start_date or (now - timedelta(days=now.weekday()))
    e_date = end_date or (s_date + timedelta(days=6))

    target_emp_id = employee_id or current_user.id
    if current_user.role != "admin" and target_emp_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot download other employee's report")

    emp = db.query(Profile).filter(Profile.id == target_emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    stream = generate_pdf_report(db, emp, s_date, e_date)
    filename = f"MB_Solar_Hub_Report_{emp.employee_id}_{s_date.strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        stream,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/trigger-digest")
def trigger_digest(
    report_type: str = Query("daily"),
    db: Session = Depends(get_db),
    current_user: Profile = Depends(require_admin)
):
    """Admin triggers scheduled email digest to Sir"""
    res = trigger_scheduled_management_report(db, report_type=report_type)
    return res
