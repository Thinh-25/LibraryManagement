import axios from 'axios';
import { useSession } from '../stores/session';
const baseURL = import.meta.env.VITE_API_BASE_URL;
if (!baseURL) throw new Error('Thiếu cấu hình VITE_API_BASE_URL.');
export const api = axios.create({
  baseURL,
  timeout: 15_000
});
api.interceptors.request.use(config => {
  const token = useSession.getState().token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
api.interceptors.response.use(response => response, (error: unknown) => {
  if (axios.isAxiosError(error) && error.response?.status === 401) useSession.getState().clear();
  return Promise.reject(error);
});
export async function getData<T>(path: string, params?: object): Promise<T> {
  return (await api.get<T>(path, {
    params
  })).data;
}
export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
export async function getAllPages<T>(path: string): Promise<T[]> {
  const items: T[] = [];
  let page = 1;
  let total = 0;
  do {
    const result = await getData<Page<T>>(path, {
      page,
      page_size: 100
    });
    items.push(...result.items);
    total = result.total;
    page++;
    if (result.items.length === 0) break;
  } while (items.length < total);
  return items;
}
