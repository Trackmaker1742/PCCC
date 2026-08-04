// ============================================================
// Application Entry Point
// ============================================================
import '../../static/css/style.css';

import {
  mockUsers,
  mockTenants,
  setMockUsers,
  setMockTenants,
  setCurrentUser,
  setActiveTenant,
} from './state';
import { fetchTenants, fetchUsers } from './api';
import { setupDateMask } from './utils/dates';
import { showToast } from './toast';
import { fetchAndRenderCatalog, resetFilters, updateFormVisibility } from './catalog';
import { fetchAndRenderAudits } from './audit';
import { onFileSelected, onUploadSubmitted, initUploadDragAndDrop } from './upload';
import { initModal, initModalDragAndDrop } from './modal';

// ---- DOM References ---------------------------------------------------------
const userSelect        = document.getElementById('userSelect')        as HTMLSelectElement;
const activeTenantLabel = document.getElementById('activeTenantLabel')!;
const filterCode        = document.getElementById('filterCode')        as HTMLInputElement;
const filterStatus      = document.getElementById('filterStatus')      as HTMLSelectElement;
const resetFiltersBtn   = document.getElementById('resetFiltersBtn')!;
const docFileInput      = document.getElementById('docFileInput')      as HTMLInputElement;
const uploadForm        = document.getElementById('uploadForm')        as HTMLFormElement;

// ---- Data Loading -----------------------------------------------------------

async function loadMockData(): Promise<void> {
  try {
    const [tenants, users] = await Promise.all([fetchTenants(), fetchUsers()]);
    setMockTenants(tenants);
    setMockUsers(users);

    userSelect.innerHTML = users
      .map((u) => {
        const tenant = tenants.find((t) => t.id === u.tenant_id);
        const tenantName = tenant ? tenant.ma_tenant : 'Không rõ';

        const roleLabels: Record<string, string> = {
          ADMIN: 'Quản trị viên',
          THAM_TRA_VIEN: 'Thẩm tra viên',
          CHUYEN_GIA_PHE_DUYET: 'Phê duyệt viên',
        };
        const roleLabel = roleLabels[u.vai_tro] ?? u.vai_tro;

        return `<option value="${u.id}">${u.ho_ten} (${tenantName} - ${roleLabel})</option>`;
      })
      .join('');
  } catch (err) {
    console.error(err);
    showToast('Không thể tải thông tin cấu hình giả lập.', 'error');
  }
}

// ---- Context / Permissions --------------------------------------------------

async function onUserChanged(): Promise<void> {
  const selectedUserId = userSelect.value;
  const user = mockUsers.find((u) => u.id === selectedUserId) ?? null;
  setCurrentUser(user);
  if (!user) return;

  const tenant = mockTenants.find((t) => t.id === user.tenant_id) ?? null;
  setActiveTenant(tenant);
  if (!tenant) return;

  activeTenantLabel.textContent = `${tenant.ten_co_quan} (${tenant.ma_tenant})`;

  updateFormVisibility();
  await fetchAndRenderCatalog();
  await fetchAndRenderAudits();
}

// ---- Wiring -----------------------------------------------------------------

function wireEventListeners(): void {
  // User / context switcher
  userSelect.addEventListener('change', () => { void onUserChanged(); });

  // Upload form
  docFileInput.addEventListener('change', onFileSelected);
  uploadForm.addEventListener('submit', (e) => { void onUploadSubmitted(e as SubmitEvent); });

  // Filters
  filterCode.addEventListener('input', () => { void fetchAndRenderCatalog(); });
  filterStatus.addEventListener('change', () => { void fetchAndRenderCatalog(); });
  resetFiltersBtn.addEventListener('click', resetFilters);

  // Date masks (they call fetchAndRenderCatalog internally when complete)
  setupDateMask('docReleaseDate');
  setupDateMask('docEffectiveDate');
  setupDateMask('filterStartDate', () => { void fetchAndRenderCatalog(); });
  setupDateMask('filterEndDate',   () => { void fetchAndRenderCatalog(); });

  // Replace PDF modal
  initModal();

  // Drag and Drop initializations
  initUploadDragAndDrop();
  initModalDragAndDrop();
}

// ---- Bootstrap --------------------------------------------------------------

window.addEventListener('DOMContentLoaded', async () => {
  wireEventListeners();
  await loadMockData();
  await onUserChanged();
});
