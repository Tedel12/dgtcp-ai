import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { anomaliesService } from '../api/anomalies';
import { 
  ArrowLeft, 
  AlertTriangle, 
  Clock, 
  User, 
  FileText, 
  ShieldAlert,
  ChevronRight,
  CheckCircle2,
  XCircle,
  MoreVertical,
  Info
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const AnomalieDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showConfirm, setShowConfirm] = useState<'valider' | 'rejeter' | null>(null);

  const { data: anomalie, isLoading, error } = useQuery({
    queryKey: ['anomalie', id],
    queryFn: () => anomaliesService.getById(id!),
    enabled: !!id,
  });

  const mutation = useMutation({
    mutationFn: (data: { statut: string, note_traitement?: string }) => 
      anomaliesService.updateStatut(id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['anomalie', id] });
      setShowConfirm(null);
      // On pourrait ajouter un toast ici
    },
  });

  if (isLoading) return (
    <div className="flex flex-col items-center justify-center h-[60vh] space-y-4">
      <div className="w-10 h-10 border-4 border-slate-900 border-t-transparent rounded-full animate-spin" />
      <p className="text-slate-400 text-sm font-medium animate-pulse">Chargement des données sécurisées...</p>
    </div>
  );
  
  if (error || !anomalie) return <div className="p-8 text-center text-red-500">Erreur lors de la récupération de l'anomalie.</div>;

  const getRiskColor = (niveau: string) => {
    switch (niveau) {
      case 'critique': return 'bg-red-500 text-white';
      case 'eleve': return 'bg-orange-500 text-white';
      case 'moyen': return 'bg-amber-400 text-white';
      default: return 'bg-slate-400 text-white';
    }
  };

  const handleAction = (statut: 'traitee' | 'archivee') => {
    mutation.mutate({ statut, note_traitement: `Action effectuée via le portail de contrôle.` });
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 md:space-y-8 animate-in pb-10">
      {/* Header Navigation - Mobile Optimized */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <button 
          onClick={() => navigate(-1)}
          className="group flex items-center space-x-2 text-slate-500 hover:text-slate-900 transition-colors w-fit"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          <span className="text-sm font-medium">Retour au flux</span>
        </button>
        <div className="hidden sm:flex items-center space-x-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
          <span>Contrôle</span>
          <ChevronRight className="w-3 h-3" />
          <span className="text-slate-900">{anomalie.reference}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 md:gap-8 items-start">
        {/* Main Content Area (Lg: 8/12) */}
        <div className="lg:col-span-8 space-y-6 md:space-y-8">
          <div className="bg-white rounded-3xl md:rounded-[2.5rem] border border-slate-100 shadow-sm overflow-hidden">
            <div className="p-6 md:p-10">
              {/* Badge + Title Row */}
              <div className="flex flex-wrap items-center gap-3 mb-6">
                <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter shadow-sm ${getRiskColor(anomalie.niveau_risque)}`}>
                  Niveau {anomalie.niveau_risque}
                </span>
                <span className="bg-slate-100 text-slate-600 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tighter">
                  IA SCORE: {anomalie.score_risque}%
                </span>
              </div>

              <div className="space-y-4">
                <h1 className="text-2xl md:text-3xl font-black text-slate-900 leading-tight">
                  Analyse de la transaction <span className="text-blue-600">#{anomalie.reference}</span>
                </h1>
                <div className="flex items-center space-x-2 text-slate-500">
                  <Clock className="w-4 h-4" />
                  <p className="text-sm font-medium">Détecté le {new Date(anomalie.detected_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
                </div>
              </div>

              <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
                <div className="bg-slate-50/50 p-6 rounded-2xl border border-slate-100 space-y-1">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Ministère Émetteur</p>
                  <p className="text-slate-900 font-bold">{anomalie.ministere || 'Inconnu'}</p>
                </div>
                <div className="bg-slate-50/50 p-6 rounded-2xl border border-slate-100 space-y-1">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Montant de l'opération</p>
                  <p className="text-slate-900 font-black text-xl">{anomalie.montant?.toLocaleString()} FCFA</p>
                </div>
              </div>

              <div className="mt-10 space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center space-x-2 text-slate-900">
                    <FileText className="w-5 h-5 text-blue-500" />
                    <h3 className="font-bold">Description de l'anomalie</h3>
                  </div>
                  <p className="text-slate-600 text-sm md:text-base leading-relaxed bg-white p-4 rounded-xl border border-slate-50">
                    {anomalie.description}
                  </p>
                </div>

                {anomalie.recommandation && (
                  <motion.div 
                    initial={{ opacity: 0, x: -10 }} 
                    animate={{ opacity: 1, x: 0 }}
                    className="p-5 rounded-2xl bg-orange-50 border border-orange-100 flex items-start space-x-4"
                  >
                    <ShieldAlert className="w-6 h-6 text-orange-500 shrink-0 mt-0.5" />
                    <div className="space-y-1">
                      <p className="text-orange-900 font-bold text-sm">Action recommandée par l'IA</p>
                      <p className="text-orange-800 text-sm leading-relaxed">{anomalie.recommandation}</p>
                    </div>
                  </motion.div>
                )}
              </div>
            </div>
          </div>
          
          {/* Mobile Action Buttons (sticky bottom on small screens) */}
          <div className="lg:hidden grid grid-cols-2 gap-4">
            <button 
              onClick={() => handleAction('traitee')}
              disabled={mutation.isPending}
              className="flex-1 bg-slate-900 text-white py-4 rounded-2xl text-sm font-bold flex items-center justify-center space-x-2 shadow-lg shadow-slate-200 active:scale-95 transition-all"
            >
              <CheckCircle2 className="w-4 h-4 text-green-400" />
              <span>Valider</span>
            </button>
            <button 
              onClick={() => handleAction('archivee')}
              disabled={mutation.isPending}
              className="flex-1 bg-white border border-red-100 text-red-600 py-4 rounded-2xl text-sm font-bold flex items-center justify-center space-x-2 shadow-sm active:scale-95 transition-all"
            >
              <XCircle className="w-4 h-4" />
              <span>Rejeter</span>
            </button>
          </div>
        </div>

        {/* Sidebar Actions (Lg: 4/12) - Visible only on Desktop */}
        <div className="hidden lg:block lg:col-span-4 space-y-6 sticky top-24">
          <div className="bg-slate-900 rounded-[2rem] p-8 text-white space-y-8 shadow-2xl shadow-slate-300">
            <div>
              <h3 className="text-lg font-bold">Actions de contrôle</h3>
              <p className="text-slate-400 text-xs mt-1 font-medium">Décision finale du régulateur</p>
            </div>
            
            <div className="space-y-3">
              <button 
                onClick={() => handleAction('traitee')}
                disabled={mutation.isPending}
                className="w-full bg-white text-slate-900 py-4 rounded-2xl text-sm font-black hover:bg-slate-50 transition-all flex items-center justify-center space-x-3 group"
              >
                {mutation.isPending && showConfirm === 'valider' ? (
                  <div className="w-4 h-4 border-2 border-slate-900 border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <CheckCircle2 className="w-5 h-5 text-green-500 group-hover:scale-110 transition-transform" />
                    <span>Valider la conformité</span>
                  </>
                )}
              </button>
              <button 
                onClick={() => handleAction('archivee')}
                disabled={mutation.isPending}
                className="w-full bg-red-500/10 border border-red-500/20 text-red-500 py-4 rounded-2xl text-sm font-black hover:bg-red-500 hover:text-white transition-all flex items-center justify-center space-x-3 group"
              >
                <XCircle className="w-5 h-5 group-hover:scale-110 transition-transform" />
                <span>Rejeter le paiement</span>
              </button>
            </div>
            
            <div className="pt-4 border-t border-white/10 text-center">
              <div className="inline-flex items-center space-x-2 text-[10px] text-slate-500 uppercase tracking-widest font-bold">
                <Info className="w-3 h-3" />
                <span>Validation requise sous 24h</span>
              </div>
            </div>
          </div>

          <div className="p-8 border border-slate-100 bg-white rounded-[2rem] space-y-6">
            <h4 className="font-bold text-sm text-slate-900 uppercase tracking-widest">Parcours d'audit</h4>
            <div className="space-y-8 relative before:absolute before:left-2 before:top-2 before:bottom-2 before:w-[1px] before:bg-slate-100">
              <div className="flex items-start space-x-4 relative pl-1">
                <div className="w-4 h-4 rounded-full bg-blue-500 border-4 border-white shadow-md shrink-0" />
                <div>
                  <p className="text-[11px] font-black text-slate-900 uppercase">Détection automatique</p>
                  <p className="text-[10px] text-slate-400 font-medium">{new Date(anomalie.detected_at).toLocaleTimeString()}</p>
                </div>
              </div>
              <div className="flex items-start space-x-4 relative pl-1 opacity-40">
                <div className="w-4 h-4 rounded-full bg-slate-200 border-4 border-white shrink-0" />
                <div>
                  <p className="text-[11px] font-black text-slate-900 uppercase tracking-tight">Analyse en cours</p>
                  <p className="text-[10px] text-slate-400 font-medium">Contrôleur en attente</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnomalieDetail;
