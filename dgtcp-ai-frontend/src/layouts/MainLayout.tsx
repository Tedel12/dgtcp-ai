import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LayoutDashboard, 
  ReceiptEuro, 
  AlertTriangle, 
  BarChart3, 
  Users, 
  Settings, 
  LogOut, 
  Menu, 
  X, 
  Bell, 
  Search,
  User,
  ShieldCheck,
  Upload
} from 'lucide-react';

interface SidebarItemProps {
  icon: any;
  label: string;
  path: string;
  active: boolean;
  collapsed: boolean;
}

const SidebarItem = ({ icon: Icon, label, path, active, collapsed }: SidebarItemProps) => (
  <Link to={path}>
    <motion.div 
      whileHover={{ x: 4 }}
      className={`flex items-center px-4 py-3 rounded-2xl cursor-pointer transition-all duration-200 group ${
        active 
          ? 'bg-slate-900 text-white shadow-lg shadow-slate-200' 
          : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
      }`}
    >
      <Icon className={`w-5 h-5 ${active ? 'text-white' : 'text-slate-400 group-hover:text-slate-900'} transition-colors`} />
      {!collapsed && (
        <span className="ml-3 font-medium text-[14.5px] whitespace-nowrap">{label}</span>
      )}
      {active && !collapsed && (
        <motion.div layoutId="active-pill" className="ml-auto w-1.5 h-1.5 rounded-full bg-blue-400" />
      )}
    </motion.div>
  </Link>
);

const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [user, setUser] = useState<any>(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) setUser(JSON.parse(savedUser));
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/auth');
  };

  const menuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
    { icon: ReceiptEuro, label: 'Transactions', path: '/transactions' },
    { icon: AlertTriangle, label: 'Anomalies', path: '/anomalies' },
    { icon: BarChart3, label: 'Analyses IA', path: '/analyses' },
    { icon: Users, label: 'Gouvernance', path: '/gouvernance' },
    { icon: Upload, label: 'Importation', path: '/import' },
  ];

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      {/* Sidebar */}
      <motion.aside 
        initial={false}
        animate={{ width: collapsed ? 88 : 280 }}
        className="fixed inset-y-0 left-0 bg-white border-r border-slate-100 z-50 flex flex-col transition-all duration-300 ease-in-out"
      >
        <div className="h-24 flex items-center px-7">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center shadow-lg shadow-slate-200">
              <ShieldCheck className="text-white w-6 h-6" />
            </div>
            {!collapsed && (
              <motion.span 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="font-bold text-xl tracking-tight text-slate-900"
              >
                DGTCP-AI
              </motion.span>
            )}
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-2">
          {menuItems.map((item) => (
            <SidebarItem 
              key={item.path}
              {...item}
              active={location.pathname === item.path}
              collapsed={collapsed}
            />
          ))}
        </nav>

        <div className="p-4 border-t border-slate-100 space-y-2">
          <SidebarItem 
            icon={Settings} 
            label="Paramètres" 
            path="/settings" 
            active={location.pathname === '/settings'} 
            collapsed={collapsed}
          />
          <button 
            onClick={handleLogout}
            className="w-full flex items-center px-4 py-3 rounded-2xl text-red-500 hover:bg-red-50 transition-colors group"
          >
            <LogOut className="w-5 h-5" />
            {!collapsed && <span className="ml-3 font-medium text-[14.5px]">Déconnexion</span>}
          </button>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className={`flex-1 flex flex-col transition-all duration-300 ${collapsed ? 'ml-[88px]' : 'ml-[280px]'}`}>
        <header className="h-20 bg-white/80 backdrop-blur-md border-b border-slate-100 sticky top-0 z-40 px-8 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button 
              onClick={() => setCollapsed(!collapsed)}
              className="p-2.5 rounded-xl hover:bg-slate-50 text-slate-500 transition-colors"
            >
              {collapsed ? <Menu className="w-5 h-5" /> : <X className="w-5 h-5" />}
            </button>
            <div className="hidden md:flex items-center px-4 py-2 bg-slate-50 rounded-2xl border border-slate-100 group focus-within:ring-4 focus-within:ring-blue-500/5 focus-within:border-blue-500 transition-all">
              <Search className="w-4 h-4 text-slate-400" />
              <input 
                placeholder="Rechercher une transaction..." 
                className="bg-transparent border-none outline-none ml-3 text-sm w-64 placeholder:text-slate-400"
              />
            </div>
          </div>

          <div className="flex items-center space-x-5">
            <button className="relative p-2.5 rounded-xl hover:bg-slate-50 text-slate-500 transition-all active:scale-95 group">
              <Bell className="w-5 h-5 group-hover:text-slate-900 transition-colors" />
              <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white shadow-sm" />
            </button>

            <div className="h-8 w-[1px] bg-slate-100" />

            <div className="flex items-center space-x-4 pl-2 cursor-pointer group">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-semibold text-slate-900 group-hover:text-blue-600 transition-colors capitalize">
                  {user ? `${user.prenom} ${user.nom}` : 'Chargement...'}
                </p>
                <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                  {user?.role?.replace('_', ' ') || 'Utilisateur'}
                </p>
              </div>
              <div className="w-11 h-11 rounded-2xl bg-slate-100 border border-slate-200 flex items-center justify-center overflow-hidden shadow-sm group-hover:border-blue-200 transition-all">
                <User className="w-6 h-6 text-slate-400" />
              </div>
            </div>
          </div>
        </header>

        <div className="p-8 flex-1">
          {children}
        </div>
      </main>
    </div>
  );
};

export default MainLayout;
