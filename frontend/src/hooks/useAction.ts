import { useMutation, useQueryClient } from '@tanstack/react-query';
import { App } from 'antd';
import { api } from '../services/api';
import { errorMessage } from '../utils/access';
export function useAction() {
  const client = useQueryClient();
  const {
    message
  } = App.useApp();
  return useMutation({
    mutationFn: async ({
      path,
      body,
      method = 'post'
    }: {
      path: string;
      body?: unknown;
      method?: 'post' | 'patch' | 'delete';
    }) => (await api.request({
      url: path,
      data: body,
      method
    })).data as unknown,
    onSuccess: () => {
      void client.invalidateQueries();
      void message.success('Đã lưu thay đổi.');
    },
    onError: error => void message.error(errorMessage(error))
  });
}
