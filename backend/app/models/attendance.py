import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, Date, DateTime, Integer, Numeric, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("employee_id", "work_date", name="uq_emp_work_date"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    employee_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    work_date = Column(Date, nullable=False, index=True)
    check_in_time = Column(DateTime, nullable=True)
    check_out_time = Column(DateTime, nullable=True)
    # status: 'present', 'late', 'absent', 'weekly_off', 'holiday', 'on_leave', 'pending_correction'
    status = Column(String(50), nullable=False, default="present", index=True)
    late_minutes = Column(Integer, nullable=False, default=0)
    work_hours = Column(Numeric(5, 2), nullable=True)
    check_in_mode = Column(String(50), nullable=False, default="normal") # 'normal', 'correction_approved', 'manual_admin'
    check_out_mode = Column(String(50), nullable=True, default="normal")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = relationship("Profile", foreign_keys=[employee_id], back_populates="attendance_records")
    lunch_records = relationship("LunchRecord", back_populates="attendance", cascade="all, delete-orphan")

class LunchRecord(Base):
    __tablename__ = "lunch_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    attendance_id = Column(String(36), ForeignKey("attendance_records.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    work_date = Column(Date, nullable=False, index=True)
    lunch_out_time = Column(DateTime, nullable=False)
    lunch_in_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    late_minutes = Column(Integer, nullable=False, default=0)
    missing_lunch_in = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    attendance = relationship("AttendanceRecord", back_populates="lunch_records")
