import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Cpu,
  CheckSquare,
  BarChart3,
  Lightbulb,
  Sparkles,
  FileText,
  User,
  LogOut,
  ShieldCheck,
  Bot,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const navItems = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Platforms', path: '/platforms', icon: Cpu },
  { name: 'Daily Tasks', path: '/tasks', icon: CheckSquare },
  { name: 'Analytics', path: '/analytics', icon: BarChart3 },
  { name: 'Insights', path: '/insights', icon: Lightbulb },
  { name: 'Recommendations', path: '/recommendations', icon: Sparkles },
  { name: 'Resume & ATS', path: '/resume', icon: FileText },
  { name: 'Interviews & Prep', path: '/interviews', icon: Bot, isNew: true },
  { name: 'Profile & Goals', path: '/profile', icon: User },
];

export const Sidebar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <aside className="w-64 bg-slate-900/90 border-r border-slate-800 flex flex-col justify-between shrink-0 min-h-screen">
      <div>
        {/* Brand Logo */}
        <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-800">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-400 flex items-center justify-center text-white font-bold shadow-lg shadow-brand-500/30">
            E
          </div>
          <div>
            <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              EDUOO
            </span>
            <span className="text-[10px] block font-semibold text-brand-400 -mt-1 tracking-widest uppercase">
              AI Career Mentor
            </span>
          </div>
        </div>

        {/* User Snapshot */}
        {user && (
          <div className="p-4 mx-3 my-3 rounded-xl bg-slate-800/60 border border-slate-700/50">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Target Goal</div>
            <div className="text-sm font-bold text-white truncate mt-0.5">{user.target_role || 'Software Engineer'}</div>
            <div className="flex items-center gap-2 mt-2 text-xs text-brand-300">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Career Track Active</span>
            </div>
          </div>
        )}

        {/* Navigation Links */}
        <nav className="px-3 space-y-1 mt-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-brand-600 text-white shadow-md shadow-brand-600/30 font-semibold'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span className="flex-1 truncate">{item.name}</span>
                {item.isNew && (
                  <span className="text-[9px] font-black tracking-widest uppercase px-1.5 py-0.5 rounded-md bg-gradient-to-r from-brand-500 to-indigo-500 text-white shadow-sm">
                    AI
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer / Logout */}
      <div className="p-4 border-t border-slate-800">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium text-rose-400 hover:bg-rose-500/10 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
