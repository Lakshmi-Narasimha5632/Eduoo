import React, { useState, useEffect } from 'react';
import {
  User,
  Save,
  CheckCircle2,
  AlertCircle,
  Key,
  Briefcase,
  Mail,
  Send,
  RefreshCw,
  Zap,
  Check,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';

export const Profile = () => {
  const { user, updateProfile } = useAuth();

  // Profile form state
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [college, setCollege] = useState(user?.college || '');
  const [branch, setBranch] = useState(user?.branch || '');
  const [gradYear, setGradYear] = useState(user?.graduation_year || 2026);
  const [targetRole, setTargetRole] = useState(user?.target_role || 'Software Engineer');
  const [dailyHours, setDailyHours] = useState(user?.daily_study_hours || 2);
  const [bio, setBio] = useState(user?.bio || '');
  const [careerGoal, setCareerGoal] = useState(user?.career_goal || '');

  // Target roles options
  const [targetRolesList, setTargetRolesList] = useState([
    'Software Engineer',
    'Frontend Engineer',
    'Backend Engineer',
    'Full Stack Engineer',
    'DevOps Engineer',
    'AI / ML Engineer',
    'Data Engineer',
    'Mobile App Developer',
    'Security Engineer',
  ]);

  // Password form state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Notifications state
  const [notifPrefs, setNotifPrefs] = useState({
    email_notifications: true,
    notification_email: '',
    daily_task_reminders: true,
    streak_reminders: true,
    interview_reminders: true,
    platform_sync_alerts: true,
    weekly_summaries: true,
    realtime_interview_email: true,
    realtime_platform_sync_email: true,
    realtime_task_email: true,
  });
  const [customEmail, setCustomEmail] = useState('');
  const [savingEmail, setSavingEmail] = useState(false);
  const [sendingTestEmail, setSendingTestEmail] = useState(false);
  const [testEmailMsg, setTestEmailMsg] = useState(null);

  // UI state
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setCollege(user.college || '');
      setBranch(user.branch || '');
      setGradYear(user.graduation_year || 2026);
      setTargetRole(user.target_role || 'Software Engineer');
      setDailyHours(user.daily_study_hours || 2);
      setBio(user.bio || '');
      setCareerGoal(user.career_goal || '');
    }

    const loadMeta = async () => {
      try {
        const [rolesRes, prefsRes] = await Promise.all([
          api.get('/auth/target-roles/'),
          api.get('/notifications/preferences/'),
        ]);
        if (rolesRes?.target_roles) {
          setTargetRolesList(rolesRes.target_roles);
        }
        if (prefsRes?.preferences) {
          setNotifPrefs((prev) => ({ ...prev, ...prefsRes.preferences }));
          setCustomEmail(prefsRes.preferences.notification_email || '');
        }
      } catch {}
    };
    loadMeta();
  }, [user]);

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setSavingProfile(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await updateProfile({
        full_name: fullName,
        college,
        branch,
        graduation_year: Number(gradYear),
        target_role: targetRole,
        daily_study_hours: Number(dailyHours),
        bio,
        career_goal: careerGoal,
      });
      setSuccessMsg('Profile and learning preferences updated successfully!');
    } catch (err) {
      setErrorMsg(err?.message || 'Failed to update profile.');
    } finally {
      setSavingProfile(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setErrorMsg('New password and confirmation do not match.');
      return;
    }
    setSavingPassword(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await api.post('/auth/password/change/', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setSuccessMsg('Password changed successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      setErrorMsg(err?.message || 'Failed to update password.');
    } finally {
      setSavingPassword(false);
    }
  };

  const handleTogglePref = async (key) => {
    const updated = { ...notifPrefs, [key]: !notifPrefs[key] };
    setNotifPrefs(updated);
    try {
      await api.put('/notifications/preferences/', { preferences: updated });
    } catch {}
  };

  const handleSaveEmail = async () => {
    setSavingEmail(true);
    setTestEmailMsg(null);
    try {
      const emailToSave = customEmail.trim();
      const updated = { ...notifPrefs, notification_email: emailToSave };
      setNotifPrefs(updated);
      await api.put('/notifications/preferences/', { preferences: updated });
      setTestEmailMsg({ type: 'success', text: 'Real-time delivery email address saved successfully!' });
    } catch (err) {
      setTestEmailMsg({ type: 'error', text: err?.message || 'Failed to update delivery email.' });
    } finally {
      setSavingEmail(false);
    }
  };

  const handleSendTestEmail = async () => {
    setSendingTestEmail(true);
    setTestEmailMsg(null);
    try {
      const target = customEmail.trim() || user?.email;
      const res = await api.post('/notifications/test-email/', { email: target });
      setTestEmailMsg({
        type: 'success',
        text: res?.message || `Real-time test email sent to ${target}! Check your inbox or development console.`,
      });
    } catch (err) {
      setTestEmailMsg({
        type: 'error',
        text: err?.response?.data?.error?.message || err?.message || 'Failed to send real-time test email.',
      });
    } finally {
      setSendingTestEmail(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-3">
          <User className="w-7 h-7 text-brand-400" />
          User Profile & Career Goal Settings
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Customize your target career role, study capacity budget, academic profile, and security credentials.
        </p>
      </div>

      {/* Notifications */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}
      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-sm flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 shrink-0 text-emerald-400" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Profile Form Card */}
      <form onSubmit={handleProfileSubmit} className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white font-black text-xl shadow-lg">
              {fullName ? fullName[0].toUpperCase() : 'U'}
            </div>
            <div>
              <h3 className="font-bold text-white text-base">{fullName || user?.username}</h3>
              <p className="text-xs text-slate-400">{user?.email}</p>
            </div>
          </div>

          <button
            type="submit"
            disabled={savingProfile}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold shadow-lg shadow-brand-500/25 transition disabled:opacity-50"
          >
            <Save className={`w-3.5 h-3.5 ${savingProfile ? 'animate-spin' : ''}`} />
            <span>{savingProfile ? 'Saving...' : 'Save Profile'}</span>
          </button>
        </div>

        {/* Basic Information */}
        <div className="space-y-4">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Personal & Academic Information
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Full Name</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-800/90 border border-slate-700 rounded-xl text-white text-xs focus:border-brand-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">College / University</label>
              <input
                type="text"
                value={college}
                placeholder="e.g. Stanford University"
                onChange={(e) => setCollege(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-800/90 border border-slate-700 rounded-xl text-white text-xs focus:border-brand-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Major / Branch</label>
              <input
                type="text"
                value={branch}
                placeholder="e.g. Computer Science & Engineering"
                onChange={(e) => setBranch(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-800/90 border border-slate-700 rounded-xl text-white text-xs focus:border-brand-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Graduation Year</label>
              <input
                type="number"
                min="2020"
                max="2035"
                value={gradYear}
                onChange={(e) => setGradYear(Number(e.target.value))}
                className="w-full px-3.5 py-2.5 bg-slate-800/90 border border-slate-700 rounded-xl text-white text-xs focus:border-brand-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Career & Study Budget Configuration */}
        <div className="space-y-4 pt-4 border-t border-slate-800">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Briefcase className="w-4 h-4 text-brand-400" />
            Career Goal & Daily Study Budget
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Target Engineering Role</label>
              <select
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-800/90 border border-slate-700 rounded-xl text-white text-xs focus:border-brand-500 focus:outline-none"
              >
                {targetRolesList.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Daily Study Budget ({dailyHours} hours / day)
              </label>
              <input
                type="range"
                min="0.5"
                max="8"
                step="0.5"
                value={dailyHours}
                onChange={(e) => setDailyHours(Number(e.target.value))}
                className="w-full mt-2 accent-brand-500"
              />
              <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                <span>30 mins</span>
                <span>2 hours (Recommended)</span>
                <span>8 hours</span>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Career Goal Statement</label>
            <textarea
              rows={2}
              placeholder="e.g. Aiming to join a Tier-1 tech company as a Backend Engineer specializing in scalable distributed microservices."
              value={careerGoal}
              onChange={(e) => setCareerGoal(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-slate-800/90 border border-slate-700 rounded-xl text-white text-xs focus:border-brand-500 focus:outline-none leading-relaxed"
            />
          </div>
        </div>
      </form>

      {/* Password Change Card */}
      <form onSubmit={handlePasswordSubmit} className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-brand-400" />
            <h3 className="font-bold text-white text-sm">Security & Password</h3>
          </div>

          <button
            type="submit"
            disabled={savingPassword}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition disabled:opacity-50"
          >
            <span>{savingPassword ? 'Updating...' : 'Update Password'}</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Current Password</label>
            <input
              type="password"
              required
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="w-full px-3.5 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white text-xs focus:border-brand-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">New Password</label>
            <input
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full px-3.5 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white text-xs focus:border-brand-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Confirm New Password</label>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-3.5 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white text-xs focus:border-brand-500 focus:outline-none"
            />
          </div>
        </div>
      </form>

      {/* Notification & Real-Time Email Preferences */}
      <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400">
              <Mail className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-white text-sm">Real-Time Email & Notification Alerts</h3>
              <p className="text-xs text-slate-400">Receive instant scorecards, platform telemetry updates, and milestone alerts.</p>
            </div>
          </div>
          <div>
            {notifPrefs.email_notifications ? (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[11px] font-bold tracking-wide uppercase">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse inline-block" />
                Real-Time Push: Active
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800 text-slate-400 border border-slate-700 text-[11px] font-bold uppercase">
                Email Push: Paused
              </span>
            )}
          </div>
        </div>

        {/* Master Email Toggle Card */}
        <div className="p-4 rounded-xl bg-gradient-to-r from-brand-950/40 via-slate-800/50 to-slate-900/50 border border-brand-500/20 flex items-center justify-between">
          <div className="flex items-start gap-3">
            <Zap className="w-5 h-5 text-brand-400 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-bold text-white">Enable Real-Time Email Notifications</p>
              <p className="text-[11px] text-slate-300 mt-0.5">
                Automatically dispatch instant HTML emails with detailed performance telemetry whenever major events occur.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => handleTogglePref('email_notifications')}
            className={`w-12 h-6 rounded-full transition-colors p-1 flex items-center shrink-0 ${
              notifPrefs.email_notifications ? 'bg-brand-600 justify-end' : 'bg-slate-700 justify-start'
            }`}
          >
            <span className="w-4 h-4 rounded-full bg-white block shadow-md" />
          </button>
        </div>

        {/* Delivery Email & Test Send Controls */}
        <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-800 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex-1">
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Notification Delivery Email
              </label>
              <p className="text-[11px] text-slate-400 mb-2">
                Defaults to your account email (<span className="text-slate-300 font-mono">{user?.email}</span>). Set a custom address if desired.
              </p>
              <div className="flex items-center gap-2 max-w-md">
                <input
                  type="email"
                  placeholder={user?.email || 'your-email@domain.com'}
                  value={customEmail}
                  onChange={(e) => setCustomEmail(e.target.value)}
                  className="w-full px-3.5 py-1.5 bg-slate-900 border border-slate-700 rounded-xl text-white text-xs font-mono focus:border-brand-500 focus:outline-none"
                />
                <button
                  type="button"
                  onClick={handleSaveEmail}
                  disabled={savingEmail}
                  className="px-3 py-1.5 rounded-xl bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold shrink-0 transition flex items-center gap-1.5"
                >
                  {savingEmail ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Save className="w-3 h-3" />}
                  Save
                </button>
              </div>
            </div>

            <div className="sm:self-end">
              <button
                type="button"
                onClick={handleSendTestEmail}
                disabled={sendingTestEmail}
                className="w-full sm:w-auto px-4 py-2 rounded-xl bg-gradient-to-r from-brand-600 to-purple-600 hover:from-brand-500 hover:to-purple-500 text-white text-xs font-bold shadow-lg shadow-brand-500/20 transition flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {sendingTestEmail ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Send className="w-3.5 h-3.5" />
                )}
                <span>Send Real-Time Test Email</span>
              </button>
            </div>
          </div>

          {testEmailMsg && (
            <div
              className={`p-3 rounded-xl text-xs flex items-center gap-2.5 transition ${
                testEmailMsg.type === 'success'
                  ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-300'
                  : 'bg-rose-500/10 border border-rose-500/20 text-rose-300'
              }`}
            >
              {testEmailMsg.type === 'success' ? (
                <Check className="w-4 h-4 text-emerald-400 shrink-0" />
              ) : (
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              )}
              <span>{testEmailMsg.text}</span>
            </div>
          )}
        </div>

        {/* Granular Real-Time Event Alerts */}
        <div className="space-y-3">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Real-Time Alert Event Channels
          </p>

          {[
            {
              key: 'realtime_interview_email',
              icon: '🎯',
              label: 'Mock Interview Performance & Evaluation Emails',
              desc: 'Dispatches instant comprehensive evaluation scorecard, hire decision, strengths, and weaknesses upon completion.',
            },
            {
              key: 'realtime_platform_sync_email',
              icon: '⚡',
              label: 'Platform Telemetry Synchronization Alerts',
              desc: 'Sends real-time email notification when LeetCode, GitHub, HackerRank, or CodeChef syncs new problems and badges.',
            },
            {
              key: 'realtime_task_email',
              icon: '🔥',
              label: 'Daily Study Goals & Streak Milestone Celebrations',
              desc: 'Alerts you in real time when you finish daily tasks or hit consistent problem-solving streaks.',
            },
            {
              key: 'weekly_summaries',
              icon: '📊',
              label: 'Weekly Career & Performance Digest',
              desc: 'Weekly report synthesizing algorithm hours, interview readiness, and recommendations.',
            },
          ].map((item) => (
            <div key={item.key} className="flex items-center justify-between p-3.5 rounded-xl bg-slate-800/40 border border-slate-800/80 hover:bg-slate-800/60 transition">
              <div className="flex items-start gap-3">
                <span className="text-base">{item.icon}</span>
                <div>
                  <p className="text-xs font-bold text-white">{item.label}</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">{item.desc}</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => handleTogglePref(item.key)}
                className={`w-11 h-6 rounded-full transition-colors p-1 flex items-center shrink-0 ml-3 ${
                  notifPrefs[item.key] ? 'bg-brand-600 justify-end' : 'bg-slate-700 justify-start'
                }`}
              >
                <span className="w-4 h-4 rounded-full bg-white block shadow-md" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Profile;
