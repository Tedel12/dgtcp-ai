import api from './client';
import { AuthResponse, LoginRequest, SignupRequest } from '../types/auth';

export const authService = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', data);
    return response.data;
  },

  signup: async (data: SignupRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/signup', data);
    return response.data;
  },

  getMe: async (): Promise<any> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};
