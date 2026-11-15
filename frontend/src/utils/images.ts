const MAX_COVER_SIZE = 5 * 1024 * 1024;
const COVER_PATH = /^\/media\/covers\/[0-9a-f]{32}\.webp$/;

export function validateCoverFile(file: Pick<File, 'type' | 'size'>): string | null {
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) return 'Vui lòng chọn ảnh JPG, PNG hoặc WebP.';
  if (file.size === 0) return 'File ảnh trống. Vui lòng chọn ảnh khác.';
  if (file.size > MAX_COVER_SIZE) return 'Ảnh không được vượt quá 5 MB.';
  return null;
}

export function resolveImageUrl(value: string | null | undefined, apiBaseUrl: string): string | undefined {
  if (!value) return undefined;
  try {
    if (COVER_PATH.test(value)) return new URL(value, new URL(apiBaseUrl).origin).href;
    const url = new URL(value);
    return ['http:', 'https:'].includes(url.protocol) ? url.href : undefined;
  } catch {
    return undefined;
  }
}
