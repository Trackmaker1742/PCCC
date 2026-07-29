from typing import List
from sqlalchemy.orm import Session
from app.infrastructure.audit.observer import IChangeLogObserver, AuditChangeLogObserver
from app.infrastructure.audit.event import DocumentChangeEvent

class ChangeLogPublisher:
    """
    Publisher class (Subject) managing observers and publishing change events.
    """
    
    def __init__(self):
        self._observers: List[IChangeLogObserver] = []

    def subscribe(self, observer: IChangeLogObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: IChangeLogObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def publish(self, event: DocumentChangeEvent, db: Session) -> None:
        for observer in self._observers:
            observer.on_document_changed(event, db)

# Instantiate global publisher singleton and register the DB audit observer
audit_publisher = ChangeLogPublisher()
audit_publisher.subscribe(AuditChangeLogObserver())
