from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.document import RegulatoryDocument

class IDocumentRepository(ABC):
    """
    Interface for regulatory document repository operations (Repository Pattern).
    Defines the contract for reading and writing document entities.
    """
    
    @abstractmethod
    def save(self, doc: RegulatoryDocument, db) -> RegulatoryDocument:
        """
        Persists or updates a document.
        """
        pass

    @abstractmethod
    def find_by_id(self, doc_id: str, db) -> Optional[RegulatoryDocument]:
        """
        Finds a document by ID.
        """
        pass

    @abstractmethod
    def find_by_code(self, ma_hieu: str, tenant_id: str, db) -> Optional[RegulatoryDocument]:
        """
        Finds a document by its official code under a specific tenant.
        """
        pass

    @abstractmethod
    def find_all(self, criteria: dict, db) -> List[RegulatoryDocument]:
        """
        Searches all documents matching filter criteria.
        """
        pass
