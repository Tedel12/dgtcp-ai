import api from './client';
import { Transaction } from '../types/transaction';

export const transactionsService = {
  getById: async (id: string | number): Promise<any> => {
    const response = await api.get(`/transactions/${id}`);
    return response.data;
  },
  getAnomalies: async (id: string | number): Promise<any[]> => {
    const response = await api.get(`/transactions/${id}/anomalies`);
    return response.data;
  }
};
