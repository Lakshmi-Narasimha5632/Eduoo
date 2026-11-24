import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';

// Pages
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { Platforms } from './pages/Platforms';
import { Tasks } from './pages/Tasks';
import { Analytics } from './pages/Analytics';
import { Insights } from './pages/Insights';
import { Recommendations } from './pages/Recommendations';
import { Resume } from './pages/Resume';
import { MockInterviews } from './pages/MockInterviews';
import { InterviewRoom } from './pages/InterviewRoom';
import { InterviewResult } from './pages/InterviewResult';
import { Profile } from './pages/Profile';
import { RefreshCw } from 'lucide-react';

const ProtectedLayout = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-400">
        <div className="w-12 h-12 rounded-2xl bg-brand-600 flex items-center justify-center text-white font-extrabold text-2xl shadow-xl shadow-brand-500/30 mb-4 animate-pulse">
          E
        </div>
        <RefreshCw className="w-5 h-5 animate-spin text-brand-400 mb-2" />
        <p className="text-xs font-semibold tracking-wider uppercase text-slate-500">
          Loading Eduoo AI Core...
        </p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-brand-500 selection:text-white">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main App Container */}
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />
        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export const App = () => {
  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Application Routes */}
            <Route element={<ProtectedLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/platforms" element={<Platforms />} />
              <Route path="/tasks" element={<Tasks />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/insights" element={<Insights />} />
              <Route path="/recommendations" element={<Recommendations />} />
              <Route path="/resume" element={<Resume />} />
              <Route path="/interviews" element={<MockInterviews />} />
              <Route path="/interviews/:id" element={<InterviewRoom />} />
              <Route path="/interviews/:id/result" element={<InterviewResult />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  );
};

export default App;
