from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.profile import Profile
from app.schemas.attendance import LunchOutRequest, LunchInRequest, LunchRecordResponse
from app.services.attendance_service import process_lunch_out, process_lunch_in

router = APIRouter(prefix="/lunch", tags=["Lunch Tracking"])

@router.post("/out", response_model=LunchRecordResponse)
def lunch_out(
    payload: LunchOutRequest = None,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    ts = payload.timestamp if payload else None
    notes = payload.notes if payload else None
    record = process_lunch_out(db, current_user, notes=notes, custom_time=ts)
    return record

@router.post("/in", response_model=LunchRecordResponse)
def lunch_in(
    payload: LunchInRequest = None,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    ts = payload.timestamp if payload else None
    record = process_lunch_in(db, current_user, custom_time=ts)
    return record
