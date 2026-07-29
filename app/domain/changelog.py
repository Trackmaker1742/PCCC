import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from app.database import Base

class ChangeLogEntry(Base):
    __tablename__ = "changelogs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("regulatory_documents.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False)  # e.g., CREATE, UPDATE, REPLACE, STATUS_CHANGE
    performed_by = Column(String(36), ForeignKey("users.id"), nullable=True)  # Mocked user ID performing action
    performed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    detail = Column(String(1000), nullable=True)

    def __repr__(self):
        return f"<ChangeLogEntry(document_id='{self.document_id}', action='{self.action}', performed_by='{self.performed_by}')>"
