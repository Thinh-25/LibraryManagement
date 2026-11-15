import { Alert, Button, Space, Typography } from 'antd';
import { useEffect, useId, useRef, useState } from 'react';
import { api } from '../services/api';
import { errorMessage } from '../utils/access';
import { validateCoverFile } from '../utils/images';
import { CoverImage } from './CoverImage';

interface ImagePickerProps {
  value?: string | null;
  onChange?: (value: string | null) => void;
  onBlockedChange?: (blocked: boolean) => void;
  id?: string;
}

export function ImagePicker({ value, onChange, onBlockedChange, id }: ImagePickerProps) {
  const helpId = useId();
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string>();
  const [selectedFile, setSelectedFile] = useState<File>();
  const controller = useRef<AbortController | null>(null);
  const fileInput = useRef<HTMLInputElement | null>(null);
  const generation = useRef(0);
  const blockedCallback = useRef(onBlockedChange);
  blockedCallback.current = onBlockedChange;

  useEffect(() => () => {
    generation.current++;
    controller.current?.abort();
  }, []);

  async function upload(file: File) {
    const current = ++generation.current;
    controller.current?.abort();
    const validation = validateCoverFile(file);
    setSelectedFile(file);
    setError(validation ?? undefined);
    setUploading(false);
    blockedCallback.current?.(true);
    if (validation) return;
    const abort = new AbortController();
    controller.current = abort;
    setUploading(true);
    const body = new FormData();
    body.append('file', file);
    try {
      const result = await api.post<{ url: string }>('/uploads/covers', body, { signal: abort.signal });
      if (current !== generation.current) return;
      if (!/^\/media\/covers\/[0-9a-f]{32}\.webp$/.test(result.data.url)) throw new Error('Invalid image upload response');
      onChange?.(result.data.url);
      setSelectedFile(undefined);
      blockedCallback.current?.(false);
    } catch (cause) {
      if (current === generation.current) setError(errorMessage(cause));
    } finally {
      if (current === generation.current) setUploading(false);
    }
  }

  function remove() {
    generation.current++;
    controller.current?.abort();
    setUploading(false);
    setSelectedFile(undefined);
    setError(undefined);
    onChange?.(null);
    blockedCallback.current?.(false);
  }

  return <Space orientation="vertical" className="full-width">
    <CoverImage value={value} alt="Ảnh bìa xem trước" />
    <Button onClick={() => fileInput.current?.click()}>Chọn ảnh từ máy</Button>
    <input ref={fileInput} id={id} className="cover-file-input" type="file" accept="image/jpeg,image/png,image/webp" aria-label="Chọn ảnh từ máy" aria-describedby={helpId} tabIndex={-1} onChange={event => {
      const file = event.target.files?.[0];
      event.target.value = '';
      if (file) void upload(file);
    }} />
    <Typography.Text type="secondary" id={helpId}>JPG, PNG hoặc WebP, tối đa 5 MB. Ảnh được xem trước sau khi tải lên.</Typography.Text>
    {uploading && <span role="status">Đang tải ảnh lên…</span>}
    {error && <Alert type="error" title={error} showIcon />}
    <Space>
      {error && selectedFile && <Button onClick={() => void upload(selectedFile)}>Thử tải lại ảnh</Button>}
      {(value || selectedFile) && <Button onClick={remove}>Bỏ ảnh</Button>}
    </Space>
  </Space>;
}
