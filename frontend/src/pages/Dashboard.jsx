import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Flame,
  CheckCircle2,
  Circle,
  ArrowRight,
  TrendingUp,
  Cpu,
  Sparkles,
  Lightbulb,
  Clock,
  Award,
} from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { StatCard } from '../components/StatCard';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';

export const Dashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [todayTasks, setTodayTasks] = useState([]);
  const [careerReadiness, setCareerReadiness] = useState(null);
  const [weeklyProgress, setWeeklyProgress] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [completingId, setCompletingId] = useState(null);

  const fetchDashboard = async () => {
    try {
      const [dashRes, tasksRes, readinessRes, weeklyRes, platRes] = await Promise.all([
        api.get('/dashboard/'),
        api.get('/tasks/today/'),
        api.get('/skills/career-readiness/'),
        api.get('/progress/weekly/'),
        api.get('/platforms/'),
      ]);

      setDashboardData(dashRes);
      setTodayTasks(tasksRes?.plan?.tasks || []);
      setCareerReadiness(readinessRes);
      setWeeklyProgress(weeklyRes?.daily || []);
      setPlatforms(platRes?.platforms || []);
    } catch (err) {
      console.error('Error loading dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const [regeneratingTasks, setRegeneratingTasks] = useState(false);

  const handleRegenerateTasks = async () => {
    setRegeneratingTasks(true);
    try {
      const res = await api.post('/tasks/generate/');
      if (res?.plan?.tasks) {
        setTodayTasks(res.plan.tasks);
      }
      await fetchDashboard();
    } catch (err) {
      console.error('Task regen error:', err);
    } finally {
      setRegeneratingTasks(false);
    }
  };

  const handleCompleteTask = async (taskId) => {
    setCompletingId(taskId);
    try {
      await api.post(`/tasks/${taskId}/toggle/`);
      setTodayTasks((prev) =>
        prev.map((t) =>
          t.id === taskId
            ? {
                ...t,
                is_completed: !Boolean(t.is_completed || t.status === 'completed'),
                status: Boolean(t.is_completed || t.status === 'completed') ? 'planned' : 'completed',
              }
            : t
        )
      );
      await fetchDashboard();
      window.dispatchEvent(new CustomEvent('study-progress-updated'));
    } catch (err) {
      console.error('Task complete error:', err);
    } finally {
      setCompletingId(null);
    }
  };

  const completedCount = todayTasks.filter((t) => Boolean(t.is_completed || t.status === 'completed')).length;
  const totalMinutes = todayTasks.reduce((acc, t) => acc + (t.estimated_minutes || 0), 0);
  const completedMinutes = todayTasks
    .filter((t) => Boolean(t.is_completed || t.status === 'completed'))
    .reduce((acc, t) => acc + (t.estimated_minutes || 0), 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[70vh]">
        <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* 1. Header Banner */}
      <div className="glass-card p-6 md:p-8 rounded-3xl relative overflow-hidden bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-brand-500/20">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-brand-500/20 text-brand-300 border border-brand-500/30">
              Personalized Career Track
            </span>
            <h1 className="text-3xl font-black text-white mt-2 tracking-tight">
              Target: {user?.target_role || 'Full Stack Developer'}
            </h1>
            <p className="text-sm text-slate-300 mt-1 max-w-xl">
              Eduoo has mapped your daily curriculum across LeetCode, GitHub projects, and mock interviews to prepare you for senior hiring bars.
            </p>
          </div>

          {/* Overall Career Readiness Gauge */}
          <div className="flex items-center gap-4 bg-slate-900/80 p-4 rounded-2xl border border-slate-700/60 shrink-0">
            <div className="relative w-16 h-16 flex items-center justify-center">
              <svg className="w-16 h-16 transform -rotate-90">
                <circle cx="32" cy="32" r="28" stroke="currentColor" strokeWidth="6" className="text-slate-800" fill="transparent" />
                <circle
                  cx="32"
                  cy="32"
                  r="28"
                  stroke="currentColor"
                  strokeWidth="6"
                  strokeDasharray={175.9}
                  strokeDashoffset={175.9 - (175.9 * (careerReadiness?.overall_readiness || 68)) / 100}
                  className="text-brand-500"
                  strokeLinecap="round"
                  fill="transparent"
                />
              </svg>
              <span className="absolute text-sm font-black text-white">
                {careerReadiness?.overall_readiness || 68}%
              </span>
            </div>
            <div>
              <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Career Readiness</div>
              <div className="text-sm font-bold text-white mt-0.5">
                {careerReadiness?.overall_readiness >= 75 ? 'Interview Ready' : 'In Preparation'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Key Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <StatCard
          title="Today's Progress"
          value={`${completedMinutes} / ${totalMinutes || 90}m`}
          subtitle={`${completedCount} of ${todayTasks.length} tasks completed`}
          icon={Clock}
          color="brand"
        />
        <StatCard
          title="Active Platforms"
          value={platforms.filter((p) => p.connected).length}
          subtitle="of 6 supported platforms"
          icon={Cpu}
          color="emerald"
        />
        <StatCard
          title="Consistency Streak"
          value={`${dashboardData?.overview?.current_streak ?? dashboardData?.current_streak ?? 0} ${(dashboardData?.overview?.current_streak ?? dashboardData?.current_streak ?? 0) === 1 ? 'Day' : 'Days'}`}
          subtitle={
            (dashboardData?.overview?.current_streak || dashboardData?.current_streak)
              ? "Unbroken study habit"
              : "Complete a task to build streak"
          }
          icon={Flame}
          color="amber"
        />
        <StatCard
          title="Mock Interview Score"
          value={dashboardData?.latest_interview_score !== undefined && dashboardData?.latest_interview_score !== null ? `${dashboardData.latest_interview_score}/100` : 'None yet'}
          subtitle={dashboardData?.latest_interview_score !== undefined && dashboardData?.latest_interview_score !== null ? "Latest AI assessment" : "Start your first mock interview"}
          icon={Award}
          color="purple"
        />
      </div>

      {/* 3. Main Grid: Today's Tasks + Weekly Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Today's Study Plan (2 Cols) */}
        <div className="lg:col-span-2 glass-card p-6 rounded-3xl space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-brand-400" />
                Today's Study Plan
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Targeted recommendations aligned with your target role and skill gaps
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleRegenerateTasks}
                disabled={regeneratingTasks}
                className="text-xs text-brand-300 hover:text-white px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 transition flex items-center gap-1.5"
              >
                <Sparkles className={`w-3 h-3 ${regeneratingTasks ? 'animate-spin' : ''}`} />
                <span>{regeneratingTasks ? 'Planning...' : 'Regenerate'}</span>
              </button>
              <Link to="/tasks" className="text-xs text-brand-400 font-semibold hover:underline flex items-center gap-1">
                View All <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          <div className="space-y-3">
            {todayTasks.length === 0 ? (
              <p className="text-sm text-slate-400 py-6 text-center">No tasks scheduled for today.</p>
            ) : (
              todayTasks.map((task) => {
                const isDone = Boolean(task.is_completed || task.status === 'completed');
                return (
                  <div
                    key={task.id}
                    className={`p-4 rounded-2xl border transition-all flex items-start justify-between gap-4 ${
                      isDone
                        ? 'bg-slate-900/40 border-slate-800/80 opacity-70'
                        : 'bg-slate-800/60 border-slate-700/80 hover:border-brand-500/40 shadow-sm'
                    }`}
                  >
                    <div className="flex items-start gap-3.5">
                      <button
                        onClick={() => handleCompleteTask(task.id)}
                        disabled={completingId === task.id}
                        className="mt-0.5 text-slate-400 hover:text-emerald-400 transition"
                      >
                        {isDone ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-400 fill-emerald-500/20" />
                        ) : (
                          <Circle className="w-5 h-5" />
                        )}
                      </button>

                      <div>
                        <span className={`text-sm font-bold block ${isDone ? 'line-through text-slate-400' : 'text-white'}`}>
                          {task.title}
                        </span>
                        <p className="text-xs text-slate-400 mt-0.5">{task.description}</p>
                        <div className="flex items-center gap-3 mt-2 text-[11px] font-medium text-slate-400">
                          <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-700 text-slate-300">
                            {task.task_type}
                          </span>
                          <span>⏱ {task.estimated_minutes} min</span>
                          {task.difficulty && (
                            <span className="capitalize text-brand-300 font-semibold">
                              • {task.difficulty}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {task.problem_url && (
                      <a
                        href={task.problem_url}
                        target="_blank"
                        rel="noreferrer"
                        className="px-3 py-1.5 rounded-lg bg-brand-600/20 text-brand-300 border border-brand-500/30 text-xs font-semibold hover:bg-brand-600 hover:text-white transition shrink-0"
                      >
                        Open
                      </a>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Weekly Study Activity Chart (1 Col) */}
        <div className="glass-card p-6 rounded-3xl space-y-4 flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-indigo-400" />
              Weekly Study Time
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Completed study minutes per day</p>
          </div>

          <div className="h-48 w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={weeklyProgress}>
                <defs>
                  <linearGradient id="colorMinutes" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  tickFormatter={(d) => new Date(d).toLocaleDateString('en-US', { weekday: 'short' })}
                  stroke="#64748b"
                  fontSize={11}
                />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                  labelFormatter={(d) => `Date: ${d}`}
                />
                <Area type="monotone" dataKey="study_minutes" stroke="#6366f1" fillOpacity={1} fill="url(#colorMinutes)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="pt-3 border-t border-slate-800 text-xs text-slate-400 flex justify-between">
            <span>Weekly Goal: 14 hours</span>
            <span className="text-brand-400 font-bold">
              {weeklyProgress.reduce((acc, d) => acc + (d.study_minutes || 0), 0)} min logged
            </span>
          </div>
        </div>
      </div>

      {/* 4. Platform Overview + Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Connected Platforms Bar */}
        <div className="glass-card p-6 rounded-3xl space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Cpu className="w-5 h-5 text-emerald-400" />
              Connected Platforms
            </h2>
            <Link to="/platforms" className="text-xs text-brand-400 font-semibold hover:underline">
              Manage
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {platforms.map((p) => (
              <div
                key={p.platform}
                className="p-3.5 rounded-2xl bg-slate-800/60 border border-slate-700/60 flex flex-col justify-between"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white capitalize">{p.display_name}</span>
                  <div
                    className={`w-2 h-2 rounded-full ${
                      p.connected ? 'bg-emerald-400 shadow-sm shadow-emerald-400/50' : 'bg-slate-600'
                    }`}
                  />
                </div>
                <div className="mt-2 text-[11px] text-slate-400 truncate">
                  {p.connected ? (p.username ? `@${p.username}` : 'Connected') : 'Not Connected'}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actionable Insights */}
        <div className="glass-card p-6 rounded-3xl space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-amber-400" />
              Strategic Insights
            </h2>
            <Link to="/insights" className="text-xs text-brand-400 font-semibold hover:underline">
              View All
            </Link>
          </div>

          <div className="space-y-3">
            {(dashboardData?.insights || []).slice(0, 3).map((insight) => (
              <div
                key={insight.id}
                className="p-3.5 rounded-2xl bg-slate-800/50 border border-slate-700/60 flex items-start gap-3"
              >
                <div className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center shrink-0 mt-0.5">
                  <Sparkles className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-white">{insight.title}</h4>
                  <p className="text-xs text-slate-400 mt-0.5">{insight.message}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
