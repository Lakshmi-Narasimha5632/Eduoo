import React, { useState, useEffect } from 'react';
import { Bell, Flame, Check, Mail, Settings } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';

export const Navbar = () => {
  const { user } = useAuth();
  const [streak, setStreak] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [showNotifs, setShowNotifs] = useState(false);

  useEffect(() => {
    const fetchHeaderData = async () => {
      try {
        const [progressRes, notifsRes] = await Promise.all([
          api.get('/progress/'),
          api.get('/notifications/?unread=true'),
        ]);
        if (progressRes?.current_streak !== undefined) {
          setStreak(progressRes.current_streak);
        }
        if (notifsRes?.notifications) {
          setNotifications(notifsRes.notifications);
        }
      } catch {}
    };
    fetchHeaderData();

    const handleProgressUpdate = () => {
      fetchHeaderData();
    };

    window.addEventListener('study-progress-updated', handleProgressUpdate);
    window.addEventListener('focus', handleProgressUpdate);

    return () => {
      window.removeEventListener('study-progress-updated', handleProgressUpdate);
      window.removeEventListener('focus', handleProgressUpdate);
    };
  }, []);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const handleMarkRead = async (id) => {
    try {
      await api.post('/notifications/read/', { id });
      setNotifications((prev) => (id ? prev.filter((n) => n.id !== id) : []));
    } catch {}
  };

  return (
    <header className="h-16 bg-slate-900/50 backdrop-blur-md border-b border-slate-800 flex items-center justify-between px-8 sticky top-0 z-40">
      {/* Greeting */}
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-bold text-white">
          {getGreeting()},{' '}
          <span className="text-brand-400">
            {user?.full_name?.split(' ')[0] || user?.username || 'Learner'}
          </span>{' '}
          👋
        </h1>
        {user?.target_role && (
          <span className="hidden md:inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-brand-500/10 text-brand-300 border border-brand-500/20">
            {user.target_role}
          </span>
        )}
      </div>

      {/* Action Badges & Notifications */}
      <div className="flex items-center gap-4">
        {/* Streak Counter */}
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20 font-semibold text-xs shadow-sm">
          <Flame className="w-4 h-4 text-amber-400 fill-amber-400 animate-pulse" />
          <span>{streak} {streak === 1 ? 'day' : 'days'} streak</span>
        </div>

        {/* Notifications Icon with popover */}
        <div className="relative">
          <button
            onClick={() => setShowNotifs(!showNotifs)}
            className="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 hover:text-white hover:bg-slate-700 transition relative"
          >
            <Bell className="w-4 h-4" />
            {notifications.length > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-brand-500 text-white rounded-full text-[10px] font-bold flex items-center justify-center">
                {notifications.length}
              </span>
            )}
          </button>

          {showNotifs && (
            <div className="absolute right-0 mt-2 w-80 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl p-4 z-50">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <span className="text-xs font-bold uppercase text-slate-400 tracking-wider">
                  Notifications
                </span>
                {notifications.length > 0 && (
                  <button
                    onClick={() => handleMarkRead()}
                    className="text-xs text-brand-400 hover:underline"
                  >
                    Mark all read
                  </button>
                )}
              </div>
              <div className="mt-2 space-y-2 max-h-64 overflow-y-auto">
                {notifications.length === 0 ? (
                  <p className="text-xs text-slate-400 py-3 text-center">No new notifications</p>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      className="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs flex justify-between gap-2"
                    >
                      <div className="flex-1">
                        <p className="font-semibold text-white">{n.title}</p>
                        <p className="text-slate-300 mt-0.5 leading-relaxed">{n.message}</p>
                        {n.email_sent && (
                          <div className="mt-1.5">
                            <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20 font-medium">
                              <Mail className="w-2.5 h-2.5" /> Emailed in Real-Time
                            </span>
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => handleMarkRead(n.id)}
                        className="text-slate-400 hover:text-emerald-400 shrink-0 self-start mt-0.5"
                        title="Mark as read"
                      >
                        <Check className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))
                )}
              </div>
              <div className="mt-2 pt-2 border-t border-slate-800 text-center">
                <a
                  href="/profile"
                  onClick={() => setShowNotifs(false)}
                  className="text-[11px] text-brand-400 hover:text-brand-300 font-medium inline-flex items-center justify-center gap-1"
                >
                  <Settings className="w-3 h-3" /> Real-Time Email Settings
                </a>
              </div>
            </div>
          )}
        </div>

        {/* Avatar */}
        <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-brand-600 to-purple-600 flex items-center justify-center text-white font-bold text-sm shadow-md">
          {user?.full_name ? user.full_name[0].toUpperCase() : (user?.username?.[0]?.toUpperCase() || 'U')}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
