import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, Date, DateTime, Integer, Text, ForeignKey, JSON
from app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class ReportHistory(Base):
    __tablename__ = "report_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_type = Column(String(50), nullable=False, index=True) # 'daily', 'weekly', 'monthly'
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    employee_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    file_format = Column(String(10), nullable=False) # 'xlsx', 'pdf'
    file_path = Column(Text, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default="generated") # 'generated', 'failed'
    has_unresolved_corrections = Column(Boolean, nullable=False, default=False)
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class ReportDeliveryLog(Base):
    __tablename__ = "report_delivery_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_history_id = Column(String(36), ForeignKey("report_history.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_email = Column(String(255), nullable=False, index=True)
    recipient_name = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="pending", index=True) # 'pending', 'sent', 'failed', 'retrying'
    attempts = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    actor_id = Column(String(36), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    target_entity = Column(String(100), nullable=False, index=True)
    target_id = Column(String(100), nullable=True)
    changes = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
