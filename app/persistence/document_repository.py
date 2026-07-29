from typing import List, Optional
from sqlalchemy.orm import Session
from app.persistence.repository_interface import IDocumentRepository
from app.domain.document import RegulatoryDocument
from app.core.tenant_context import TenantContext

class DocumentRepositoryImpl(IDocumentRepository):
    """
    SQLAlchemy implementation of the IDocumentRepository.
    Enforces multi-tenant query isolation by reading from TenantContext.
    """
    
    def save(self, doc: RegulatoryDocument, db: Session) -> RegulatoryDocument:
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    def find_by_id(self, doc_id: str, db: Session) -> Optional[RegulatoryDocument]:
        tenant = TenantContext.get_current_tenant()
        if not tenant:
            return None
            
        # Scope lookup by active tenant
        return db.query(RegulatoryDocument).filter(
            RegulatoryDocument.id == doc_id,
            RegulatoryDocument.tenant_id == tenant.id
        ).first()

    def find_by_code(self, ma_hieu: str, tenant_id: str, db: Session) -> Optional[RegulatoryDocument]:
        # Scoped explicitly by the provided tenant_id parameter for validator use-cases
        return db.query(RegulatoryDocument).filter(
            RegulatoryDocument.ma_hieu == ma_hieu,
            RegulatoryDocument.tenant_id == tenant_id
        ).first()

    def find_all(self, criteria: dict, db: Session) -> List[RegulatoryDocument]:
        tenant = TenantContext.get_current_tenant()
        if not tenant:
            return []
            
        # Initialize tenant-scoped query
        query = db.query(RegulatoryDocument).filter(
            RegulatoryDocument.tenant_id == tenant.id
        )
        
        # Apply filters
        if criteria.get("ma_hieu"):
            query = query.filter(RegulatoryDocument.ma_hieu.ilike(f"%{criteria['ma_hieu']}%"))
            
        if criteria.get("trang_thai"):
            query = query.filter(RegulatoryDocument.trang_thai == criteria["trang_thai"])
            
        if criteria.get("tu_ngay"):
            query = query.filter(RegulatoryDocument.ngay_ban_hanh >= criteria["tu_ngay"])
            
        if criteria.get("den_ngay"):
            query = query.filter(RegulatoryDocument.ngay_ban_hanh <= criteria["den_ngay"])

        # Order by release date desc
        return query.order_by(RegulatoryDocument.ngay_ban_hanh.desc()).all()
