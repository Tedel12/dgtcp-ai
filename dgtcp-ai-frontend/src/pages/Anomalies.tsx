import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle, 
  XCircle, 
  Filter,
  Download
} from 'lucide-react';
import api from '../api/client';
import { StatutAnomalie, NiveauRisque } from '../types/anomalie';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

const Anomalies: React.FC = () => {
  const [filter, setFilter] = useState('');
  const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['anomalies', filter],
    queryFn: async () => {
      const res = await api.get('/anomalies', { params: { statut: filter || undefined } });
      return res.data;
    }
  });

  const handleExport = async (format: 'excel' | 'csv') => {
    try {
      const response = await api.get(`/rapports/export/anomalies?format=${format}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `anomalies_dgtcp.${format === 'excel' ? 'xlsx' : 'csv'}`);
      document.body.appendChild(link);
      link.click();
    } catch (err) {
      console.error("Erreur lors de l'export", err);
    }
  };

  const mutation = useMutation({
    mutationFn: (data: { id: number, statut: StatutAnomalie, note_traitement: string }) => 
      api.patch(`/anomalies/${data.id}`, { statut: data.statut, note_traitement: data.note_traitement }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['anomalies'] });
      setMessage({ text: 'Anomalie traitée avec succès', type: 'success' });
      setTimeout(() => setMessage(null), 3000);
    },
    onError: () => {
      setMessage({ text: 'Erreur lors du traitement', type: 'error' });
      setTimeout(() => setMessage(null), 3000);
    }
  });

  const getRiskColor = (niveau: NiveauRisque) => {
    switch (niveau) {
      case NiveauRisque.CRITIQUE: return 'bg-rose-500 text-white';
      case NiveauRisque.ELEVE: return 'bg-orange-500 text-white';
      case NiveauRisque.MOYEN: return 'bg-amber-400 text-white';
      default: return 'bg-slate-200 text-slate-700';
    }
  };

  if (isLoading) return <div className="text-center py-20 font-bold text-slate-500">Chargement des anomalies...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-slate-900">Centre de Traitement des Anomalies</h2>
        <div className="flex items-center space-x-3">
          <select 
            className="bg-white border border-slate-200 rounded-xl px-4 py-2 text-sm font-semibold outline-none focus:ring-2 focus:ring-blue-500/20"
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="">Tous les statuts</option>
            <option value={StatutAnomalie.NON_TRAITE}>Non traitées</option>
            <option value={StatutAnomalie.TRAITE}>Traitées (Validées)</option>
            <option value={StatutAnomalie.FAUX_POSITIF}>Faux Positifs (Rejetées)</option>
          </select>
          <button 
            onClick={() => handleExport('excel')}
            className="p-2.5 bg-white border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 transition-all title='Exporter en Excel'"
          >
            <Download className="w-5 h-5" />
          </button>
        </div>
      </div>

      <AnimatePresence>
        {message && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className={`p-4 rounded-2xl text-sm font-bold ${message.type === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'}`}
          >
            {message.text}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="bg-white rounded-[2rem] border border-slate-100 shadow-[0_8px_30px_rgb(0,0,0,0.02)] overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-bold tracking-wider">
            <tr>
              <th className="px-8 py-6">Référence</th>
              <th className="px-8 py-6">Type</th>
              <th className="px-8 py-6">Risque</th>
              <th className="px-8 py-6">Détails</th>
              <th className="px-8 py-6 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {data?.anomalies.map((anom: any) => (
              <tr key={anom.id} className="hover:bg-slate-50/50 transition-colors">
                <td className="px-8 py-5 font-bold text-slate-900 text-sm">{anom.reference}</td>
                <td className="px-8 py-5">
                  <span className={`px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wide ${
                    anom.type_anomalie === 'trop_percu' ? 'bg-orange-100 text-orange-700' : 'bg-slate-100 text-slate-600'
                  }`}>
                    {anom.type_anomalie.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-8 py-5">
                  <span className={`px-3 py-1 rounded-full text-[11px] font-bold uppercase ${getRiskColor(anom.niveau_risque)}`}>
                    {anom.niveau_risque}
                  </span>
                </td>
                <td className="px-8 py-5 text-sm">
                  <p className="font-semibold text-slate-900">{anom.montant?.toLocaleString()} FCFA</p>
                  <p className="text-slate-400 text-xs">{anom.fournisseur}</p>
                </td>
                <td className="px-8 py-5 text-right">
                  {anom.statut === StatutAnomalie.NON_TRAITE && (
                    <div className="flex justify-end space-x-2">
                      <button 
                        onClick={() => mutation.mutate({ id: anom.id, statut: StatutAnomalie.TRAITE, note_traitement: "Validé par analyste" })}
                        className="p-2 bg-emerald-50 text-emerald-600 rounded-xl hover:bg-emerald-100 transition-all"
                        title="Valider"
                      >
                        <CheckCircle className="w-5 h-5" />
                      </button>
                      <button 
                        onClick={() => mutation.mutate({ id: anom.id, statut: StatutAnomalie.FAUX_POSITIF, note_traitement: "Faux positif" })}
                        className="p-2 bg-rose-50 text-rose-600 rounded-xl hover:bg-rose-100 transition-all"
                        title="Rejeter"
                      >
                        <XCircle className="w-5 h-5" />
                      </button>
                    </div>
                  )}
                  {anom.statut !== StatutAnomalie.NON_TRAITE && (
                    <span className="text-xs font-bold text-slate-400 uppercase bg-slate-100 px-3 py-1 rounded-full">
                      {anom.statut.replace('_', ' ')}
                    </span>
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

export default Anomalies;
