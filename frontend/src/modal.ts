// ============================================================
// Replace PDF Modal Module
// ============================================================
import { currentUser, activeTenant } from './state';
import { replacePdf } from './api';
import { showToast } from './toast';
import { fetchAndRenderCatalog } from './catalog';
import { fetchAndRenderAudits } from './audit';

const replaceModal           = document.getElementById('replaceModal')!;
const replaceFileInput       = document.getElementById('replaceFileInput')       as HTMLInputElement;
const replaceFilePromptText  = document.getElementById('replaceFilePromptText')!;
const replaceFileSelectedInfo = document.getElementById('replaceFileSelectedInfo')!;

export function openReplaceModal(docId: string, docCode: string): void {
  (document.getElementById('replaceDocId') as HTMLInputElement).value = docId;
  document.getElementById('replaceDocCode')!.textContent = docCode;

  replaceFileInput.value = '';
  replaceFilePromptText.style.display = 'block';
  replaceFileSelectedInfo.style.display = 'none';

  replaceModal.classList.add('show');
}

export function closeReplaceModal(): void {
  replaceModal.classList.remove('show');
}

export function onReplaceFileSelected(): void {
  const file = replaceFileInput.files?.[0];
  if (file) {
    replaceFilePromptText.style.display = 'none';
    replaceFileSelectedInfo.style.display = 'block';
    replaceFileSelectedInfo.textContent = `Đã chọn: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
  } else {
    replaceFilePromptText.style.display = 'block';
    replaceFileSelectedInfo.style.display = 'none';
  }
}

export async function onReplaceSubmitted(e: SubmitEvent): Promise<void> {
  e.preventDefault();
  if (!currentUser || !activeTenant) return;

  const docId = (document.getElementById('replaceDocId') as HTMLInputElement).value;
  const file  = replaceFileInput.files?.[0];

  if (!file) {
    showToast('Vui lòng chọn file PDF nguồn mới.', 'error');
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  const submitBtn = document.getElementById('replaceSubmitBtn') as HTMLButtonElement;
  submitBtn.disabled = true;
  submitBtn.textContent = 'Đang cập nhật...';

  try {
    await replacePdf(
      { 'X-User-ID': currentUser.id, 'X-Tenant-ID': activeTenant.id },
      docId,
      formData
    );

    showToast('Đã thay thế file PDF nguồn và tăng phiên bản!');
    closeReplaceModal();
    await fetchAndRenderCatalog();
    await fetchAndRenderAudits();
  } catch (err) {
    showToast(err instanceof Error ? err.message : 'Lỗi không xác định.', 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Cập Nhật Nguồn';
  }
}

/** Wire up modal close + backdrop click */
export function initModal(): void {
  document.getElementById('closeReplaceModalBtn')!.addEventListener('click', closeReplaceModal);
  document.getElementById('cancelReplaceBtn')!.addEventListener('click', closeReplaceModal);
  replaceModal.addEventListener('click', (e) => {
    if (e.target === replaceModal) closeReplaceModal();
  });
  replaceFileInput.addEventListener('change', onReplaceFileSelected);
  (document.getElementById('replaceForm') as HTMLFormElement).addEventListener('submit', (e) => {
    void onReplaceSubmitted(e as SubmitEvent);
  });
}
