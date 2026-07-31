// ============================================================
// Upload Form Module
// ============================================================
import { currentUser, activeTenant } from './state';
import { uploadDocument } from './api';
import { parseInputDate } from './utils/dates';
import { showToast } from './toast';
import { fetchAndRenderCatalog } from './catalog';
import { fetchAndRenderAudits } from './audit';

const docFileInput      = document.getElementById('docFileInput')      as HTMLInputElement;
const filePromptText    = document.getElementById('filePromptText')!;
const fileSelectedInfo  = document.getElementById('fileSelectedInfo')!;

function formatFileSize(bytes: number): string {
  return `${(bytes / 1024).toFixed(1)} KB`;
}

export function onFileSelected(): void {
  const file = docFileInput.files?.[0];
  if (file) {
    filePromptText.style.display = 'none';
    fileSelectedInfo.style.display = 'block';
    fileSelectedInfo.textContent = `Đã chọn: ${file.name} (${formatFileSize(file.size)})`;
  } else {
    filePromptText.style.display = 'block';
    fileSelectedInfo.style.display = 'none';
  }
}

export async function onUploadSubmitted(e: SubmitEvent): Promise<void> {
  e.preventDefault();
  if (!currentUser || !activeTenant) return;

  const file = docFileInput.files?.[0];
  if (!file) {
    showToast('Vui lòng chọn file PDF nguồn.', 'error');
    return;
  }

  const code      = (document.getElementById('docCode')          as HTMLInputElement).value.trim();
  const title     = (document.getElementById('docTitle')         as HTMLTextAreaElement).value.trim();
  const issuer    = (document.getElementById('docIssuer')        as HTMLInputElement).value.trim();
  const release   = parseInputDate((document.getElementById('docReleaseDate')   as HTMLInputElement).value);
  const effective = parseInputDate((document.getElementById('docEffectiveDate') as HTMLInputElement).value);
  const supersede = (document.getElementById('supersedeSelect')  as HTMLSelectElement).value;

  if (!release || !effective) {
    showToast('Vui lòng nhập ngày hợp lệ dạng dd/mm/yyyy.', 'error');
    return;
  }

  const formData = new FormData();
  formData.append('ma_hieu',           code);
  formData.append('ten_day_du',        title);
  formData.append('co_quan_ban_hanh',  issuer);
  formData.append('ngay_ban_hanh',     release);
  formData.append('ngay_hieu_luc',     effective);
  if (supersede) formData.append('replaces_document_id', supersede);
  formData.append('file', file);

  const submitBtn = document.getElementById('uploadSubmitBtn') as HTMLButtonElement;
  const btnSpan   = submitBtn.querySelector('span')!;
  submitBtn.disabled = true;
  btnSpan.textContent = 'Đang nạp lên...';

  try {
    await uploadDocument(
      { 'X-User-ID': currentUser.id, 'X-Tenant-ID': activeTenant.id },
      formData
    );

    showToast('Đã nạp văn bản quy phạm thành công!');
    (document.getElementById('uploadForm') as HTMLFormElement).reset();
    filePromptText.style.display = 'block';
    fileSelectedInfo.style.display = 'none';

    await fetchAndRenderCatalog();
    await fetchAndRenderAudits();
  } catch (err) {
    showToast(err instanceof Error ? err.message : 'Lỗi không xác định.', 'error');
  } finally {
    submitBtn.disabled = false;
    btnSpan.textContent = 'Nạp Văn Bản';
  }
}
