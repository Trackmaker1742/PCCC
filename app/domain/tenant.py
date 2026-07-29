import uuid
from sqlalchemy import Column, String
from app.database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ten_co_quan = Column(String(255), nullable=False)
    ma_tenant = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Tenant(ma_tenant='{self.ma_tenant}', ten_co_quan='{self.ten_co_quan}')>"
