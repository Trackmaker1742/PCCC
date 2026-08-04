// ============================================================
// Document Catalog Module
// ============================================================
import type { Document, DocumentStatus } from './types';
import { currentUser, getHeaders } from './state';
import { fetchDocuments, updateDocumentStatus } from './api';
import { parseInputDate, formatDate } from './utils/dates';
import { escapeHtml } from './utils/html';
import { showToast } from './toast';
import { fetchAndRenderAudits } from './audit';
import { openReplaceModal } from './modal';

const catalogList    = document.getElementById('catalogList')!;
const supersedeSelect = document.getElementById('supersedeSelect') as HTMLSelectElement;

// ---- Filters ----------------------------------------------------------------

export function resetFilters(): void {
  (document.getElementById('filterCode') as HTMLInputElement).value = '';
  (document.getElementById('filterStatus') as HTMLSelectElement).value = '';
  (document.getElementById('filterStartDate') as HTMLInputElement).value = '';
  (document.getElementById('filterEndDate') as HTMLInputElement).value = '';
  void fetchAndRenderCatalog();
}

export function onFilterDateInput(): void {
  const startVal = (document.getElementById('filterStartDate') as HTMLInputElement).value;
  const endVal   = (document.getElementById('filterEndDate') as HTMLInputElement).value;
  const isStartOk = !startVal || startVal.length === 10;
  const isEndOk   = !endVal   || endVal.length === 10;
  if (isStartOk && isEndOk) void fetchAndRenderCatalog();
}

// ---- Fetch & Render ---------------------------------------------------------

export async function fetchAndRenderCatalog(): Promise<void> {
  const codeVal   = (document.getElementById('filterCode') as HTMLInputElement).value;
  const statusVal = (document.getElementById('filterStatus') as HTMLSelectElement).value;
  const startVal  = (document.getElementById('filterStartDate') as HTMLInputElement).value;
  const endVal    = (document.getElementById('filterEndDate') as HTMLInputElement).value;

  try {
    const docs = await fetchDocuments(getHeaders(), {
      ma_hieu:   codeVal   || undefined,
      trang_thai: statusVal || undefined,
      tu_ngay:   parseInputDate(startVal) || undefined,
      den_ngay:  parseInputDate(endVal)   || undefined,
    });
    renderCatalog(docs);
    populateSupersedeDropdown(docs);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Lỗi không xác định.';
    catalogList.innerHTML = `<div class="empty-state"><i class="fa-solid fa-triangle-exclamation" style="color: var(--status-expired);"></i><p>${message}</p></div>`;
  }
}

function populateSupersedeDropdown(docs: Document[]): void {
  const activeDocs = docs.filter((d) => d.trang_thai === 'HIEU_LUC');
  supersedeSelect.innerHTML =
    '<option value="">-- Không (Văn bản mới) --</option>' +
    activeDocs
      .map(
        (d) =>
          `<option value="${d.id}">${d.ma_hieu} v${d.version} - ${d.ten_day_du.substring(0, 45)}...</option>`
      )
      .join('');
}

function getStatusInfo(status: DocumentStatus): { cls: string; label: string } {
  switch (status) {
    case 'HIEU_LUC':          return { cls: 'active',     label: 'Đang có hiệu lực' };
    case 'HET_HIEU_LUC':      return { cls: 'expired',    label: 'Hết hiệu lực' };
    case 'BI_THAY_THE':       return { cls: 'superseded', label: 'Bị thay thế' };
    case 'CHO_XU_LY_NOI_DUNG':
    default:                  return { cls: 'pending',    label: 'Chờ xử lý nội dung' };
  }
}

function renderCatalog(docs: Document[]): void {
  if (!docs || docs.length === 0) {
    catalogList.innerHTML = `
      <div class="empty-state">
        <i class="fa-regular fa-folder-open"></i>
        <p>Không tìm thấy văn bản quy phạm nào trong danh mục cơ quan này.</p>
      </div>`;
    return;
  }

  const isInspector = currentUser?.vai_tro === 'THAM_TRA_VIEN' || currentUser?.vai_tro === 'ADMIN';
  const isApprover  = currentUser?.vai_tro === 'CHUYEN_GIA_PHE_DUYET' || currentUser?.vai_tro === 'ADMIN';

  catalogList.innerHTML = docs
    .map((doc, idx) => {
      const { cls, label } = getStatusInfo(doc.trang_thai);

      const fileSection = doc.file_url
        ? `<div class="file-section">
             <a href="${doc.file_url}" target="_blank" class="file-link">
               <i class="fa-solid fa-file-pdf" style="font-size: 1.1rem;"></i>
               <span>Tải File PDF Nguồn</span>
             </a>
             <span class="checksum-info" title="Mã SHA-256: ${doc.file_checksum}">
               <i class="fa-solid fa-fingerprint"></i>
               ${doc.file_checksum.substring(0, 10)}...
             </span>
           </div>`
        : `<div class="file-section" style="color: var(--status-expired);">
             <span><i class="fa-solid fa-triangle-exclamation"></i> Chưa đính kèm file PDF</span>
           </div>`;

      const replaceBtn =
        isInspector && doc.trang_thai !== 'BI_THAY_THE'
          ? `<button class="btn btn-secondary btn-sm" data-action="replace" data-id="${doc.id}" data-code="${escapeHtml(doc.ma_hieu)}">
               <i class="fa-solid fa-file-signature"></i> Thay thế PDF
             </button>`
          : '';

      const approveBtn =
        isApprover && doc.trang_thai === 'CHO_XU_LY_NOI_DUNG'
          ? `<button class="btn btn-primary btn-sm" style="background: var(--status-active); box-shadow: none;" data-action="approve" data-id="${doc.id}">
               <i class="fa-solid fa-circle-check"></i> Phê duyệt
             </button>`
          : '';

      const archiveBtn =
        isApprover && doc.trang_thai === 'HIEU_LUC'
          ? `<button class="btn btn-secondary btn-sm" style="color: var(--status-expired); border-color: var(--status-border-expired);" data-action="archive" data-id="${doc.id}">
               <i class="fa-solid fa-box-archive"></i> Lưu trữ / Thu hồi
             </button>`
          : '';

      return `
        <div class="doc-card" style="animation-delay: ${idx * 0.05}s">
          <div class="doc-header">
            <div class="doc-title-sec">
              <span class="doc-code">${escapeHtml(doc.ma_hieu)}
                <span style="color: var(--text-muted); font-weight: normal; margin-left: 0.5rem;">Phiên bản ${doc.version}</span>
              </span>
              <h3 class="doc-title">${escapeHtml(doc.ten_day_du)}</h3>
            </div>
            <span class="status-badge ${cls}">${label}</span>
          </div>

          <div class="doc-meta-grid">
            <div class="meta-item">
              <span class="meta-label">Cơ quan ban hành</span>
              <span class="meta-val">${escapeHtml(doc.co_quan_ban_hanh)}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Ngày ban hành</span>
              <span class="meta-val">${formatDate(doc.ngay_ban_hanh)}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Ngày có hiệu lực</span>
              <span class="meta-val">${formatDate(doc.ngay_hieu_luc)}</span>
            </div>
          </div>

          ${fileSection}

          <div class="card-actions">
            ${replaceBtn}${approveBtn}${archiveBtn}
          </div>
        </div>`;
    })
    .join('');

  // Delegate click events on the rendered cards
  catalogList.addEventListener('click', handleCardAction);
}

async function handleCardAction(e: Event): Promise<void> {
  const target = (e.target as HTMLElement).closest<HTMLButtonElement>('[data-action]');
  if (!target) return;

  const action = target.dataset['action'];
  const docId  = target.dataset['id'] ?? '';

  if (action === 'replace') {
    openReplaceModal(docId, target.dataset['code'] ?? '');
  } else if (action === 'approve') {
    await changeStatus(docId, 'HIEU_LUC');
  } else if (action === 'archive') {
    await changeStatus(docId, 'HET_HIEU_LUC');
  }
}

async function changeStatus(docId: string, status: DocumentStatus): Promise<void> {
  try {
    await updateDocumentStatus(getHeaders(), docId, status);
    showToast('Đã chuyển trạng thái văn bản thành công.');
    await fetchAndRenderCatalog();
    await fetchAndRenderAudits();
  } catch (err) {
    showToast(err instanceof Error ? err.message : 'Lỗi không xác định.', 'error');
  }
}

// ---- Context ----------------------------------------------------------------

export function updateFormVisibility(): void {
  const uploadBtn = document.getElementById('uploadSubmitBtn') as HTMLButtonElement | null;
  if (!uploadBtn) return;

  const isInspector = currentUser?.vai_tro === 'THAM_TRA_VIEN' || currentUser?.vai_tro === 'ADMIN';
  uploadBtn.disabled = !isInspector;
  const span = uploadBtn.querySelector('span');
  if (span) {
    span.textContent = isInspector ? 'Nạp Văn Bản' : 'Vô Hiệu Hóa (Chỉ Thẩm Tra Viên)';
  }
}
