import React from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api/client';
import { motion } from 'framer-motion';
import { Shield, Clock, User, Activity } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

const Audit: React.FC = () => {
  const { data: logs, isLoading } = useQuery({
    queryKey: ['audit-logs'],
    queryFn: async () => {
      const res = await api.get('/audit/logs');
      return res.data;
    }
  });

  if (isLoading) return <div className="flex justify-center py-20">Chargement du journal d'audit...</div>;

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in">
      <div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Audit & Journal Système</h1>
        <p className="text-slate-500 text-sm mt-1 font-medium italic">Traçabilité complète des actions sensibles effectuées sur la plateforme.</p>
      </div>

      <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm overflow-hidden">
        <div className="p-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
          <div className="flex items-center space-x-3">
            <Shield className="w-5 h-5 text-blue-600" />
            <span className="font-bold text-slate-900">Journal des évènements</span>
          </div>
          <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Temps Réel</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="text-[11px] font-black uppercase tracking-widest text-slate-400 bg-white">
              <tr>
                <th className="px-8 py-5">Horodatage</th>
                <th className="px-8 py-5">Utilisateur</th>
                <th className="px-8 py-5">Action</th>
                <th className="px-8 py-5">Entité</th>
                <th className="px-8 py-5 text-right">Adresse IP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {logs?.map((log: any) => (
                <tr key={log.id} className="hover:bg-slate-50/50 transition-colors group">
                  <td className="px-8 py-5">
                    <div className="flex items-center space-x-2">
                      <Clock className="w-3 h-3 text-slate-300" />
                      <span className="text-xs font-bold text-slate-600">
                        {format(new Date(log.created_at), 'dd MMM yyyy HH:mm', { locale: fr })}
                      </span>
                    </div>
                  </td>
                  <td className="px-8 py-5">
                    <div className="flex items-center space-x-2">
                      <User className="w-3 h-3 text-blue-400" />
                      <span className="text-xs font-black text-slate-900">{log.utilisateur_nom}</span>
                    </div>
                  </td>
                  <td className="px-8 py-5">
                    <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter ${
                      log.action.includes('VALIDATION') ? 'bg-emerald-50 text-emerald-600' :
                      log.action.includes('REJET') ? 'bg-rose-50 text-rose-600' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {log.action.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-8 py-5">
                    <span className="text-xs font-medium text-slate-500">{log.entite || '—'}</span>
                  </td>
                  <td className="px-8 py-5 text-right">
                    <span className="text-[10px] font-mono font-bold text-slate-400">{log.ip_address || '127.0.0.1'}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Audit;
