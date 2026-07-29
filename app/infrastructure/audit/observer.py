from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.infrastructure.audit.event import DocumentChangeEvent
from app.domain.changelog import ChangeLogEntry

class IChangeLogObserver(ABC):
    """
    Abstract observer interface for receiving document change notifications.
    """
    
    @abstractmethod
    def on_document_changed(self, event: DocumentChangeEvent, db: Session) -> None:
        """
        Called when a document state has changed.
        """
        pass

class AuditChangeLogObserver(IChangeLogObserver):
    """
    Concrete observer that captures document change events and records
    them in the SQLite changelogs database table.
    """
    
    def on_document_changed(self, event: DocumentChangeEvent, db: Session) -> None:
        # Create and persist a ChangeLogEntry
        log_entry = ChangeLogEntry(
            document_id=event.document_id,
            action=event.action,
            performed_by=event.performed_by,
            detail=event.detail
        )
        db.add(log_entry)
        db.commit()
        print(f"[AUDIT LOG] Document {event.document_id} had action '{event.action}' by User {event.performed_by}")
