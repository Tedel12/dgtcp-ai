import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Upload, CheckCircle } from 'lucide-react';
import api from '../api/client';
import { useNavigate } from 'react-router-dom';

const DataImport: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const navigate = useNavigate();

  const mutation = useMutation({
    mutationFn: (formData: FormData) => api.post('/data/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    onSuccess: () => {
      // Redirection automatique vers le centre d'anomalies après 2 secondes
      setTimeout(() => navigate('/anomalies'), 2000);
    }
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setFile(e.target.files[0]);
  };

  const handleUpload = () => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    mutation.mutate(formData);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h2 className="text-2xl font-bold text-slate-900">Importation de Données (SIGFIP/ASTER)</h2>
      
      <div className="bg-white p-10 rounded-[2rem] border border-slate-100 shadow-[0_8px_30px_rgb(0,0,0,0.02)] text-center">
        <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
          <Upload className="w-8 h-8 text-blue-600" />
        </div>
        
        <input type="file" accept=".csv" onChange={handleFileChange} className="hidden" id="fileInput" />
        <label htmlFor="fileInput" className="cursor-pointer block text-sm font-bold text-slate-900 hover:text-blue-600">
          {file ? file.name : "Cliquez ici pour sélectionner un fichier CSV"}
        </label>
        
        <button 
          onClick={handleUpload}
          disabled={!file || mutation.isPending}
          className="mt-8 bg-slate-900 text-white px-8 py-3 rounded-xl font-bold text-sm hover:bg-slate-800 transition-all disabled:opacity-50"
        >
          {mutation.isPending ? "Analyse en cours..." : "Lancer l'analyse IA"}
        </button>

        {mutation.isSuccess && (
          <div className="mt-6 p-4 bg-emerald-50 rounded-xl text-emerald-700 text-sm font-bold flex flex-col items-center justify-center space-y-2">
            <CheckCircle className="w-8 h-8" />
            <p>Importation réussie !</p>
            <p className="text-xs">{mutation.data.data.transactions_traitees} transactions traitées, {mutation.data.data.anomalies_detectees} anomalies détectées.</p>
            <p className="text-xs font-medium text-emerald-600">Redirection vers le centre de traitement...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DataImport;
