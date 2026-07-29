from abc import ABC, abstractmethod
from typing import Optional

class IUploadValidator(ABC):
    """
    Base class for upload validators implementing the Chain of Responsibility pattern.
    Handles the linking of validators and traversal down the chain.
    """
    
    def __init__(self):
        self.next_validator: Optional[IUploadValidator] = None

    def set_next(self, validator: 'IUploadValidator') -> 'IUploadValidator':
        """
        Sets the next validator in the chain. 
        Returns the passed validator to enable chain-building: val1.set_next(val2).set_next(val3)
        """
        self.next_validator = validator
        return validator

    def validate(self, filename: str, file_content: bytes, request_data: dict, tenant_id: str, db) -> None:
        """
        Executes the current validator's check, and if successful, forwards to the next link.
        """
        self._check(filename, file_content, request_data, tenant_id, db)
        
        if self.next_validator:
            self.next_validator.validate(filename, file_content, request_data, tenant_id, db)

    @abstractmethod
    def _check(self, filename: str, file_content: bytes, request_data: dict, tenant_id: str, db) -> None:
        """
        Concrete check to be implemented by child validators.
        Should raise an HTTPException if validation fails.
        """
        pass
