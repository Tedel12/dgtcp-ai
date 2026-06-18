import React from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  AlertCircle, 
  CheckCircle2, 
  Wallet, 
  ArrowUpRight, 
  ArrowDownRight,
  Filter,
  Download,
  Zap,
  Activity,
  Timer,
  ChevronRight
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  LineChart,
  Line
} from 'recharts';
import { useQuery } from '@tanstack/react-query';
import api from '../api/client';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

// Composant pour les indicateurs de performance IA (Module 8 du document Aubin)
const PerformanceIndicator = ({ label, value, trend, color }: any) => {
  const colorMap: any = {
    blue: { bg: 'bg-blue-50', text: 'text-blue-600', stroke: '#3B82F6' },
    green: { bg: 'bg-emerald-50', text: 'text-emerald-600', stroke: '#10B981' },
    orange: { bg: 'bg-orange-50', text: 'text-orange-600', stroke: '#F59E0B' },
    purple: { bg: 'bg-purple-50', text: 'text-purple-600', stroke: '#8B5CF6' },
  };
  const theme = colorMap[color] || colorMap.blue;

  return (
    <div className="bg-white p-5 rounded-3xl border border-slate-100 flex items-center justify-between group hover:border-blue-100 transition-all">
      <div>
        <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-1">{label}</p>
        <h4 className="text-xl font-bold text-slate-900">{value}</h4>
      </div>
      <div className="h-12 w-20">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={trend.map((v: number, i: number) => ({ i, v }))}>
            <Line 
              type="monotone" 
              dataKey="v" 
              stroke={theme.stroke} 
              strokeWidth={2} 
              dot={false} 
              animationDuration={2000}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

const KPICard = ({ title, value, subValue, trend, icon: Icon, color }: any) => (
  <motion.div 
    whileHover={{ y: -4 }}
    className="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-[0_8px_30px_rgb(0,0,0,0.02)] flex flex-col justify-between relative overflow-hidden"
  >
    <div className="flex justify-between items-start z-10">
      <div className={`p-3 rounded-2xl ${color.bg}`}>
        <Icon className={`w-6 h-6 ${color.text}`} />
      </div>
      {trend !== undefined && (
        <div className={`flex items-center space-x-1 text-xs font-bold px-2.5 py-1 rounded-full ${trend >= 0 ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-red-600'}`}>
          {trend >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
          <span>{Math.abs(trend)}%</span>
        </div>
      )}
    </div>
    <div className="mt-5 z-10">
      <p className="text-slate-500 text-sm font-medium">{title}</p>
      <h3 className="text-2xl font-bold text-slate-900 mt-1 tracking-tight">{value}</h3>
      {subValue && <p className="text-slate-400 text-xs mt-1.5 font-medium">{subValue}</p>}
    </div>
    <div className={`absolute -right-4 -bottom-4 w-24 h-24 rounded-full ${color.bg} opacity-10 blur-2xl`} />
  </motion.div>
);

const Dashboard: React.FC = () => {
  // 1. Fetch Summary (KPIs, Charts, IA Indicators)
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: async () => {
      const res = await api.get('/dashboard/summary');
      return res.data;
    }
  });

  const handleExportPDF = async () => {
    try {
      const response = await api.get('/rapports/rapport-executif', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'Rapport_Strategique_DGTCP.pdf');
      document.body.appendChild(link);
      link.click();
    } catch (err) {
      console.error("Erreur lors de l'export PDF", err);
    }
  };

  // 2. Fetch Real Alerts (Recent)
  const { data: alertsData, isLoading: alertsLoading } = useQuery({
    queryKey: ['recent-alerts'],
    queryFn: async () => {
      const res = await api.get('/alertes/recentes?limit=4');
      return res.data;
    }
  });

  if (summaryLoading || alertsLoading) return (
    <div className="flex items-center justify-center h-[60vh]">
      <div className="relative">
        <div className="w-12 h-12 border-4 border-slate-100 border-t-blue-600 rounded-full animate-spin" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" />
        </div>
      </div>
    </div>
  );

  const kpis = summary?.kpi;
  const evolution = summary?.evolution.points;
  const repartition = summary?.repartition_anomalies.segments;
  const indicators = summary?.indicateurs.indicateurs;
  const recentAlerts = alertsData?.alertes || [];

  return (
    <div className="space-y-8 max-w-[1600px] mx-auto pb-12">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">Executive Dashboard</h1>
          <p className="text-slate-500 text-sm mt-1.5 font-medium flex items-center">
            <Zap className="w-4 h-4 text-amber-400 mr-2" />
            Analyse proactive des flux financiers en temps réel — DGTCP Bénin
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-2 px-5 py-3 bg-white border border-slate-200 rounded-2xl text-[13px] font-bold text-slate-700 hover:bg-slate-50 transition-all shadow-sm">
            <Filter className="w-4 h-4 text-slate-400" />
            <span>Période : Ce mois</span>
          </button>
          <button 
            onClick={handleExportPDF}
            className="flex items-center space-x-2 px-6 py-3 bg-slate-900 text-white rounded-2xl text-[13px] font-bold hover:bg-slate-800 transition-all shadow-xl shadow-slate-200 active:scale-95"
          >
            <Download className="w-4 h-4" />
            <span>Rapport Stratégique</span>
          </button>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard 
          title="Volume de Transactions" 
          value={kpis?.total_transactions.toLocaleString() || "0"} 
          trend={kpis?.variation_transactions}
          icon={Activity} 
          color={{ bg: 'bg-indigo-50', text: 'text-indigo-600' }}
          subValue="Flux financier mensuel"
        />
        <KPICard 
          title="Anomalies Détectées" 
          value={kpis?.anomalies_detectees || "0"} 
          trend={-2.4} 
          icon={AlertCircle} 
          color={{ bg: 'bg-rose-50', text: 'text-rose-600' }}
          subValue={`${kpis?.taux_anomalies}% du volume total`}
        />
        <KPICard 
          title="Conformité Globale" 
          value={`${kpis?.taux_transactions_normales}%`} 
          icon={CheckCircle2} 
          color={{ bg: 'bg-emerald-50', text: 'text-emerald-600' }}
          subValue="Transactions validées par l'IA"
        />
        <KPICard 
          title="Impact Financier" 
          value={`${(kpis?.economies_potentielles / 1_000_000).toFixed(1)}M FCFA`} 
          icon={Wallet} 
          color={{ bg: 'bg-amber-50', text: 'text-amber-600' }}
          subValue="Montants à risque élevé (Bloqués)"
        />
      </div>

      {/* Main Analysis Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Evolution Chart (Real Data) */}
        <div className="lg:col-span-2 bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-[0_8px_30px_rgb(0,0,0,0.01)]">
          <div className="flex items-center justify-between mb-10">
            <div className="flex items-center space-x-3">
              <div className="w-1.5 h-6 bg-blue-600 rounded-full" />
              <h3 className="text-xl font-bold text-slate-900 tracking-tight">Tendances des Flux</h3>
            </div>
            <div className="flex bg-slate-50 p-1 rounded-xl">
              <button className="px-4 py-1.5 bg-white shadow-sm rounded-lg text-xs font-bold text-blue-600 transition-all">Volume</button>
              <button className="px-4 py-1.5 text-xs font-bold text-slate-400 hover:text-slate-600 transition-all">Risque</button>
            </div>
          </div>
          <div className="h-[380px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={evolution}>
                <defs>
                  <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.15}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F8FAFC" />
                <XAxis 
                  dataKey="date" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#94A3B8', fontSize: 11, fontWeight: 600 }}
                  dy={15}
                />
                <YAxis 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#94A3B8', fontSize: 11, fontWeight: 600 }}
                />
                <Tooltip 
                  cursor={{ stroke: '#3B82F6', strokeWidth: 1, strokeDasharray: '4 4' }}
                  contentStyle={{ borderRadius: '24px', border: 'none', boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)', padding: '16px' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="total" 
                  name="Total Transactions"
                  stroke="#3B82F6" 
                  strokeWidth={4}
                  fillOpacity={1} 
                  fill="url(#colorTotal)" 
                />
                <Area 
                  type="monotone" 
                  dataKey="anomalies" 
                  name="Anomalies"
                  stroke="#EF4444" 
                  strokeWidth={2}
                  fill="transparent" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Repartition Donut (Real Data) */}
        <div className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-[0_8px_30px_rgb(0,0,0,0.01)] flex flex-col">
          <div className="mb-8 text-center">
            <h3 className="text-xl font-bold text-slate-900 tracking-tight">Typologie des Risques</h3>
            <p className="text-slate-400 text-xs font-bold mt-1 uppercase tracking-widest">Répartition IA</p>
          </div>
          <div className="flex-1 min-h-[320px] flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={repartition}
                  innerRadius={85}
                  outerRadius={115}
                  paddingAngle={10}
                  dataKey="count"
                  nameKey="label"
                  animationBegin={0}
                  animationDuration={1500}
                >
                  {repartition?.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.couleur} stroke="none" />
                  ))}
                </Pie>
                <Tooltip />
                <Legend 
                  verticalAlign="bottom" 
                  height={80} 
                  content={({ payload }) => (
                    <div className="grid grid-cols-1 gap-2.5 mt-6 px-4">
                      {payload?.map((entry: any, index: number) => (
                        <div key={index} className="flex items-center justify-between group">
                          <div className="flex items-center space-x-2.5 text-left">
                            <div className="w-2 h-2 rounded-full ring-4 ring-slate-50 transition-all group-hover:scale-125" style={{ backgroundColor: entry.color }} />
                            <span className="text-[11.5px] font-bold text-slate-600">{entry.value}</span>
                          </div>
                          <span className="text-[11.5px] font-extrabold text-slate-900">
                            {repartition?.[index]?.count}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Performance Indicators (Module 8 of Intro document) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {indicators?.map((ind: any, idx: number) => (
          <PerformanceIndicator 
            key={idx}
            label={ind.label}
            value={ind.valeur}
            color={ind.couleur}
            trend={ind.tendance}
          />
        ))}
      </div>

      {/* Real-time Alerts Block (Module 6) */}
      <div className="bg-slate-900 p-10 rounded-[3rem] text-white relative shadow-2xl shadow-slate-300 group overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/10 blur-[120px] rounded-full -mr-32 -mt-32 transition-all group-hover:bg-blue-600/20" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-rose-600/5 blur-[100px] rounded-full -ml-32 -mb-32" />
        
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-10 border-b border-white/5 pb-6">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-rose-500/20 rounded-2xl border border-rose-500/30 animate-pulse">
                <AlertCircle className="text-rose-500 w-6 h-6" />
              </div>
              <div>
                <h3 className="text-2xl font-bold tracking-tight">Signalements Critiques</h3>
                <p className="text-slate-400 text-sm font-medium mt-1">Nécessitent une validation immédiate des décideurs</p>
              </div>
            </div>
            <button className="bg-white/5 hover:bg-white/10 px-5 py-2.5 rounded-xl text-xs font-bold transition-all border border-white/10 flex items-center space-x-2">
              <span>Consulter tout le flux</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {recentAlerts.length > 0 ? (
              recentAlerts.map((alert: any) => (
                <div key={alert.id} className="bg-white/5 border border-white/10 p-6 rounded-[2rem] flex items-center justify-between hover:bg-white/10 hover:-translate-y-1 transition-all cursor-pointer group/item">
                  <div className="flex items-center space-x-5">
                    <div className={`w-14 h-14 rounded-2xl flex items-center justify-center text-sm font-black border ${
                      alert.niveau === 'critique' ? 'bg-rose-500/20 text-rose-500 border-rose-500/20' : 'bg-orange-500/20 text-orange-500 border-orange-500/20'
                    }`}>
                      {alert.niveau === 'critique' ? '!!!' : '!'}
                    </div>
                    <div>
                      <h4 className="font-bold text-sm leading-tight text-white group-hover/item:text-blue-400 transition-colors">{alert.titre}</h4>
                      <p className="text-[11px] text-slate-400 mt-2 font-bold uppercase tracking-wider">{alert.entite_concernee}</p>
                      <p className="text-xs text-slate-500 mt-1 font-medium">{format(new Date(alert.created_at), 'HH:mm', { locale: fr })} — {alert.montant_concerne?.toLocaleString()} FCFA</p>
                    </div>
                  </div>
                  <div className="hidden sm:block text-right">
                    <div className="bg-rose-500/10 text-rose-400 text-[10px] px-3 py-1 rounded-full font-black uppercase tracking-tighter border border-rose-500/10 mb-2">
                      Bloquer
                    </div>
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">{alert.niveau}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-2 text-center py-10 border-2 border-dashed border-white/5 rounded-[2rem]">
                <p className="text-slate-500 font-bold italic">Aucune alerte critique non traitée.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
