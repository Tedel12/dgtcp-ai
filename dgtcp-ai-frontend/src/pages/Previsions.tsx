import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { TrendingUp, AlertTriangle, Scale, Target } from 'lucide-react';
import { 
  ComposedChart, 
  Line, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Legend 
} from 'recharts';
import api from '../api/client';
import { PrevisionResponse, RisqueBudgetaire } from '../types/prevision';

const Previsions: React.FC = () => {
  const { data: tresorerie, isLoading: loadingTres } = useQuery<PrevisionResponse>({
    queryKey: ['previsions-tresorerie'],
    queryFn: async () => (await api.get('/predictions/tresorerie')).data
  });

  const { data: risques, isLoading: loadingRisque } = useQuery<RisqueBudgetaire[]>({
    queryKey: ['risques-budgetaires'],
    queryFn: async () => (await api.get('/predictions/risques-budgetaires')).data
  });

  if (loadingTres || loadingRisque) return <div className="text-center py-20 font-bold text-slate-500">Chargement des prévisions...</div>;

  return (
    <div className="space-y-8 max-w-[1600px] mx-auto pb-12">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Prévisions Budgétaires & IA</h2>
          <p className="text-slate-500 text-sm mt-1">Analyse des flux prévisionnels de trésorerie</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-[0_8px_30px_rgb(0,0,0,0.02)]">
          <h3 className="text-lg font-bold text-slate-900 mb-8">Trésorerie Prévisionnelle (6 mois)</h3>
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={tresorerie?.previsions}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                <XAxis dataKey="mois" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94A3B8' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94A3B8' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="depenses_prevues" name="Dépenses Prévues" fill="#3B82F6" radius={[8, 8, 0, 0]} />
                <Bar dataKey="recettes_prevues" name="Recettes Prévues" fill="#10B981" radius={[8, 8, 0, 0]} />
                <Line type="monotone" dataKey="solde_previsionnel" name="Solde Prévisionnel" stroke="#F59E0B" strokeWidth={3} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-[0_8px_30px_rgb(0,0,0,0.02)]">
          <h3 className="text-lg font-bold text-slate-900 mb-6">Risques par Ministère</h3>
          <div className="space-y-4">
            {risques?.slice(0, 5).map((r) => (
              <div key={r.ministere} className="flex justify-between items-center p-4 bg-slate-50 rounded-2xl">
                <div>
                  <p className="text-sm font-bold text-slate-900">{r.ministere}</p>
                  <p className="text-xs text-slate-500 font-medium">Exécution: {r.taux_execution_pct}%</p>
                </div>
                {r.taux_execution_pct > 100 && <AlertTriangle className="w-5 h-5 text-rose-500" />}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Previsions;
