import { useState } from 'react';
import { resolveImageUrl } from '../utils/images';

export function CoverImage({ value, alt, small = false }: { value?: string | null; alt: string; small?: boolean }) {
  const src = resolveImageUrl(value, import.meta.env.VITE_API_BASE_URL);
  const [failed, setFailed] = useState<string>();
  return src && failed !== src ? <img className={`cover-image${small ? ' cover-image-small' : ''}`} src={src} alt={alt} loading="lazy" onError={() => setFailed(src)} /> :
    <span className={`cover-placeholder${small ? ' cover-image-small' : ''}`} role="img" aria-label={`${alt}: ${value ? 'Không tải được ảnh' : 'Chưa có ảnh'}`}>{value ? 'Ảnh lỗi' : 'Chưa có ảnh'}</span>;
}
