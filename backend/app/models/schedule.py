import uuid
from datetime import datetime, date, time
from sqlalchemy import Column, String, Boolean, Date, DateTime, Time, Text, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Shift(Base):
    __tablename__ = "shifts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, default="Standard Shift")
    start_time = Column(Time, nullable=False, default=time(9, 0))
    end_time = Column(Time, nullable=False, default=time(18, 0))
    check_in_start = Column(Time, nullable=False, default=time(8, 45))
    check_in_end = Column(Time, nullable=False, default=time(10, 0))
    check_out_start = Column(Time, nullable=False, default=time(18, 0))
    check_out_end = Column(Time, nullable=False, default=time(19, 0))
    lunch_start = Column(Time, nullable=False, default=time(13, 0))
    lunch_end = Column(Time, nullable=False, default=time(14, 0))
    is_default = Column(Boolean, nullable=False, default=True)

class EmployeeSchedule(Base):
    __tablename__ = "employee_schedules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    employee_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    # 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
    weekly_off_day = Column(Integer, nullable=False, default=6) # 6=Sunday by default, but completely flexible
    effective_from = Column(Date, nullable=False, default=date.today)
    effective_to = Column(Date, nullable=True) # None = active ongoing
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String(36), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)

    employee = relationship("Profile", foreign_keys=[employee_id], back_populates="schedules")

class ScheduleOverride(Base):
    __tablename__ = "schedule_overrides"
    __table_args__ = (
        UniqueConstraint("employee_id", "override_date", name="uq_emp_override_date"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    employee_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    override_date = Column(Date, nullable=False, index=True)
    is_working_day = Column(Boolean, nullable=False) # True = scheduled to work; False = weekly off override
    reason = Column(Text, nullable=True)
    approved_by = Column(String(36), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    employee = relationship("Profile", foreign_keys=[employee_id], back_populates="schedule_overrides")

class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    holiday_date = Column(Date, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
