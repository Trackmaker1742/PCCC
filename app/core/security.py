from fastapi import HTTPException
from app.domain.user import User, Role

class AccessControlService:
    """
    AccessControlService checks user permissions based on their role.
    - ADMIN: Full access to all actions.
    - THAM_TRA_VIEN (Inspector): Can create and replace documents.
    - CHUYEN_GIA_PHE_DUYET (Approver): Can approve and change document statuses.
    """
    
    @staticmethod
    def check_permission(user: User, action: str) -> bool:
        if not user:
            return False
            
        role = user.vai_tro
        
        # ADMIN inherits all permissions
        if role == Role.ADMIN:
            return True

        if action == "VIEW_CATALOG":
            return role in [Role.THAM_TRA_VIEN, Role.CHUYEN_GIA_PHE_DUYET]
            
        if action in ["CREATE_DOCUMENT", "REPLACE_DOCUMENT"]:
            return role == Role.THAM_TRA_VIEN

        if action in ["CHANGE_STATUS", "APPROVE_DOCUMENT"]:
            return role == Role.CHUYEN_GIA_PHE_DUYET

        return False

    @classmethod
    def require_permission(cls, user: User, action: str):
        """
        Helper that raises an HTTP 403 Forbidden error if permissions are insufficient.
        """
        if not cls.check_permission(user, action):
            raise HTTPException(
                status_code=403, 
                detail=f"Access Denied: Role '{user.vai_tro.value if user else 'None'}' does not have permission to run '{action}'"
            )
