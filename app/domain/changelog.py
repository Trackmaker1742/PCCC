import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, String, DateTime, ForeignKey
from app.database import Base

def get_utc_plus_7():
    """
    Returns the naive current datetime adjusted to UTC+7 (Indochina Time).
    """
    return datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)

class ChangeLogEntry(Base):
    __tablename__ = "changelogs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("regulatory_documents.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False)  # e.g., CREATE, UPDATE, REPLACE, STATUS_CHANGE
    performed_by = Column(String(36), ForeignKey("users.id"), nullable=True)  # Mocked user ID performing action
    performed_at = Column(DateTime, nullable=False, default=get_utc_plus_7)
    detail = Column(String(1000), nullable=True)

    def __repr__(self):
        return f"<ChangeLogEntry(document_id='{self.document_id}', action='{self.action}', performed_by='{self.performed_by}')>"
