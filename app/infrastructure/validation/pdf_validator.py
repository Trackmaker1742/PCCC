from fastapi import HTTPException
from app.infrastructure.validation.interface import IUploadValidator

class PdfFormatValidator(IUploadValidator):
    """
    Validates that the uploaded file is a PDF by checking its extension
    and verifying the standard %PDF magic header bytes.
    """
    
    def _check(self, filename: str, file_content: bytes, request_data: dict, tenant_id: str, db) -> None:
        # Check file extension
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF documents are supported for upload."
            )
            
        # Verify PDF header magic bytes (first 4 bytes must be b"%PDF")
        if len(file_content) < 4 or file_content[:4] != b"%PDF":
            raise HTTPException(
                status_code=400, 
                detail="Invalid file format. Uploaded file is not a valid PDF document."
            )
