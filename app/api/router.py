from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.middleware import set_tenant_context
from app.core.tenant_context import TenantContext
from app.domain.tenant import Tenant
from app.domain.user import User
from app.domain.document import DocumentStatus
from app.domain.changelog import ChangeLogEntry
from app.services.catalog_service import DocumentCatalogService
from app.services.upload_service import DocumentUploadService

# Expose the API router, setting set_tenant_context to run for every endpoint
router = APIRouter(prefix="/api", dependencies=[Depends(set_tenant_context)])

catalog_service = DocumentCatalogService()
upload_service = DocumentUploadService()

@router.get("/tenants")
def get_tenants(db: Session = Depends(get_db)):
    """
    Simulated helper: Lists all tenants so the frontend dashboard
    can switch environments dynamically.
    """
    return db.query(Tenant).all()

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    """
    Simulated helper: Lists all mock users so the frontend can
    simulate different credentials and role profiles.
    """
    return db.query(User).all()

@router.get("/documents")
def list_documents(
    ma_hieu: Optional[str] = None,
    trang_thai: Optional[DocumentStatus] = None,
    tu_ngay: Optional[date] = None,
    den_ngay: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Lists and filters documents for the active tenant context.
    """
    criteria = {
        "ma_hieu": ma_hieu,
        "trang_thai": trang_thai,
        "tu_ngay": tu_ngay,
        "den_ngay": den_ngay
    }
    return catalog_service.list_documents(criteria, db)

@router.post("/documents/upload")
async def upload_document(
    ma_hieu: str = Form(...),
    ten_day_du: str = Form(...),
    co_quan_ban_hanh: str = Form(...),
    ngay_ban_hanh: date = Form(...),
    ngay_hieu_luc: date = Form(...),
    replaces_document_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Registers metadata and stores the uploaded PDF source document.
    Handles Chain of Responsibility validation, storage strategy,
    versioning, and supersession links.
    """
    file_content = await file.read()
    metadata = {
        "ma_hieu": ma_hieu,
        "ten_day_du": ten_day_du,
        "co_quan_ban_hanh": co_quan_ban_hanh,
        "ngay_ban_hanh": ngay_ban_hanh,
        "ngay_hieu_luc": ngay_hieu_luc,
        "replaces_document_id": replaces_document_id
    }
    return await upload_service.upload_new_document(
        filename=file.filename,
        file_content=file_content,
        metadata=metadata,
        db=db
    )

@router.put("/documents/{doc_id}/replace")
async def replace_document(
    doc_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Replaces the physical PDF attachment of an existing document.
    Increments the version counter and resets review status.
    """
    file_content = await file.read()
    return await upload_service.replace_document_file(
        doc_id=doc_id,
        filename=file.filename,
        file_content=file_content,
        db=db
    )

@router.put("/documents/{doc_id}/status")
def change_document_status(
    doc_id: str,
    status: DocumentStatus,
    db: Session = Depends(get_db)
):
    """
    Transitions document state (e.g. approving a document).
    Requires Approver/Admin rights.
    """
    catalog_service.change_status(doc_id, status, db)
    return {"message": f"Document status changed to {status.value} successfully."}

@router.get("/audit-logs")
def get_audit_logs(
    document_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Fetches the history of audit trails (Observer logs) for the active tenant.
    """
    tenant = TenantContext.get_current_tenant()
    if not tenant:
        raise HTTPException(status_code=401, detail="Active tenant context is missing.")
        
    from app.domain.document import RegulatoryDocument
    
    # Query changelogs, joining document to restrict queries strictly to active tenant's documents
    query = db.query(ChangeLogEntry).join(
        RegulatoryDocument, 
        ChangeLogEntry.document_id == RegulatoryDocument.id
    ).filter(RegulatoryDocument.tenant_id == tenant.id)
    
    if document_id:
        query = query.filter(ChangeLogEntry.document_id == document_id)
        
    return query.order_by(ChangeLogEntry.performed_at.desc()).all()
