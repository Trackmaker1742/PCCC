from contextvars import ContextVar
from typing import Optional
from app.domain.tenant import Tenant
from app.domain.user import User

# Context variables for Tenant and User, isolated per async execution flow/request
_current_tenant: ContextVar[Optional[Tenant]] = ContextVar("current_tenant", default=None)
_current_user: ContextVar[Optional[User]] = ContextVar("current_user", default=None)

class TenantContext:
    """
    Ambient Context (Singleton) mapping to the multi-tenant context in the design.
    Uses ContextVar instead of ThreadLocal to be fully compatible with async request loops.
    """
    
    @staticmethod
    def get_current_tenant() -> Optional[Tenant]:
        return _current_tenant.get()

    @staticmethod
    def set_current_tenant(tenant: Optional[Tenant]) -> None:
        _current_tenant.set(tenant)

    @staticmethod
    def get_current_user() -> Optional[User]:
        return _current_user.get()

    @staticmethod
    def set_current_user(user: Optional[User]) -> None:
        _current_user.set(user)
