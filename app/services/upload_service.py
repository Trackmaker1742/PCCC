import hashlib
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.persistence.document_repository import DocumentRepositoryImpl
from app.infrastructure.validation.pdf_validator import PdfFormatValidator
from app.infrastructure.validation.code_validator import DuplicateCodeValidator
from app.infrastructure.storage.storage_factory import FileStorageFactory
from app.core.security import AccessControlService
from app.core.tenant_context import TenantContext
from app.domain.document import RegulatoryDocument, DocumentStatus
from app.infrastructure.audit.publisher import audit_publisher
from app.infrastructure.audit.event import DocumentChangeEvent

class DocumentUploadService:
    """
    Service managing upload, storage, replacement, and validation of 
    regulatory document source files (UC-A0-02).
    """
    
    def __init__(self):
        self.repo = DocumentRepositoryImpl()
        
        # Build validation chain (Chain of Responsibility)
        self.validator_chain = PdfFormatValidator()
        self.validator_chain.set_next(DuplicateCodeValidator())
        
        self.storage_factory = FileStorageFactory()
        self.access_control = AccessControlService()
        self.publisher = audit_publisher

    async def upload_new_document(
        self, 
        filename: str, 
        file_content: bytes, 
        metadata: dict, 
        db: Session
    ) -> RegulatoryDocument:
        """
        Validates, stores, and registers a brand new document PDF upload.
        Optionally links to and deprecates an old document if this supersedes one.
        Requires 'CREATE_DOCUMENT' permissions.
        """
        user = TenantContext.get_current_user()
        self.access_control.require_permission(user, "CREATE_DOCUMENT")
        tenant = TenantContext.get_current_tenant()
        
        # 1. Run complete validator chain
        self.validator_chain.validate(filename, file_content, metadata, tenant.id, db)
        
        # 2. Store file via tenant strategy
        storage_strategy = self.storage_factory.get_strategy(tenant.id)
        file_url = storage_strategy.store(file_content, filename, tenant.id)
        
        # 3. Calculate SHA-256 Checksum
        checksum = hashlib.sha256(file_content).hexdigest()
        
        # 4. Construct record
        doc = RegulatoryDocument(
            ma_hieu=metadata["ma_hieu"],
            ten_day_du=metadata["ten_day_du"],
            co_quan_ban_hanh=metadata["co_quan_ban_hanh"],
            ngay_ban_hanh=metadata["ngay_ban_hanh"],
            ngay_hieu_luc=metadata["ngay_hieu_luc"],
            trang_thai=DocumentStatus.CHO_XU_LY_NOI_DUNG,
            file_url=file_url,
            file_checksum=checksum,
            tenant_id=tenant.id,
            version=1
        )
        
        # 5. Handle supersession link if replacing an existing document
        replaces_id = metadata.get("replaces_document_id")
        if replaces_id:
            old_doc = self.repo.find_by_id(replaces_id, db)
            if old_doc:
                # Deprecate the old document
                old_doc.mark_as_superseded(doc.id)
                self.repo.save(old_doc, db)
                
                # Log old document deprecation
                self.publisher.publish(
                    DocumentChangeEvent(
                        document_id=old_doc.id,
                        action="STATUS_CHANGE",
                        performed_by=user.id,
                        detail=f"Marked as BI_THAY_THE. Superseded by code '{doc.ma_hieu}'"
                    ),
                    db
                )
        
        saved_doc = self.repo.save(doc, db)
        
        # 6. Publish audit event
        self.publisher.publish(
            DocumentChangeEvent(
                document_id=saved_doc.id,
                action="CREATE",
                performed_by=user.id,
                detail=f"Uploaded source document '{filename}' with code '{saved_doc.ma_hieu}'"
            ),
            db
        )
        return saved_doc

    async def replace_document_file(
        self, 
        doc_id: str, 
        filename: str, 
        file_content: bytes, 
        db: Session
    ) -> RegulatoryDocument:
        """
        Replaces the source PDF file of an existing document, increments its version,
        and resets its status for review.
        Requires 'REPLACE_DOCUMENT' permissions.
        """
        user = TenantContext.get_current_user()
        self.access_control.require_permission(user, "REPLACE_DOCUMENT")
        tenant = TenantContext.get_current_tenant()
        
        doc = self.repo.find_by_id(doc_id, db)
        if not doc:
            raise HTTPException(status_code=404, detail="Regulatory document not found")
            
        # 1. Run PDF format check only (skip duplicate code check since we replace the file of the same document)
        pdf_only_validator = PdfFormatValidator()
        pdf_only_validator.validate(filename, file_content, {}, tenant.id, db)
        
        # 2. Delete old file and store new file
        storage_strategy = self.storage_factory.get_strategy(tenant.id)
        if doc.file_url:
            storage_strategy.delete(doc.file_url)
            
        file_url = storage_strategy.store(file_content, filename, tenant.id)
        
        # 3. Calculate Checksum
        checksum = hashlib.sha256(file_content).hexdigest()
        
        # 4. Attach new file, increment version, and reset status to pending
        doc.attach_file(file_url, checksum)
        doc.version += 1
        doc.trang_thai = DocumentStatus.CHO_XU_LY_NOI_DUNG
        
        saved_doc = self.repo.save(doc, db)
        
        # 5. Publish replacement event
        self.publisher.publish(
            DocumentChangeEvent(
                document_id=saved_doc.id,
                action="REPLACE",
                performed_by=user.id,
                detail=f"Replaced source PDF with '{filename}'. Incremented version to {saved_doc.version}"
            ),
            db
        )
        return saved_doc
