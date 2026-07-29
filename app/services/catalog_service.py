from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.persistence.document_repository import DocumentRepositoryImpl
from app.core.security import AccessControlService
from app.core.tenant_context import TenantContext
from app.domain.document import RegulatoryDocument, DocumentStatus
from app.infrastructure.audit.publisher import audit_publisher
from app.infrastructure.audit.event import DocumentChangeEvent

class DocumentCatalogService:
    """
    Service responsible for querying and managing metadata of regulatory documents (UC-A0-01).
    Enforces active tenant-scoping and user permissions.
    """
    
    def __init__(self):
        self.repo = DocumentRepositoryImpl()
        self.access_control = AccessControlService()
        self.publisher = audit_publisher

    def list_documents(self, criteria: dict, db: Session):
        """
        Lists documents based on current filters and active tenant context.
        Requires 'VIEW_CATALOG' permissions.
        """
        user = TenantContext.get_current_user()
        self.access_control.require_permission(user, "VIEW_CATALOG")
        return self.repo.find_all(criteria, db)

    def create_document(self, dto: dict, db: Session) -> RegulatoryDocument:
        """
        Registers a document's metadata (without an immediate file upload).
        Requires 'CREATE_DOCUMENT' permissions.
        """
        user = TenantContext.get_current_user()
        self.access_control.require_permission(user, "CREATE_DOCUMENT")
        tenant = TenantContext.get_current_tenant()
        
        doc = RegulatoryDocument(
            ma_hieu=dto["ma_hieu"],
            ten_day_du=dto["ten_day_du"],
            co_quan_ban_hanh=dto["co_quan_ban_hanh"],
            ngay_ban_hanh=dto["ngay_ban_hanh"],
            ngay_hieu_luc=dto["ngay_hieu_luc"],
            trang_thai=DocumentStatus.CHO_XU_LY_NOI_DUNG,
            tenant_id=tenant.id,
            version=1
        )
        
        saved_doc = self.repo.save(doc, db)
        
        # Publish creation audit event
        self.publisher.publish(
            DocumentChangeEvent(
                document_id=saved_doc.id,
                action="CREATE",
                performed_by=user.id,
                detail=f"Created metadata record. Code: {saved_doc.ma_hieu}"
            ),
            db
        )
        return saved_doc

    def update_metadata(self, doc_id: str, dto: dict, db: Session) -> RegulatoryDocument:
        """
        Updates document metadata. Requires 'CREATE_DOCUMENT' permissions.
        """
        user = TenantContext.get_current_user()
        self.access_control.require_permission(user, "CREATE_DOCUMENT")
        
        doc = self.repo.find_by_id(doc_id, db)
        if not doc:
            raise HTTPException(status_code=404, detail="Không tìm thấy văn bản quy phạm pháp luật")
            
        doc.update_metadata(dto)
        saved_doc = self.repo.save(doc, db)
        
        # Publish edit audit event
        self.publisher.publish(
            DocumentChangeEvent(
                document_id=saved_doc.id,
                action="UPDATE",
                performed_by=user.id,
                detail=f"Updated metadata fields. Code: {saved_doc.ma_hieu}"
            ),
            db
        )
        return saved_doc

    def change_status(self, doc_id: str, status: DocumentStatus, db: Session) -> None:
        """
        Promotes/updates a document status (e.g. approving/expiring a document).
        Requires 'CHANGE_STATUS' permissions.
        """
        user = TenantContext.get_current_user()
        self.access_control.require_permission(user, "CHANGE_STATUS")
        
        doc = self.repo.find_by_id(doc_id, db)
        if not doc:
            raise HTTPException(status_code=404, detail="Không tìm thấy văn bản quy phạm pháp luật")
            
        old_status = doc.trang_thai
        doc.trang_thai = status
        self.repo.save(doc, db)
        
        # Publish status change event
        self.publisher.publish(
            DocumentChangeEvent(
                document_id=doc.id,
                action="STATUS_CHANGE",
                performed_by=user.id,
                detail=f"Thay đổi trạng thái từ '{old_status.value}' sang '{status.value}'"
            ),
            db
        )
