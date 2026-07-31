// ============================================================
// Toast Notification Module
// ============================================================
import type { ToastType } from './types';

const toast       = document.getElementById('toast')!;
const toastMsg    = document.getElementById('toastMessage')!;
const toastIcon   = document.getElementById('toastIcon')!;

let toastTimer: ReturnType<typeof setTimeout> | null = null;

/**
 * Display a transient toast popup notification.
 */
export function showToast(message: string, type: ToastType = 'success'): void {
  toastMsg.textContent = message;

  if (type === 'success') {
    toastIcon.className = 'fa-solid fa-circle-check';
    toastIcon.style.color = '#34d399';
  } else {
    toastIcon.className = 'fa-solid fa-circle-exclamation';
    toastIcon.style.color = '#f87171';
  }

  toast.className = `toast show ${type}`;

  if (toastTimer !== null) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove('show');
    toastTimer = null;
  }, 3500);
}
