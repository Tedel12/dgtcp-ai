import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, User, Briefcase, ArrowRight, ShieldCheck } from 'lucide-react';
import { authService } from '../api/auth';
import { useNavigate } from 'react-router-dom';

const Auth: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Form State
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    nom: '',
    prenom: '',
    poste: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (error) setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      let response;
      if (isLogin) {
        response = await authService.login({
          email: formData.email,
          password: formData.password,
        });
      } else {
        response = await authService.signup({
          email: formData.email,
          password: formData.password,
          nom: formData.nom,
          prenom: formData.prenom,
          poste: formData.poste,
        });
      }

      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.utilisateur));
      
      // Animation de succès puis redirection
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || "Une erreur est survenue lors de l'authentification");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#F8FAFC] flex items-center justify-center p-4 font-sans">
      {/* Background Decor - Subtil */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-5%] w-[40%] h-[40%] rounded-full bg-blue-50/50 blur-3xl" />
        <div className="absolute bottom-[-5%] right-[-5%] w-[30%] h-[30%] rounded-full bg-slate-100 blur-3xl" />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="w-full max-w-[460px] z-10"
      >
        <div className="bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 overflow-hidden">
          {/* Header */}
          <div className="p-8 pb-4 text-center">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-slate-900 mb-6 shadow-lg shadow-slate-200">
              <ShieldCheck className="text-white w-7 h-7" />
            </div>
            <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">
              DGTCP-AI
            </h1>
            <p className="text-slate-500 mt-2 text-sm">
              {isLogin 
                ? "Plateforme intelligente de détection des anomalies" 
                : "Créez votre compte d'analyste financier"}
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-8 pt-4 space-y-4">
            <AnimatePresence mode="wait">
              {!isLogin && (
                <motion.div 
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="grid grid-cols-2 gap-4 overflow-hidden"
                >
                  <div className="space-y-1.5">
                    <label className="text-[13px] font-medium text-slate-700 ml-1">Nom</label>
                    <div className="relative group">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                      <input 
                        name="nom"
                        value={formData.nom}
                        onChange={handleChange}
                        className="w-full bg-slate-50 border border-slate-100 rounded-xl py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/10 focus:border-blue-500 transition-all"
                        placeholder="Zannou"
                        required={!isLogin}
                      />
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[13px] font-medium text-slate-700 ml-1">Prénom</label>
                    <div className="relative group">
                      <input 
                        name="prenom"
                        value={formData.prenom}
                        onChange={handleChange}
                        className="w-full bg-slate-50 border border-slate-100 rounded-xl py-2.5 px-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/10 focus:border-blue-500 transition-all"
                        placeholder="Romuald"
                        required={!isLogin}
                      />
                    </div>
                  </div>
                  <div className="col-span-2 space-y-1.5">
                    <label className="text-[13px] font-medium text-slate-700 ml-1">Poste occupé</label>
                    <div className="relative group">
                      <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                      <input 
                        name="poste"
                        value={formData.poste}
                        onChange={handleChange}
                        className="w-full bg-slate-50 border border-slate-100 rounded-xl py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/10 focus:border-blue-500 transition-all"
                        placeholder="Analyste budgétaire"
                      />
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="space-y-1.5">
              <label className="text-[13px] font-medium text-slate-700 ml-1">Adresse Email</label>
              <div className="relative group">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                <input 
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-100 rounded-xl py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/10 focus:border-blue-500 transition-all"
                  placeholder="r.zannou@dgtcp.bj"
                  required
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between ml-1">
                <label className="text-[13px] font-medium text-slate-700">Mot de passe</label>
                {isLogin && (
                  <button type="button" className="text-[12px] text-blue-600 font-medium hover:underline">Oublié ?</button>
                )}
              </div>
              <div className="relative group">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                <input 
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-100 rounded-xl py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/10 focus:border-blue-500 transition-all"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {error && (
              <motion.div 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="p-3 rounded-xl bg-red-50 border border-red-100 text-red-600 text-xs font-medium"
              >
                {error}
              </motion.div>
            )}

            <button 
              type="submit"
              disabled={loading}
              className="w-full bg-slate-900 text-white rounded-xl py-3 text-sm font-semibold shadow-lg shadow-slate-200 hover:bg-slate-800 active:scale-[0.98] transition-all flex items-center justify-center space-x-2 disabled:opacity-70 disabled:active:scale-100"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <span>{isLogin ? "Se connecter" : "Créer mon compte"}</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Footer Toggle */}
          <div className="p-6 bg-slate-50/50 border-t border-slate-100 text-center">
            <button 
              onClick={() => setIsLogin(!isLogin)}
              className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
            >
              {isLogin 
                ? "Vous n'avez pas de compte ? " 
                : "Vous avez déjà un compte ? "}
              <span className="font-semibold text-blue-600 underline-offset-4 hover:underline">
                {isLogin ? "S'inscrire" : "Se connecter"}
              </span>
            </button>
          </div>
        </div>
        
        <p className="text-center text-slate-400 text-[11px] mt-8 uppercase tracking-[0.1em] font-medium">
          Direction Générale du Trésor et de la Comptabilité Publique — Bénin
        </p>
      </motion.div>
    </div>
  );
};

export default Auth;
