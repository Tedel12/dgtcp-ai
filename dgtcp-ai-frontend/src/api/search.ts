import api from './client';

export interface SearchResult {
  type: 'transaction' | 'anomalie';
  id: number;
  title: string;
  subtitle: string;
  url: string;
}

export const searchService = {
  search: async (q: string): Promise<SearchResult[]> => {
    const response = await api.get<SearchResult[]>('/search', { params: { q } });
    return response.data;
  },
};
