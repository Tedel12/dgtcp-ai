import api from './client';
import { Anomalie } from '../types/anomalie';

export const anomaliesService = {
  getById: async (id: string | number): Promise<any> => {
    const response = await api.get(`/anomalies/${id}`);
    return response.data;
  },
  updateStatut: async (id: string | number, data: { statut: string, note_traitement?: string }): Promise<any> => {
    const response = await api.patch(`/anomalies/${id}`, data);
    return response.data;
  }
};
