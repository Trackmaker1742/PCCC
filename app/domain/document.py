import enum
import uuid
from sqlalchemy import Column, String, Date, Integer, ForeignKey, Enum
from app.database import Base

class DocumentStatus(str, enum.Enum):
    CHO_XU_LY_NOI_DUNG = "CHO_XU_LY_NOI_DUNG"
    HIEU_LUC = "HIEU_LUC"
    HET_HIEU_LUC = "HET_HIEU_LUC"
    BI_THAY_THE = "BI_THAY_THE"

class RegulatoryDocument(Base):
    __tablename__ = "regulatory_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ma_hieu = Column(String(100), nullable=False)
    ten_day_du = Column(String(500), nullable=False)
    co_quan_ban_hanh = Column(String(255), nullable=False)
    ngay_ban_hanh = Column(Date, nullable=True)
    ngay_hieu_luc = Column(Date, nullable=True)
    trang_thai = Column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.CHO_XU_LY_NOI_DUNG)
    file_url = Column(String(1024), nullable=True)
    file_checksum = Column(String(64), nullable=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    version = Column(Integer, nullable=False, default=1)

    def update_metadata(self, dto_data: dict):
        """Updates the metadata fields from a dictionary/DTO."""
        for field in ["ma_hieu", "ten_day_du", "co_quan_ban_hanh", "ngay_ban_hanh", "ngay_hieu_luc"]:
            if field in dto_data and dto_data[field] is not None:
                setattr(self, field, dto_data[field])

    def mark_as_superseded(self, new_doc_id: str = None):
        """Marks this document as superseded (replaced) by another document."""
        self.trang_thai = DocumentStatus.BI_THAY_THE

    def attach_file(self, file_url: str, checksum: str):
        """Attaches a file URL and its checksum to this document."""
        self.file_url = file_url
        self.file_checksum = checksum

    def __repr__(self):
        return f"<RegulatoryDocument(ma_hieu='{self.ma_hieu}', version={self.version}, trang_thai='{self.trang_thai}')>"
