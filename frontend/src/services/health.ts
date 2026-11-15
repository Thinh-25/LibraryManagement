import { api } from './api';
import type { HealthResponse } from '../types/health';

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await api.get<unknown>('/health');
  if (typeof data !== 'object' || data === null || !('status' in data) || data.status !== 'ok') {
    throw new Error('Phản hồi trạng thái API không hợp lệ.');
  }
  return { status: data.status };
}
