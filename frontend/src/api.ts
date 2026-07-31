// ============================================================
// API Layer — all fetch calls in one place
// ============================================================
import type { Tenant, User, Document, AuditLog, DocumentStatus } from './types';

const BOOTSTRAP_HEADERS: Record<string, string> = {
  'X-User-ID': 'u1111111-1111-1111-1111-111111111111',
  'X-Tenant-ID': 't1111111-1111-1111-1111-111111111111',
};

export async function fetchTenants(): Promise<Tenant[]> {
  const res = await fetch('/api/tenants', { headers: BOOTSTRAP_HEADERS });
  if (!res.ok) throw new Error('Failed to fetch tenants');
  return res.json();
}

export async function fetchUsers(): Promise<User[]> {
  const res = await fetch('/api/users', { headers: BOOTSTRAP_HEADERS });
  if (!res.ok) throw new Error('Failed to fetch users');
  return res.json();
}

export async function fetchDocuments(
  headers: Record<string, string>,
  params: {
    ma_hieu?: string;
    trang_thai?: string;
    tu_ngay?: string;
    den_ngay?: string;
  }
): Promise<Document[]> {
  const query = new URLSearchParams();
  if (params.ma_hieu)   query.set('ma_hieu', params.ma_hieu);
  if (params.trang_thai) query.set('trang_thai', params.trang_thai);
  if (params.tu_ngay)   query.set('tu_ngay', params.tu_ngay);
  if (params.den_ngay)  query.set('den_ngay', params.den_ngay);

  const res = await fetch(`/api/documents?${query}`, { headers });
  if (!res.ok) throw new Error('Tải danh mục văn bản thất bại.');
  return res.json();
}

export async function fetchAuditLogs(headers: Record<string, string>): Promise<AuditLog[]> {
  const res = await fetch('/api/audit-logs', { headers });
  if (!res.ok) throw new Error('Failed to fetch audit logs');
  return res.json();
}

export async function uploadDocument(
  headers: Record<string, string>,
  formData: FormData
): Promise<Document> {
  const res = await fetch('/api/documents/upload', {
    method: 'POST',
    headers,
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail ?? 'Kiểm tra dữ liệu hoặc tải lên thất bại.');
  }
  return res.json();
}

export async function updateDocumentStatus(
  headers: Record<string, string>,
  docId: string,
  status: DocumentStatus
): Promise<void> {
  const res = await fetch(`/api/documents/${docId}/status?status=${status}`, {
    method: 'PUT',
    headers,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail ?? 'Chuyển trạng thái thất bại.');
  }
}

export async function replacePdf(
  headers: Record<string, string>,
  docId: string,
  formData: FormData
): Promise<void> {
  const res = await fetch(`/api/documents/${docId}/replace`, {
    method: 'PUT',
    headers,
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail ?? 'Thay thế file PDF thất bại.');
  }
}
