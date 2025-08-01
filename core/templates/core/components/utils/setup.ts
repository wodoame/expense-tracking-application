import { QueryClient } from '@tanstack/query-core';

// 1. Create a QueryClient instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // Data is considered fresh for 5 minutes
      gcTime: 1000 * 60 * 5, // Cache data for 5 minutes
      refetchOnWindowFocus: false, // Disable refetch on window focus for vanilla JS
    },
  },
});

export { queryClient };