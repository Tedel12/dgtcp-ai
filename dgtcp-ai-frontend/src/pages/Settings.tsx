import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, Save, ShieldCheck } from 'lucide-react';
import api from '../api/client';

const Settings: React.FC = () => {
  const [passwords, setPasswords] = useState({ old: '', new: '' });
  const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null);

  const mutation = useMutation({
    mutationFn: (data: { old_password: string; new_password: string }) => 
      api.patch('/auth/password', data),
    onSuccess: () => {
      setMessage({ text: 'Mot de passe mis à jour', type: 'success' });
      setPasswords({ old: '', new: '' });
      setTimeout(() => setMessage(null), 3000);
    },
    onError: () => {
      setMessage({ text: 'Erreur lors de la mise à jour', type: 'error' });
      setTimeout(() => setMessage(null), 3000);
    }
  });

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h2 className="text-2xl font-bold text-slate-900">Paramètres de sécurité</h2>
      
      <div className="bg-white p-8 rounded-[2rem] border border-slate-100 shadow-[0_8px_30px_rgb(0,0,0,0.02)]">
        <div className="flex items-center space-x-4 mb-8">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl">
            <Lock className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900">Mot de passe</h3>
            <p className="text-sm text-slate-500">Mettre à jour votre accès sécurisé</p>
          </div>
        </div>

        <form className="space-y-4" onSubmit={(e) => {
          e.preventDefault();
          mutation.mutate({ old_password: passwords.old, new_password: passwords.new });
        }}>
          <input 
            type="password" placeholder="Mot de passe actuel"
            className="w-full bg-slate-50 border border-slate-100 rounded-xl py-3 px-4 text-sm focus:ring-2 focus:ring-blue-500/20"
            value={passwords.old}
            onChange={(e) => setPasswords({...passwords, old: e.target.value})}
          />
          <input 
            type="password" placeholder="Nouveau mot de passe"
            className="w-full bg-slate-50 border border-slate-100 rounded-xl py-3 px-4 text-sm focus:ring-2 focus:ring-blue-500/20"
            value={passwords.new}
            onChange={(e) => setPasswords({...passwords, new: e.target.value})}
          />
          
          <button 
            type="submit"
            className="bg-slate-900 text-white rounded-xl py-3 px-6 text-sm font-bold hover:bg-slate-800 transition-all flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Mettre à jour</span>
          </button>
        </form>

        <AnimatePresence>
            {message && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className={`mt-4 p-4 rounded-xl text-sm font-bold ${message.type === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'}`}>
                    {message.text}
                </motion.div>
            )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default Settings;
