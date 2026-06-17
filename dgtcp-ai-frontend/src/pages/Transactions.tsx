import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Search, Filter, ArrowUpRight, ArrowDownRight, ShieldCheck, AlertTriangle } from 'lucide-react';
import api from '../api/client';
import { Transaction } from '../types/transaction';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

const Transactions: React.FC = () => {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['transactions', page, search],
    queryFn: async () => {
      const res = await api.get('/transactions', { params: { page, limit: 10, fournisseur: search || undefined } });
      return res.data;
    }
  });

  if (isLoading) return <div className="text-center py-20 font-bold text-slate-500">Chargement des transactions...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Registre des Transactions</h2>
          <p className="text-slate-500 text-sm">Visualisation des flux financiers de la DGTCP</p>
        </div>
        <div className="flex bg-white p-1 rounded-xl border border-slate-200">
          <input 
            placeholder="Rechercher par fournisseur..."
            className="px-4 py-2 text-sm outline-none w-64"
            onChange={(e) => setSearch(e.target.value)}
          />
          <button className="p-2 text-slate-400 hover:text-slate-900 transition-colors">
            <Search className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="bg-white rounded-[2rem] border border-slate-100 shadow-[0_8px_30px_rgb(0,0,0,0.02)] overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-bold tracking-wider">
            <tr>
              <th className="px-8 py-6">Référence</th>
              <th className="px-8 py-6">Date</th>
              <th className="px-8 py-6">Fournisseur</th>
              <th className="px-8 py-6">Montant</th>
              <th className="px-8 py-6">Statut</th>
              <th className="px-8 py-6">Analyse IA</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {data?.transactions.map((tx: Transaction) => (
              <tr key={tx.id} className="hover:bg-slate-50/50 transition-colors">
                <td className="px-8 py-5 font-bold text-slate-900 text-sm">{tx.reference}</td>
                <td className="px-8 py-5 text-sm text-slate-600">
                  {format(new Date(tx.date_transaction), 'dd MMM yyyy', { locale: fr })}
                </td>
                <td className="px-8 py-5 text-sm font-semibold text-slate-900">{tx.fournisseur}</td>
                <td className="px-8 py-5 font-bold text-slate-900">{tx.montant.toLocaleString()} FCFA</td>
                <td className="px-8 py-5">
                  <span className={`px-3 py-1 rounded-full text-[11px] font-bold uppercase ${
                    tx.statut === 'valide' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-600'
                  }`}>
                    {tx.statut}
                  </span>
                </td>
                <td className="px-8 py-5">
                  {tx.est_anomalie ? (
                    <div className="flex items-center space-x-2 text-rose-600 font-bold text-xs">
                      <AlertTriangle className="w-4 h-4" />
                      <span>{tx.score_risque}% Risque</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2 text-emerald-600 font-bold text-xs">
                      <ShieldCheck className="w-4 h-4" />
                      <span>Conforme</span>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Transactions;
