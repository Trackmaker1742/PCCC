// ============================================================
// Date Utilities
// ============================================================

/**
 * Converts a dd/mm/yyyy string to yyyy-mm-dd for API calls.
 * Returns an empty string if the input is invalid.
 */
export function parseInputDate(value: string): string {
  if (!value) return '';
  const match = value.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  if (match) {
    return `${match[3]}-${match[2]}-${match[1]}`;
  }
  return '';
}

/**
 * Formats an ISO date string (yyyy-mm-dd or ISO 8601) to dd/mm/yyyy.
 */
export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return 'N/A';
  const d = new Date(dateStr);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
}

/**
 * Formats an ISO datetime string to dd/mm/yyyy HH:MM.
 */
export function formatDateTime(dateTimeStr: string | null | undefined): string {
  if (!dateTimeStr) return 'N/A';
  const d = new Date(dateTimeStr);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

/**
 * Attaches a dd/mm/yyyy auto-formatting mask to an input element.
 * Optionally calls `onChangeCallback` when a valid or empty value is present.
 */
export function setupDateMask(
  id: string,
  onChangeCallback?: () => void
): void {
  const input = document.getElementById(id) as HTMLInputElement | null;
  if (!input) return;

  input.addEventListener('input', () => {
    let value = input.value.replace(/\D/g, '');
    if (value.length > 8) value = value.substring(0, 8);

    if (value.length > 4) {
      input.value = `${value.substring(0, 2)}/${value.substring(2, 4)}/${value.substring(4)}`;
    } else if (value.length > 2) {
      input.value = `${value.substring(0, 2)}/${value.substring(2)}`;
    } else {
      input.value = value;
    }

    if (onChangeCallback) {
      const isComplete = !input.value || input.value.length === 10;
      if (isComplete) onChangeCallback();
    }
  });
}
