import api from './client';
import { Alerte } from '../types/alerte'; // Je vais créer ce type

export interface AlerteRecentResponse {
  non_lues: number;
  alertes: any[];
}

export const alertesService = {
  getRecentes: async (): Promise<AlerteRecentResponse> => {
    const response = await api.get<AlerteRecentResponse>('/alertes/recentes');
    return response.data;
  },
  marquerLue: async (id: number) => {
    return api.patch(`/alertes/${id}/lire`);
  },
  marquerToutesLues: async () => {
    return api.post('/alertes/lire-toutes');
  }
};
