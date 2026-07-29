from dataclasses import dataclass
from typing import Optional

@dataclass
class DocumentChangeEvent:
    """
    Data Transfer Object (DTO) capturing metadata about a document change event.
    Maps to DocumentChangeEvent in the design.
    """
    document_id: str
    action: str  # e.g., "CREATE", "UPDATE", "REPLACE", "STATUS_CHANGE"
    performed_by: Optional[str]
    detail: Optional[str] = None
