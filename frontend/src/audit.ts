// ============================================================
// Audit Log Module
// ============================================================
import type { AuditLog, AuditAction } from './types';
import { mockUsers, getHeaders } from './state';
import { fetchAuditLogs } from './api';
import { formatDateTime } from './utils/dates';
import { escapeHtml } from './utils/html';

const auditList = document.getElementById('auditList')!;

interface ActionMeta { cls: string; label: string }

function getActionMeta(action: AuditAction): ActionMeta {
  switch (action) {
    case 'CREATE':        return { cls: 'create',        label: 'Tạo mới' };
    case 'UPDATE':        return { cls: 'update',        label: 'Cập nhật' };
    case 'REPLACE':       return { cls: 'replace',       label: 'Thay thế' };
    case 'STATUS_CHANGE': return { cls: 'status_change', label: 'Trạng thái' };
    default:              return { cls: 'create',        label: action };
  }
}

function renderAudits(logs: AuditLog[]): void {
  if (!logs || logs.length === 0) {
    auditList.innerHTML =
      '<div style="color: var(--text-muted); font-size: 0.85rem; text-align: center; padding: 2rem 0;"><i class="fa-regular fa-clock" style="margin-right: 0.25rem;"></i> Chưa ghi nhận hành động nào tại cơ quan này.</div>';
    return;
  }

  auditList.innerHTML = logs
    .map((log) => {
      const { cls, label } = getActionMeta(log.action);
      const performer = mockUsers.find((u) => u.id === log.performed_by);
      const performerName = performer ? performer.ho_ten : 'Hệ thống';

      return `
        <div class="audit-item">
          <div class="audit-header">
            <span class="action-tag ${cls}">${label}</span>
            <span>${formatDateTime(log.performed_at)}</span>
          </div>
          <p style="font-weight: 500;">Người thực hiện: <span style="color: var(--accent-primary);">${performerName}</span></p>
          <p style="color: var(--text-secondary); font-size: 0.8rem; line-height: 1.3;">${escapeHtml(log.detail)}</p>
        </div>`;
    })
    .join('');
}

export async function fetchAndRenderAudits(): Promise<void> {
  try {
    const logs = await fetchAuditLogs(getHeaders());
    renderAudits(logs);
  } catch {
    auditList.innerHTML =
      '<div style="color: var(--text-muted); font-size: 0.8rem; text-align: center; padding: 2rem 0;">Tải nhật ký hoạt động thất bại.</div>';
  }
}
