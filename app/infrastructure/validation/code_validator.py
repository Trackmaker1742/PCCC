from fastapi import HTTPException
from app.infrastructure.validation.interface import IUploadValidator
from app.domain.document import RegulatoryDocument

class DuplicateCodeValidator(IUploadValidator):
    """
    Validates that the document code (ma_hieu) does not already exist 
    under the active tenant, ensuring data consistency.
    """
    
    def _check(self, filename: str, file_content: bytes, request_data: dict, tenant_id: str, db) -> None:
        ma_hieu = request_data.get("ma_hieu")
        replaces_id = request_data.get("replaces_document_id")

        if not ma_hieu:
            return

        # Query documents with the same code inside the current tenant
        query = db.query(RegulatoryDocument).filter(
            RegulatoryDocument.ma_hieu == ma_hieu,
            RegulatoryDocument.tenant_id == tenant_id
        )

        # Exclude the document currently being replaced if this is a replacement request
        if replaces_id:
            query = query.filter(RegulatoryDocument.id != replaces_id)

        existing = query.first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"A document with code '{ma_hieu}' already exists for this agency."
            )
