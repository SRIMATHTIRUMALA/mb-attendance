import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Date, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    employee_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type = Column(String(50), nullable=False) # 'casual', 'sick', 'earned', 'unpaid', 'schedule_change'
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="pending", index=True) # 'pending', 'approved', 'rejected', 'cancelled'
    reviewed_by = Column(String(36), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    review_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = relationship("Profile", foreign_keys=[employee_id], back_populates="leave_requests")

class CorrectionRequest(Base):
    __tablename__ = "correction_requests"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    employee_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    attendance_id = Column(String(36), ForeignKey("attendance_records.id", ondelete="SET NULL"), nullable=True)
    # request_type: 'check_in', 'check_out', 'lunch_in', 'lunch_out', 'schedule_change'
    request_type = Column(String(50), nullable=False, index=True)
    target_date = Column(Date, nullable=False, index=True)
    requested_time = Column(DateTime, nullable=True)
    requested_off_day = Column(Integer, nullable=True) # If requesting schedule day change
    reason = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="pending", index=True) # 'pending', 'approved', 'rejected'
    reviewed_by = Column(String(36), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    review_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = relationship("Profile", foreign_keys=[employee_id], back_populates="correction_requests")
