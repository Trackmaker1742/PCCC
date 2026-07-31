// ============================================================
// HTML Utilities
// ============================================================

const HTML_ESCAPE_MAP: Record<string, string> = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#039;',
};

/**
 * Escapes unsafe HTML characters to prevent XSS when rendering user content.
 */
export function escapeHtml(text: string | null | undefined): string {
  if (!text) return '';
  return text.replace(/[&<>"']/g, (m) => HTML_ESCAPE_MAP[m] ?? m);
}
