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

  if (loadingTres || loadingRisque) return <div className="text-center py-20 font-bold text-slate-500">Chargement des analyses prédictives...</div>;

  return (
    <div className="space-y-10 max-w-[1600px] mx-auto pb-12 animate-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-black text-slate-900 tracking-tight">Intelligence Budgétaire</h1>
          <p className="text-slate-500 text-sm mt-1 font-medium italic">Prévisions de trésorerie et analyse préventive des dépassements par ministère.</p>
        </div>
        <div className="flex items-center space-x-3 bg-white p-2 rounded-2xl border border-slate-100 shadow-sm">
          <div className="px-4 py-2 bg-blue-50 text-blue-700 rounded-xl text-xs font-black uppercase tracking-tighter">
            Solde Actuel: {tresorerie?.solde_actuel_fcfa?.toLocaleString()} FCFA
          </div>
        </div>
      </div>

      {/* Section 1: Flux de Trésorerie */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white p-10 rounded-[3rem] border border-slate-100 shadow-[0_20px_50px_rgba(0,0,0,0.02)] relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-blue-50/50 blur-3xl rounded-full -mr-20 -mt-20" />
          
          <div className="relative z-10">
            <div className="flex items-center space-x-3 mb-10">
              <div className="w-1.5 h-6 bg-blue-600 rounded-full" />
              <h3 className="text-xl font-bold text-slate-900">Projection de Trésorerie (6 mois)</h3>
            </div>
            
            <div className="h-[450px]">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={tresorerie?.previsions}>
                  <defs>
                    <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#3B82F6" stopOpacity={0.8}/>
                      <stop offset="100%" stopColor="#3B82F6" stopOpacity={0.3}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F8FAFC" />
                  <XAxis dataKey="mois" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#94A3B8', fontWeight: 600 }} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#94A3B8', fontWeight: 600 }} />
                  <Tooltip 
                    contentStyle={{ borderRadius: '24px', border: 'none', boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)', padding: '20px' }}
                  />
                  <Legend verticalAlign="top" align="right" iconType="circle" wrapperStyle={{ paddingBottom: '20px' }} />
                  <Bar dataKey="depenses_prevues" name="Dépenses Estimées" fill="url(#barGradient)" radius={[10, 10, 0, 0]} barSize={40} />
                  <Line type="monotone" dataKey="solde_previsionnel" name="Solde de Sécurité" stroke="#F59E0B" strokeWidth={4} dot={{ r: 4, fill: '#F59E0B', strokeWidth: 2, stroke: '#fff' }} animationDuration={2000} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Section 2: Risques de dépassement */}
        <div className="bg-slate-900 rounded-[3rem] p-10 text-white shadow-2xl shadow-slate-200 flex flex-col">
          <div className="mb-10">
            <div className="flex items-center space-x-3 text-rose-500 mb-2">
              <AlertTriangle className="w-5 h-5" />
              <span className="text-[10px] font-black uppercase tracking-[0.2em]">Alerte Préventive</span>
            </div>
            <h3 className="text-2xl font-bold">Risques Budgétaires</h3>
            <p className="text-slate-400 text-sm mt-2">Ministères présentant un risque de dépassement imminent des crédits.</p>
          </div>

          <div className="flex-1 space-y-5">
            {risques?.map((r, idx) => (
              <div key={idx} className="group cursor-default">
                <div className="flex justify-between items-end mb-2">
                  <div>
                    <p className="text-sm font-bold group-hover:text-blue-400 transition-colors">{r.ministere}</p>
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{r.nb_transactions} opérations</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-xs font-black ${r.taux_execution_pct > 100 ? 'text-rose-500' : 'text-emerald-500'}`}>
                      {r.taux_execution_pct}%
                    </p>
                  </div>
                </div>
                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(r.taux_execution_pct, 100)}%` }}
                    transition={{ duration: 1.5, delay: idx * 0.1 }}
                    className={`h-full rounded-full ${r.taux_execution_pct > 100 ? 'bg-rose-500' : 'bg-blue-500'}`}
                  />
                </div>
              </div>
            ))}
          </div>

          <button className="mt-10 w-full bg-white/5 border border-white/10 hover:bg-white/10 py-4 rounded-2xl text-xs font-black uppercase tracking-widest transition-all">
            Analyse Complète
          </button>
        </div>
      </div>
    </div>
  );
};

export default Previsions;
