// ============================================================
// Domain Types
// ============================================================

export interface Tenant {
  id: string;
  ma_tenant: string;
  ten_co_quan: string;
}

export interface User {
  id: string;
  ho_ten: string;
  vai_tro: 'ADMIN' | 'THAM_TRA_VIEN' | 'CHUYEN_GIA_PHE_DUYET';
  tenant_id: string;
}

export type DocumentStatus =
  | 'CHO_XU_LY_NOI_DUNG'
  | 'HIEU_LUC'
  | 'HET_HIEU_LUC'
  | 'BI_THAY_THE';

export interface Document {
  id: string;
  ma_hieu: string;
  ten_day_du: string;
  co_quan_ban_hanh: string;
  ngay_ban_hanh: string;
  ngay_hieu_luc: string;
  trang_thai: DocumentStatus;
  version: number;
  file_url: string | null;
  file_checksum: string;
}

export type AuditAction = 'CREATE' | 'UPDATE' | 'REPLACE' | 'STATUS_CHANGE';

export interface AuditLog {
  id: string;
  action: AuditAction;
  performed_by: string;
  performed_at: string;
  detail: string;
}

export type ToastType = 'success' | 'error';
