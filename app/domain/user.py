import enum
import uuid
from sqlalchemy import Column, String, ForeignKey, Enum
from app.database import Base

class Role(str, enum.Enum):
    THAM_TRA_VIEN = "THAM_TRA_VIEN"
    CHUYEN_GIA_PHE_DUYET = "CHUYEN_GIA_PHE_DUYET"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ho_ten = Column(String(255), nullable=False)
    vai_tro = Column(Enum(Role), nullable=False)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)

    def __repr__(self):
        return f"<User(ho_ten='{self.ho_ten}', vai_tro='{self.vai_tro}', tenant_id='{self.tenant_id}')>"
