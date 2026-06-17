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

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('token');
  if (!token) return <Navigate to="/auth" replace />;
  return <MainLayout>{children}</MainLayout>;
};

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/auth" element={<Auth />} />
        
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/transactions" 
          element={
            <ProtectedRoute>
              <Transactions />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/anomalies" 
          element={
            <ProtectedRoute>
              <Anomalies />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/analyses" 
          element={
            <ProtectedRoute>
              <Previsions />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/gouvernance" 
          element={
            <ProtectedRoute>
              <Gouvernance />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/settings" 
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/import" 
          element={
            <ProtectedRoute>
              <DataImport />
            </ProtectedRoute>
          } 
        />

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
};

export default App;
