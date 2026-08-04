// ============================================================
// Drag and Drop Utility
// ============================================================
import { showToast } from '../toast';

/**
 * Binds drag-and-drop event listeners to a dropzone element and maps
 * dropped PDF files to an underlying HTML input file element.
 */
export function setupDragAndDrop(
  triggerElement: HTMLElement,
  inputElement: HTMLInputElement,
  onFileSelectedCallback: () => void
): void {
  // Prevent default behaviors for drag events
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((eventName) => {
    triggerElement.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
    }, false);
  });

  // Highlight dropzone on drag over
  ['dragenter', 'dragover'].forEach((eventName) => {
    triggerElement.addEventListener(eventName, () => {
      triggerElement.classList.add('dragover');
    }, false);
  });

  // Unhighlight on drag leave
  ['dragleave', 'drop'].forEach((eventName) => {
    triggerElement.addEventListener(eventName, () => {
      triggerElement.classList.remove('dragover');
    }, false);
  });

  // Handle dropped files
  triggerElement.addEventListener('drop', (e: DragEvent) => {
    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
        const dt = new DataTransfer();
        dt.items.add(file);
        inputElement.files = dt.files;
        onFileSelectedCallback();
      } else {
        showToast('Chỉ chấp nhận file PDF.', 'error');
      }
    }
  }, false);
}
