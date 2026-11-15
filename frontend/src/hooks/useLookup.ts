import { useInfiniteQuery } from '@tanstack/react-query';
import { getData } from '../services/api';
import type { Page } from '../services/api';
export function useLookup<T>(path: string, search: string) {
  const query = useInfiniteQuery({
    queryKey: ['lookup', path, search],
    initialPageParam: 1,
    queryFn: ({
      pageParam
    }) => getData<Page<T>>(path, {
      search,
      page: pageParam,
      page_size: 50
    }),
    getNextPageParam: last => last.page * last.page_size < last.total ? last.page + 1 : undefined
  });
  return {
    ...query,
    items: query.data?.pages.flatMap(p => p.items) ?? [],
    loadMore: (event: React.UIEvent<HTMLDivElement>) => {
      const node = event.currentTarget;
      if (node.scrollHeight - node.scrollTop - node.clientHeight < 32 && query.hasNextPage && !query.isFetchingNextPage) void query.fetchNextPage();
    }
  };
}
