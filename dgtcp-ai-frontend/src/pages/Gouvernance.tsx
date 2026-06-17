import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { ShieldCheck, UserCog, User } from 'lucide-react';
import api from '../api/client';
import { Utilisateur, Role } from '../types/auth';

const Gouvernance: React.FC = () => {
  const queryClient = useQueryClient();

  const { data: users, isLoading } = useQuery<Utilisateur[]>({
    queryKey: ['users'],
    queryFn: async () => (await api.get('/users')).data
  });

  const updateRoleMutation = useMutation({
    mutationFn: (data: { id: number; role: Role }) => 
      api.patch(`/users/${data.id}/role`, null, { params: { role: data.role } }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] })
  });

  if (isLoading) return <div className="text-center py-20">Chargement...</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-slate-900">Gouvernance des Accès</h2>
      
      <div className="bg-white rounded-[2rem] border border-slate-100 shadow-[0_8px_30px_rgb(0,0,0,0.02)] overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-bold tracking-wider">
            <tr>
              <th className="px-8 py-6">Utilisateur</th>
              <th className="px-8 py-6">Email</th>
              <th className="px-8 py-6">Rôle Actuel</th>
              <th className="px-8 py-6">Changer Rôle</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {users?.map((user) => (
              <tr key={user.id} className="hover:bg-slate-50/50 transition-colors">
                <td className="px-8 py-5 flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center">
                    <User className="w-5 h-5 text-slate-500" />
                  </div>
                  <div>
                    <p className="font-bold text-slate-900 text-sm">{user.nom} {user.prenom}</p>
                    <p className="text-xs text-slate-500">{user.poste}</p>
                  </div>
                </td>
                <td className="px-8 py-5 text-sm text-slate-600">{user.email}</td>
                <td className="px-8 py-5">
                  <span className="px-3 py-1 rounded-full text-[11px] font-bold bg-blue-50 text-blue-700 uppercase">
                    {user.role.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-8 py-5">
                  <select 
                    defaultValue={user.role}
                    className="bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-xs font-bold outline-none"
                    onChange={(e) => updateRoleMutation.mutate({ id: user.id, role: e.target.value as Role })}
                  >
                    {Object.values(Role).map(role => (
                      <option key={role} value={role}>{role.replace('_', ' ')}</option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Gouvernance;
