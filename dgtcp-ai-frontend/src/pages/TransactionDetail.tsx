import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { transactionsService } from '../api/transactions';
import { 
  ArrowLeft, 
  ArrowLeftRight,
  Building2,
  Calendar,
  CreditCard,
  Hash,
  ChevronRight,
  ShieldCheck,
  AlertTriangle,
  User
} from 'lucide-react';

const TransactionDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: transaction, isLoading, error } = useQuery({
    queryKey: ['transaction', id],
    queryFn: () => transactionsService.getById(id!),
    enabled: !!id,
  });

  const { data: anomalies } = useQuery({
    queryKey: ['transaction-anomalies', id],
    queryFn: () => transactionsService.getAnomalies(id!),
    enabled: !!id,
  });

  if (isLoading) return <div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" /></div>;
  if (error || !transaction) return <div className="p-8 text-center text-red-500">Erreur lors de la récupération de la transaction.</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in">
      {/* Header Navigation */}
      <div className="flex items-center justify-between">
        <button 
          onClick={() => navigate(-1)}
          className="group flex items-center space-x-2 text-slate-500 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          <span className="text-sm font-medium">Retour</span>
        </button>
        <div className="flex items-center space-x-2 text-xs font-medium text-slate-400 uppercase tracking-wider">
          <span>Plateforme</span>
          <ChevronRight className="w-3 h-3" />
          <span>Transactions</span>
          <ChevronRight className="w-3 h-3" />
          <span className="text-slate-900">{transaction.reference}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Transaction Info */}
        <div className="lg:col-span-2 space-y-8">
          <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm p-10 space-y-10">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <h1 className="text-2xl font-bold text-slate-900">Détails du paiement</h1>
                <p className="text-slate-500 text-sm">Référence : {transaction.reference}</p>
              </div>
              <div className={`p-4 rounded-2xl ${transaction.est_anomalie ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}>
                {transaction.est_anomalie ? <AlertTriangle className="w-6 h-6" /> : <ShieldCheck className="w-6 h-6" />}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-y-10 gap-x-6">
              <div className="space-y-1">
                <div className="flex items-center space-x-2 text-slate-400 mb-1">
                  <Building2 className="w-3.5 h-3.5" />
                  <span className="text-[10px] font-bold uppercase tracking-widest">Ministère</span>
                </div>
                <p className="font-bold text-slate-900">{transaction.ministere}</p>
              </div>
              <div className="space-y-1">
                <div className="flex items-center space-x-2 text-slate-400 mb-1">
                  <User className="w-3.5 h-3.5" />
                  <span className="text-[10px] font-bold uppercase tracking-widest">Fournisseur</span>
                </div>
                <p className="font-bold text-slate-900">{transaction.fournisseur}</p>
              </div>
              <div className="space-y-1">
                <div className="flex items-center space-x-2 text-slate-400 mb-1">
                  <Calendar className="w-3.5 h-3.5" />
                  <span className="text-[10px] font-bold uppercase tracking-widest">Date transaction</span>
                </div>
                <p className="font-bold text-slate-900">{new Date(transaction.date_transaction).toLocaleDateString()}</p>
              </div>
              <div className="space-y-1">
                <div className="flex items-center space-x-2 text-slate-400 mb-1">
                  <CreditCard className="w-3.5 h-3.5" />
                  <span className="text-[10px] font-bold uppercase tracking-widest">Méthode</span>
                </div>
                <p className="font-bold text-slate-900 capitalize">{transaction.type_transaction}</p>
              </div>
            </div>

            <div className="pt-10 border-t border-slate-50 flex items-end justify-between">
              <div>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Montant décaissé</p>
                <p className="text-4xl font-black text-slate-900">{transaction.montant?.toLocaleString()} <span className="text-lg font-medium text-slate-400">FCFA</span></p>
              </div>
              <div className="text-right">
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Score de risque</p>
                <p className={`text-2xl font-black ${transaction.score_risque > 70 ? 'text-red-500' : 'text-green-500'}`}>{transaction.score_risque}%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Linked Anomalies */}
        <div className="space-y-6">
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-widest ml-2">Anomalies liées</h3>
          {anomalies && anomalies.length > 0 ? (
            anomalies.map((an) => (
              <button 
                key={an.id}
                onClick={() => navigate(`/anomalies/${an.id}`)}
                className="w-full bg-white p-6 rounded-3xl border border-slate-100 shadow-sm hover:border-blue-200 hover:shadow-md transition-all text-left group"
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="px-3 py-1 bg-red-50 text-red-600 rounded-full text-[10px] font-bold uppercase tracking-wider">{an.type_anomalie?.replace('_', ' ')}</span>
                  <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-blue-500 transition-colors" />
                </div>
                <p className="text-sm font-bold text-slate-900 line-clamp-2 mb-2">{an.description}</p>
                <p className="text-[10px] text-slate-400 font-medium">Détectée le {new Date(an.detected_at).toLocaleDateString()}</p>
              </button>
            ))
          ) : (
            <div className="bg-green-50/50 p-10 rounded-[2.5rem] border border-green-100 text-center">
              <ShieldCheck className="w-10 h-10 text-green-500 mx-auto mb-4" />
              <p className="text-sm font-bold text-green-700">Aucune anomalie</p>
              <p className="text-xs text-green-600/70 mt-1">Transaction saine et conforme.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TransactionDetail;
