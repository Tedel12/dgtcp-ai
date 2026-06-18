import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Auth from './pages/Auth';
import Dashboard from './pages/Dashboard';
import Anomalies from './pages/Anomalies';
import Transactions from './pages/Transactions';
import Previsions from './pages/Previsions';
import Gouvernance from './pages/Gouvernance';
import Settings from './pages/Settings';
import DataImport from './pages/DataImport';
import MainLayout from './layouts/MainLayout';
import Audit from './pages/Audit';

import AnomalieDetail from './pages/AnomalieDetail';
import TransactionDetail from './pages/TransactionDetail';

interface ProtectedRouteProps {
  children: React.ReactNode;
  roles?: string[];
}

const ProtectedRoute = ({ children, roles }: ProtectedRouteProps) => {
  const token = localStorage.getItem('token');
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  
  if (!token) return <Navigate to="/auth" replace />;
  
  if (roles && !roles.includes(user.role)) {
    // Si l'admin tente d'aller ailleurs, on le remet sur gouvernance
    const redirectPath = user.role === 'admin' ? '/gouvernance' : '/dashboard';
    return <Navigate to={redirectPath} replace />;
  }
  
  return <MainLayout>{children}</MainLayout>;
};

const App: React.FC = () => {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const defaultRoute = user.role === 'admin' ? '/gouvernance' : '/dashboard';

  return (
    <Router>
      <Routes>
        <Route path="/auth" element={<Auth />} />
        
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute roles={['directeur', 'comptable', 'auditeur', 'analyste_financier', 'controleur_financier']}>
              <Dashboard />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/transactions" 
          element={<ProtectedRoute roles={['directeur', 'comptable', 'controleur_financier']}><Transactions /></ProtectedRoute>} 
        />
        <Route 
          path="/transactions/:id" 
          element={<ProtectedRoute roles={['directeur', 'comptable', 'controleur_financier']}><TransactionDetail /></ProtectedRoute>} 
        />

        <Route 
          path="/anomalies" 
          element={<ProtectedRoute roles={['directeur', 'auditeur', 'analyste_financier', 'controleur_financier']}><Anomalies /></ProtectedRoute>} 
        />
        <Route 
          path="/anomalies/:id" 
          element={<ProtectedRoute roles={['directeur', 'auditeur', 'analyste_financier', 'controleur_financier']}><AnomalieDetail /></ProtectedRoute>} 
        />

        <Route 
          path="/analyses" 
          element={
            <ProtectedRoute roles={['directeur', 'analyste_financier']}>
              <Previsions />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/audit" 
          element={
            <ProtectedRoute roles={['directeur', 'auditeur']}>
              <Audit />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/gouvernance" 
          element={
            <ProtectedRoute roles={['admin', 'directeur']}>
              <Gouvernance />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/settings" 
          element={
            <ProtectedRoute roles={['admin']}>
              <Settings />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/import" 
          element={
            <ProtectedRoute roles={['directeur', 'comptable']}>
              <DataImport />
            </ProtectedRoute>
          } 
        />

        <Route path="/" element={<Navigate to={defaultRoute} replace />} />
      </Routes>
    </Router>
  );
};

export default App;
