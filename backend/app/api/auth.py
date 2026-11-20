from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.db.database import get_db
from app.core.security import create_access_token, get_current_user
from app.models.profile import Profile, Role
from app.models.schedule import EmployeeSchedule
from app.schemas.auth import LoginRequest, Token, UserProfile

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    # 1. Check if database has any profiles. If not, auto-bootstrap the default Admin (Sir) and sample employees!
    profile_count = db.query(Profile).count()
    if profile_count == 0:
        bootstrap_admin = Profile(
            employee_id="MB-ADMIN-01",
            full_name="Management Admin (Sir)",
            email="management@mbsolarhub.com",
            designation="Executive Director",
            role="admin",
            joining_date=date(2024, 1, 1),
            is_active=True
        )
        db.add(bootstrap_admin)

        sample_employee = Profile(
            employee_id="MB-001",
            full_name="Rajesh Sharma",
            email="rajesh@mbsolarhub.com",
            designation="Business Analyst",
            role="employee",
            joining_date=date(2024, 2, 1),
            is_active=True
        )
        db.add(sample_employee)
        db.commit()

        # Add initial schedules (Sunday off = 6)
        sched_admin = EmployeeSchedule(employee_id=bootstrap_admin.id, weekly_off_day=6, effective_from=date(2024, 1, 1))
        sched_emp = EmployeeSchedule(employee_id=sample_employee.id, weekly_off_day=6, effective_from=date(2024, 1, 1))
        db.add_all([sched_admin, sched_emp])
        db.commit()

    # Look up user by email
    user = db.query(Profile).filter(Profile.email == creds.email.lower()).first()
    if not user:
        # Check if login email matches demo admin or employee fallback
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Contact management."
        )

    # Generate JWT
    token_data = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "name": user.full_name
    }
    access_token = create_access_token(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserProfile)
def get_me(current_user: Profile = Depends(get_current_user)):
    return current_user
