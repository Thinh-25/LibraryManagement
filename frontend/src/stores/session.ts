import { create } from 'zustand';
import type { Role } from '../utils/access';
export interface User {
  id: number;
  ho_ten: string;
  email: string;
  so_dien_thoai: string | null;
  vai_tro: Role;
  trang_thai: boolean;
  must_change_password: boolean;
}
interface Session {
  token: string | null;
  user: User | null;
  setSession: (token: string, user: User) => void;
  setUser: (user: User) => void;
  clear: () => void;
}
export const useSession = create<Session>(set => ({
  token: null,
  user: null,
  setSession: (token, user) => set({
    token,
    user
  }),
  setUser: user => set({
    user
  }),
  clear: () => set({
    token: null,
    user: null
  })
}));
