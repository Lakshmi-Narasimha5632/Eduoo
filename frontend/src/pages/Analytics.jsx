import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart3,
  Flame,
  Clock,
  Code2,
  Compass,
  Github,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export const Analytics = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  const [progressData, setProgressData] = useState(null);
  const [unifiedData, setUnifiedData] = useState(null);
  const [readinessData, setReadinessData] = useState(null);
  const [platformsList, setPlatformsList] = useState([]);
  const [weeklyData, setWeeklyData] = useState(null);

  const fetchAnalytics = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const [progRes, uniRes, readyRes, platRes, weekRes] = await Promise.all([
        api.get('/progress/'),
        api.get('/platforms/unified/'),
        api.get('/skills/career-readiness/'),
        api.get('/platforms/'),
        api.get('/progress/weekly/'),
      ]);
      setProgressData(progRes);
      setUnifiedData(uniRes?.analytics || uniRes || null);
      setReadinessData(readyRes);
      setWeeklyData(weekRes);
      const pList = Array.isArray(platRes?.platforms)
        ? platRes.platforms
        : (Array.isArray(platRes?.accounts) ? platRes.accounts : (Array.isArray(platRes) ? platRes : []));
      setPlatformsList(pList);
    } catch (err) {
      setErrorMsg(err?.message || 'Failed to fetch analytics data.');
      setPlatformsList([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  // Dynamic daily study habit trend calculated from backend progress/weekly/
  const targetDailyMinutes = (user?.daily_study_hours || 2) * 60;
  const weeklyStudyData = Array.isArray(weeklyData?.daily) && weeklyData.daily.length > 0
    ? weeklyData.daily.map((d) => {
        let dayLabel = d.date;
        try {
          const parts = d.date.split('-');
          if (parts.length === 3) {
            const dt = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10));
            dayLabel = dt.toLocaleDateString('en-US', { weekday: 'short' });
          }
        } catch {}
        return {
          day: dayLabel,
          minutes: d.study_minutes || 0,
          target: targetDailyMinutes,
          tasks: d.tasks_completed || 0,
        };
      })
    : [
        { day: 'Mon', minutes: 0, target: targetDailyMinutes },
        { day: 'Tue', minutes: 0, target: targetDailyMinutes },
        { day: 'Wed', minutes: 0, target: targetDailyMinutes },
        { day: 'Thu', minutes: 0, target: targetDailyMinutes },
        { day: 'Fri', minutes: 0, target: targetDailyMinutes },
        { day: 'Sat', minutes: 0, target: targetDailyMinutes },
        { day: 'Sun', minutes: 0, target: targetDailyMinutes },
      ];

  // Dynamic Coding difficulty breakdown from connected LeetCode telemetry and unified analytics
  const leetcodeAccount = Array.isArray(platformsList)
    ? platformsList.find((p) => p.platform?.toLowerCase() === 'leetcode')
    : null;
  const rawLc = leetcodeAccount?.raw_data || {};
  const easySolved = Number(
    unifiedData?.difficulty_distribution?.Easy ??
    rawLc.easy_solved ??
    rawLc.difficulty_distribution?.easy ??
    0
  );
  const mediumSolved = Number(
    unifiedData?.difficulty_distribution?.Medium ??
    rawLc.medium_solved ??
    rawLc.difficulty_distribution?.medium ??
    0
  );
  const hardSolved = Number(
    unifiedData?.difficulty_distribution?.Hard ??
    rawLc.hard_solved ??
    rawLc.difficulty_distribution?.hard ??
    0
  );
  const totalSolved = easySolved + mediumSolved + hardSolved;

  const difficultyData = totalSolved > 0
    ? [
        { name: 'Easy', value: easySolved, color: '#10b981' },
        { name: 'Medium', value: mediumSolved, color: '#f59e0b' },
        { name: 'Hard', value: hardSolved, color: '#f43f5e' },
      ]
    : [
        { name: 'Easy', value: 0, color: '#10b981' },
        { name: 'Medium', value: 0, color: '#f59e0b' },
        { name: 'Hard', value: 0, color: '#f43f5e' },
      ];

  // Dynamic GitHub languages breakdown from connected GitHub telemetry and unified analytics
  const githubAccount = Array.isArray(platformsList)
    ? platformsList.find((p) => p.platform?.toLowerCase() === 'github')
    : null;
  const rawGh = githubAccount?.raw_data || {};
  const rawLangs = unifiedData?.languages || rawGh?.language_distribution || rawGh?.languages || {};
  const languagesData = Object.keys(rawLangs).length > 0
    ? Object.entries(rawLangs).map(([lang, count]) => ({ name: lang, count: Number(count) }))
    : (Array.isArray(rawGh?.top_languages) && rawGh.top_languages.length > 0
        ? rawGh.top_languages.map((l) => ({ name: l.language || l.name, count: Number(l.count || l.repos || 1) }))
        : []);

  // Career Readiness Factors (directly from backend evaluation engine)
  const readinessFactorData = Array.isArray(readinessData?.factors) && readinessData.factors.length > 0
    ? readinessData.factors
    : [
        { factor: 'Technical Skills', score: 40 },
        { factor: 'Projects & Portfolio', score: 45 },
        { factor: 'Problem Solving', score: 50 },
        { factor: 'Communication', score: 65 },
        { factor: 'Interview Prep', score: 65 },
        { factor: 'Consistency', score: 45 },
      ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-3">
            <BarChart3 className="w-7 h-7 text-brand-400" />
            Performance & Growth Analytics
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Aggregated cross-platform metrics, coding volume, consistency trends, and career readiness.
          </p>
        </div>

        <button
          onClick={fetchAnalytics}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Data</span>
        </button>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Career Readiness</span>
            <div className="w-9 h-9 rounded-xl bg-brand-500/15 flex items-center justify-center text-brand-400">
              <Compass className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white mt-2">
            {readinessData?.overall_readiness ?? readinessData?.overall_readiness_score ?? 50}
            <span className="text-sm font-semibold text-slate-400"> / 100</span>
          </div>
          <p className="text-xs text-brand-300 mt-1">
            {readinessData?.tier || 'Competitive Track'}
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Practice</span>
            <div className="w-9 h-9 rounded-xl bg-emerald-500/15 flex items-center justify-center text-emerald-400">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white mt-2">
            {Math.round((progressData?.total_study_minutes || 0) / 60)} hrs
          </div>
          <p className="text-xs text-emerald-400 mt-1">
            {progressData?.total_tasks_completed || 0} tasks finished
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Problems Solved</span>
            <div className="w-9 h-9 rounded-xl bg-amber-500/15 flex items-center justify-center text-amber-400">
              <Code2 className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white mt-2">
            {unifiedData?.total_problems_solved || 0}
          </div>
          <p className="text-xs text-amber-400 mt-1">
            LeetCode + HackerRank + CodeChef
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Current Streak</span>
            <div className="w-9 h-9 rounded-xl bg-rose-500/15 flex items-center justify-center text-rose-400">
              <Flame className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white mt-2">
            {progressData?.current_streak || 0} days
          </div>
          <p className="text-xs text-rose-400 mt-1">
            Best: {progressData?.longest_streak || 0} days
          </p>
        </div>
      </div>

      {/* Row 1: Weekly Study Trend & Career Factor Scores */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Study Trend */}
        <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white">Weekly Study Time Trend</h3>
              <p className="text-xs text-slate-400">Actual practice minutes vs daily target</p>
            </div>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-slate-800 text-brand-300 border border-slate-700">
              Past 7 Days
            </span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={weeklyStudyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="studyGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: '#fff',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="minutes"
                  stroke="#6366f1"
                  strokeWidth={3}
                  fillOpacity={1}
                  fill="url(#studyGradient)"
                  name="Study Minutes"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 6 Explainable Career Readiness Factors */}
        <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white">Career Readiness Factors</h3>
              <p className="text-xs text-slate-400">6 dimensions evaluated against industry standards</p>
            </div>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
              Weighted Index
            </span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={readinessFactorData}
                layout="vertical"
                margin={{ top: 5, right: 20, left: 30, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="factor" stroke="#94a3b8" tick={{ fontSize: 11 }} width={120} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="score" fill="#818cf8" radius={[0, 6, 6, 0]} name="Score" barSize={14} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 2: Problem Solving Difficulty & GitHub Language Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Difficulty Distribution */}
        <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white">Problem Solving Breakdown</h3>
              <p className="text-xs text-slate-400">LeetCode difficulty proportion</p>
            </div>
          </div>

          <div className="h-64 flex items-center justify-center">
            {totalSolved === 0 ? (
              <div className="flex flex-col items-center justify-center text-center p-6">
                <Code2 className="w-10 h-10 text-slate-600 mb-2" />
                <span className="text-xs text-slate-400">No LeetCode telemetry synced yet.</span>
                <Link
                  to="/platforms"
                  className="mt-3 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-semibold hover:bg-amber-500/20 transition"
                >
                  Sync LeetCode Account
                </Link>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={difficultyData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {difficultyData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      border: '1px solid #334155',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* GitHub Tech Stack Distribution */}
        <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white">Project Stack & Languages</h3>
              <p className="text-xs text-slate-400">Repositories and code volume</p>
            </div>
          </div>

          <div className="h-64 flex items-center justify-center">
            {languagesData.length === 0 ? (
              <div className="flex flex-col items-center justify-center text-center p-6">
                <Github className="w-10 h-10 text-slate-600 mb-2" />
                <span className="text-xs text-slate-400">No GitHub repositories analyzed yet.</span>
                <Link
                  to="/platforms"
                  className="mt-3 px-3 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold hover:bg-indigo-500/20 transition"
                >
                  Sync GitHub Account
                </Link>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={languagesData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      border: '1px solid #334155',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="count" fill="#10b981" radius={[6, 6, 0, 0]} name="Projects / Repos" barSize={28} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Platform Integration Health Table */}
      <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
        <h3 className="text-base font-bold text-white mb-1">Platform Sync Status</h3>
        <p className="text-xs text-slate-400 mb-4">Live telemetry and sync history across all connected profiles</p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider">
                <th className="pb-3">Platform</th>
                <th className="pb-3">Account</th>
                <th className="pb-3">Status</th>
                <th className="pb-3">Last Synced</th>
                <th className="pb-3 text-right">Key Metrics</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {['LeetCode', 'GitHub', 'Duolingo', 'HackerRank', 'CodeChef', 'LinkedIn'].map((platName) => {
                const acc = Array.isArray(platformsList)
                  ? platformsList.find((p) => p.platform?.toLowerCase() === platName.toLowerCase())
                  : null;
                const isConn = Boolean(acc?.connected || acc?.is_active);

                return (
                  <tr key={platName} className="hover:bg-slate-800/30 transition">
                    <td className="py-3 font-semibold text-white">{platName}</td>
                    <td className="py-3 text-slate-300 font-mono">{acc?.username || '—'}</td>
                    <td className="py-3">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                          isConn
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-slate-800 text-slate-500'
                        }`}
                      >
                        <span className={`w-1.5 h-1.5 rounded-full ${isConn ? 'bg-emerald-400' : 'bg-slate-600'}`} />
                        {isConn ? 'Active' : 'Unlinked'}
                      </span>
                    </td>
                    <td className="py-3 text-slate-400">
                      {acc?.last_synced_at ? new Date(acc.last_synced_at).toLocaleString() : 'Never'}
                    </td>
                    <td className="py-3 text-right text-brand-300 font-medium">
                      {isConn ? (
                        platName.toLowerCase() === 'leetcode'
                          ? `${acc?.raw_data?.total_solved ?? acc?.raw_data?.solved ?? 0} Solved`
                          : platName.toLowerCase() === 'github'
                          ? `${acc?.raw_data?.total_repositories ?? acc?.raw_data?.public_repos ?? 0} Repos`
                          : platName.toLowerCase() === 'hackerrank'
                          ? `${acc?.raw_data?.badges ?? 0} Badges • ${acc?.raw_data?.total_solved ?? acc?.raw_data?.problems_solved ?? 0} Solved`
                          : platName.toLowerCase() === 'codechef'
                          ? `${acc?.raw_data?.rating ? `${acc.raw_data.rating} (${acc.raw_data.stars ? `${acc.raw_data.stars}★` : 'Div 3'})` : 'Active'} • ${acc?.raw_data?.total_solved ?? acc?.raw_data?.solved_problems ?? 0} Solved`
                          : platName.toLowerCase() === 'duolingo'
                          ? `${acc?.raw_data?.total_xp ?? acc?.raw_data?.xp ?? 0} XP`
                          : 'Profile Connected'
                      ) : (
                        <span className="text-slate-500">No telemetry</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
