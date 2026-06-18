import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { 
  LayoutDashboard, 
  ArrowLeftRight, 
  AlertCircle, 
  TrendingUp, 
  Settings, 
  LogOut, 
  Search, 
  Bell,
  Menu,
  X,
  ShieldCheck,
  ChevronRight,
  User as UserIcon,
  Database
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { searchService, SearchResult } from '../api/search';
import { alertesService } from '../api/alertes';

const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(window.innerWidth > 1024);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [showSearch, setShowSearch] = useState(false);
  const [showNotifs, setShowNotifs] = useState(false);
  const [alertes, setAlertes] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  
  const navigate = useNavigate();
  const location = useLocation();
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const allMenuItems = [
    { name: 'Tableau de bord', path: '/dashboard', icon: LayoutDashboard, roles: ['directeur', 'comptable', 'auditeur', 'analyste_financier', 'controleur_financier'] },
    { name: 'Transactions', path: '/transactions', icon: ArrowLeftRight, roles: ['directeur', 'comptable', 'controleur_financier'] },
    { name: 'Anomalies', path: '/anomalies', icon: AlertCircle, roles: ['directeur', 'auditeur', 'analyste_financier', 'controleur_financier'] },
    { name: 'Prévisions', path: '/analyses', icon: TrendingUp, roles: ['directeur', 'analyste_financier'] },
    { name: 'Importation', path: '/import', icon: Database, roles: ['directeur', 'comptable'] },
    { name: 'Audit & Journal', path: '/audit', icon: ShieldCheck, roles: ['directeur', 'auditeur'] },
    { name: 'Gouvernance', path: '/gouvernance', icon: ShieldCheck, roles: ['admin', 'directeur'] },
    { name: 'Paramètres', path: '/settings', icon: Settings, roles: ['admin'] },
  ];

  const menuItems = allMenuItems.filter(item => item.roles.includes(user.role));

  // Fermer la sidebar sur mobile au changement de route
  useEffect(() => {
    if (window.innerWidth < 1024) {
      setIsSidebarOpen(false);
    }
  }, [location.pathname]);

  // Fetch notifications
  useEffect(() => {
    const fetchNotifs = async () => {
      try {
        const res = await alertesService.getRecentes();
        setAlertes(res.alertes);
        setUnreadCount(res.non_lues);
      } catch (err) {
        console.error("Failed to fetch notifications", err);
      }
    };
    fetchNotifs();
    const interval = setInterval(fetchNotifs, 30000); // Polling toutes les 30s
    return () => clearInterval(interval);
  }, []);

  // Search logic
  useEffect(() => {
    const delayDebounce = setTimeout(async () => {
      if (searchQuery.length >= 2) {
        const results = await searchService.search(searchQuery);
        setSearchResults(results);
        setShowSearch(true);
      } else {
        setSearchResults([]);
        setShowSearch(false);
      }
    }, 300);
    return () => clearTimeout(delayDebounce);
  }, [searchQuery]);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/auth');
  };

  const handleReadAll = async () => {
    try {
      await alertesService.marquerToutesLues();
      setAlertes(prev => prev.map(a => ({ ...a, est_lue: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error("Erreur lors du marquage des alertes", err);
    }
  };

  return (
    <div className="flex h-screen bg-[#F8FAFC] text-slate-900 font-sans overflow-hidden">
      {/* SIDEBAR - Mobile overlay logic */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsSidebarOpen(false)}
            className="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-40 lg:hidden"
          />
        )}
      </AnimatePresence>

      <motion.aside 
        initial={false}
        animate={{ 
          width: isSidebarOpen ? 280 : 0,
          x: isSidebarOpen ? 0 : -280,
          position: window.innerWidth < 1024 ? 'fixed' : 'relative'
        }}
        className={`bg-white border-r border-slate-200 flex flex-col z-50 h-full lg:translate-x-0 ${!isSidebarOpen && 'lg:w-20'}`}
      >
        <div className="h-20 flex items-center justify-between px-6 border-b border-slate-50">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center shrink-0">
              <ShieldCheck className="text-white w-6 h-6" />
            </div>
            {(isSidebarOpen || window.innerWidth < 1024) && (
              <span className="font-bold text-xl tracking-tight text-slate-900">DGTCP-AI</span>
            )}
          </div>
          <button onClick={() => setIsSidebarOpen(false)} className="lg:hidden p-2 hover:bg-slate-50 rounded-lg">
            <X className="w-5 h-5 text-slate-400" />
          </button>
        </div>
        
        {/* Navigation - adaptative */}
        <nav className="flex-1 overflow-y-auto py-6 px-4 space-y-2">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link 
                key={item.path} 
                to={item.path}
                className={`
                  flex items-center space-x-3 px-3 py-3 rounded-xl transition-all
                  ${isActive 
                    ? 'bg-slate-900 text-white shadow-lg shadow-slate-200' 
                    : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'}
                `}
              >
                <item.icon className="w-5 h-5 shrink-0" />
                {(isSidebarOpen || window.innerWidth < 1024) && <span className="font-medium text-sm">{item.name}</span>}
              </Link>
            );
          })}
        </nav>
        {/* ... reste du aside ... */}

        <div className="p-4 border-t border-slate-50">
          <button 
            onClick={handleLogout}
            className="flex items-center space-x-3 px-3 py-3 w-full rounded-xl text-red-500 hover:bg-red-50 transition-colors group"
          >
            <LogOut className="w-5 h-5 shrink-0" />
            {isSidebarOpen && <span className="font-medium text-sm">Déconnexion</span>}
          </button>
        </div>
      </motion.aside>

      {/* MAIN CONTENT */}
      <div className="flex-1 flex flex-col relative overflow-hidden">
        {/* TOP BAR */}
        <header className="h-20 bg-white border-b border-slate-200 flex items-center justify-between px-8 z-20">
          <div className="flex items-center flex-1 max-w-xl">
            <button 
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 hover:bg-slate-50 rounded-lg mr-4"
            >
              <Menu className="w-5 h-5 text-slate-500" />
            </button>

            {/* Global Search */}
            <div className="relative w-full">
              <div className="relative group">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                <input 
                  type="text"
                  placeholder="Rechercher une transaction, un fournisseur..."
                  className="w-full bg-slate-50 border border-slate-100 rounded-xl py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/10 focus:border-blue-500 transition-all"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              {/* Search Results Dropdown */}
              <AnimatePresence>
                {showSearch && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="absolute top-full mt-2 w-full bg-white rounded-2xl shadow-2xl border border-slate-100 overflow-hidden"
                  >
                    <div className="p-2">
                      {searchResults.length > 0 ? (
                        searchResults.map((res) => (
                          <button 
                            key={`${res.type}-${res.id}`}
                            onClick={() => { navigate(res.url); setShowSearch(false); setSearchQuery(''); }}
                            className="w-full text-left p-3 hover:bg-slate-50 rounded-xl flex items-center space-x-3 transition-colors"
                          >
                            <div className={`p-2 rounded-lg ${res.type === 'anomalie' ? 'bg-red-50 text-red-500' : 'bg-blue-50 text-blue-500'}`}>
                              {res.type === 'anomalie' ? <AlertCircle className="w-4 h-4" /> : <ArrowLeftRight className="w-4 h-4" />}
                            </div>
                            <div>
                              <p className="text-sm font-semibold text-slate-900">{res.title}</p>
                              <p className="text-xs text-slate-500">{res.subtitle}</p>
                            </div>
                          </button>
                        ))
                      ) : (
                        <div className="p-4 text-center text-sm text-slate-400">Aucun résultat trouvé</div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <div className="relative">
              <button 
                onClick={() => setShowNotifs(!showNotifs)}
                className="p-2.5 hover:bg-slate-50 rounded-xl relative group transition-colors"
              >
                <Bell className="w-5 h-5 text-slate-500 group-hover:text-slate-900" />
                {unreadCount > 0 && (
                  <span className="absolute top-2 right-2 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center border-2 border-white">
                    {unreadCount}
                  </span>
                )}
              </button>

              {/* Notifications Dropdown */}
              <AnimatePresence>
                {showNotifs && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    className="absolute right-0 mt-3 w-80 bg-white rounded-2xl shadow-2xl border border-slate-100 overflow-hidden"
                  >
                    <div className="p-4 border-b border-slate-50 flex items-center justify-between">
                      <div className="flex flex-col">
                        <h3 className="font-bold text-slate-900">Notifications</h3>
                        <span className="text-[10px] font-medium text-slate-400">{unreadCount} non lues</span>
                      </div>
                      <button 
                        onClick={handleReadAll}
                        className="text-[10px] font-black uppercase tracking-tighter text-blue-600 hover:text-blue-700 bg-blue-50 px-2 py-1 rounded-lg transition-colors"
                      >
                        Tout lire
                      </button>
                    </div>
                    <div className="max-h-[400px] overflow-y-auto">
                      {alertes.length > 0 ? (
                        alertes.map((alt) => (
                          <div 
                            key={alt.id} 
                            onClick={() => { navigate(`/anomalies/${alt.anomalie_id}`); setShowNotifs(false); }}
                            className="p-4 hover:bg-slate-50 border-b border-slate-50 last:border-0 transition-colors cursor-pointer group"
                          >
                            <div className="flex items-start space-x-3">
                              <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${alt.niveau === 'critique' ? 'bg-red-500' : 'bg-orange-400'}`} />
                              <div className="flex-1">
                                <p className="text-sm font-semibold text-slate-900">{alt.titre}</p>
                                <p className="text-xs text-slate-500 line-clamp-2 mt-0.5">{alt.message}</p>
                                <p className="text-[10px] text-slate-400 mt-2 uppercase font-medium">{new Date(alt.created_at).toLocaleTimeString()}</p>
                              </div>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="p-8 text-center text-slate-400 text-sm italic">Aucune notification</div>
                      )}
                    </div>
                    <Link to="/anomalies" className="block p-3 text-center text-xs font-semibold text-blue-600 bg-blue-50/50 hover:bg-blue-100 transition-colors">
                      Voir toutes les anomalies
                    </Link>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Profile */}
            <div className="flex items-center space-x-3 pl-4 border-l border-slate-200">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-bold text-slate-900">{user.prenom} {user.nom}</p>
                <p className="text-[11px] font-medium text-slate-500 uppercase tracking-wide">{user.role?.replace('_', ' ')}</p>
              </div>
              <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center border border-slate-200 overflow-hidden">
                {user.avatar_url ? (
                  <img src={user.avatar_url} alt="avatar" className="w-full h-full object-cover" />
                ) : (
                  <UserIcon className="w-5 h-5 text-slate-400" />
                )}
              </div>
            </div>
          </div>
        </header>

        {/* PAGE CONTENT */}
        <main className="flex-1 overflow-y-auto p-8">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
