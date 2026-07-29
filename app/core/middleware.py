from fastapi import Header, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.domain.tenant import Tenant
from app.domain.user import User
from app.core.tenant_context import TenantContext

def set_tenant_context(
    x_tenant_id: str = Header(None, alias="X-Tenant-ID"),
    x_user_id: str = Header(None, alias="X-User-ID"),
    db: Session = Depends(get_db)
):
    """
    FastAPI dependency that extracts the active user and tenant from headers
    and updates the async-safe TenantContext.
    """
    # Reset context variables
    TenantContext.set_current_tenant(None)
    TenantContext.set_current_user(None)

    if x_user_id:
        user = db.query(User).filter(User.id == x_user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Simulated user not found")
        TenantContext.set_current_user(user)
        
        # Override tenant with user's tenant to ensure consistent data scoping
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=401, detail="Tenant associated with user not found")
        TenantContext.set_current_tenant(tenant)
        
    elif x_tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == x_tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=401, detail="Simulated tenant not found")
        TenantContext.set_current_tenant(tenant)
