import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, Date, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Role(Base):
    __tablename__ = "employee_roles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), unique=True, nullable=False, index=True) # 'admin', 'employee'
    description = Column(Text, nullable=True)

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid) # Maps to Supabase auth.users id or UUID
    employee_id = Column(String(50), unique=True, nullable=False, index=True) # e.g. MB-001
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    designation = Column(String(255), nullable=False) # e.g. Business Analyst (NO mandatory department field)
    role = Column(String(50), nullable=False, default="employee") # 'admin' or 'employee'
    joining_date = Column(Date, nullable=False, default=date.today)
    is_active = Column(Boolean, nullable=False, default=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    schedules = relationship("EmployeeSchedule", back_populates="employee", cascade="all, delete-orphan", foreign_keys="EmployeeSchedule.employee_id")
    schedule_overrides = relationship("ScheduleOverride", back_populates="employee", cascade="all, delete-orphan", foreign_keys="ScheduleOverride.employee_id")
    attendance_records = relationship("AttendanceRecord", back_populates="employee", cascade="all, delete-orphan", foreign_keys="AttendanceRecord.employee_id")
    leave_requests = relationship("LeaveRequest", back_populates="employee", cascade="all, delete-orphan", foreign_keys="LeaveRequest.employee_id")
    correction_requests = relationship("CorrectionRequest", back_populates="employee", cascade="all, delete-orphan", foreign_keys="CorrectionRequest.employee_id")
    daily_works = relationship("DailyWorkEntry", back_populates="employee", cascade="all, delete-orphan")

class AppSettings(Base):
    __tablename__ = "app_settings"

    key = Column(String(100), primary_key=True)
    value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
