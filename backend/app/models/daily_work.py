import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, Date, DateTime, Time, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class DailyWorkEntry(Base):
    __tablename__ = "daily_work_entries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    employee_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    work_date = Column(Date, nullable=False, index=True)
    work_description = Column(Text, nullable=False)
    work_details = Column(Text, nullable=True) # Optional feedback / metrics (e.g. 24 calls made, 7 interested...)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    is_submitted = Column(Boolean, nullable=False, default=False)
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = relationship("Profile", back_populates="daily_works")
