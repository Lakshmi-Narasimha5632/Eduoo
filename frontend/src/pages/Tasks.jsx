import React, { useState, useEffect } from 'react';
import {
  CheckSquare,
  Square,
  Clock,
  Sparkles,
  ExternalLink,
  Plus,
  CheckCircle2,
  Flame,
  BookOpen,
  Code2,
  Languages,
  FolderGit2,
  HelpCircle,
  RefreshCw,
  AlertCircle,
  Calendar,
  Layers,
  Trash2,
  Mail,
  Send,
  ChevronDown,
  ChevronUp,
  LayoutGrid,
  List,
} from 'lucide-react';
import { api } from '../api/client';
import { useToast } from '../context/ToastContext';

const CATEGORY_DEFINITIONS = {
  coding: {
    key: 'coding',
    label: 'DSA & Coding Practice',
    shortLabel: 'DSA / LeetCode',
    tagline: 'Algorithmic problem solving, data structures & time complexity',
    icon: Code2,
    accent: 'text-amber-400',
    badgeBg: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
    borderColor: 'border-amber-500/30',
    cardBg: 'from-amber-950/30 via-slate-900/90 to-slate-900',
    progressColor: 'from-amber-500 to-amber-400',
  },
  project: {
    key: 'project',
    label: 'Projects & Portfolio Building',
    shortLabel: 'Projects & Git',
    tagline: 'Hands-on development, GitHub commits & feature implementation',
    icon: FolderGit2,
    accent: 'text-indigo-400',
    badgeBg: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30',
    borderColor: 'border-indigo-500/30',
    cardBg: 'from-indigo-950/30 via-slate-900/90 to-slate-900',
    progressColor: 'from-indigo-500 to-indigo-400',
  },
  interview: {
    key: 'interview',
    label: 'Interview Readiness & Behavioral',
    shortLabel: 'Interview Prep',
    tagline: 'Role-specific questions, STAR responses & mock simulations',
    icon: HelpCircle,
    accent: 'text-purple-400',
    badgeBg: 'bg-purple-500/15 text-purple-300 border-purple-500/30',
    borderColor: 'border-purple-500/30',
    cardBg: 'from-purple-950/30 via-slate-900/90 to-slate-900',
    progressColor: 'from-purple-500 to-purple-400',
  },
  reading: {
    key: 'reading',
    label: 'System Design & Technical Reading',
    shortLabel: 'System Design',
    tagline: 'Architecture tradeoffs, engineering blogs & core documentation',
    icon: BookOpen,
    accent: 'text-sky-400',
    badgeBg: 'bg-sky-500/15 text-sky-300 border-sky-500/30',
    borderColor: 'border-sky-500/30',
    cardBg: 'from-sky-950/30 via-slate-900/90 to-slate-900',
    progressColor: 'from-sky-500 to-sky-400',
  },
  language: {
    key: 'language',
    label: 'Language & Fluency Practice',
    shortLabel: 'Languages',
    tagline: 'Foreign language practice, active recall & vocabulary drills',
    icon: Languages,
    accent: 'text-emerald-400',
    badgeBg: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
    borderColor: 'border-emerald-500/30',
    cardBg: 'from-emerald-950/30 via-slate-900/90 to-slate-900',
    progressColor: 'from-emerald-500 to-emerald-400',
  },
  review: {
    key: 'review',
    label: 'Review & Revision',
    shortLabel: 'Review',
    tagline: 'Spaced repetition, concept review & error log reflection',
    icon: Layers,
    accent: 'text-cyan-400',
    badgeBg: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
    borderColor: 'border-cyan-500/30',
    cardBg: 'from-cyan-950/30 via-slate-900/90 to-slate-900',
    progressColor: 'from-cyan-500 to-cyan-400',
  },
};

const resolveCategoryKey = (taskType) => {
  const type = (taskType || '').toLowerCase();
  if (type === 'leetcode' || type === 'coding') return 'coding';
  if (type === 'github' || type === 'project') return 'project';
  if (type === 'interview' || type === 'interview_prep') return 'interview';
  if (type === 'reading' || type === 'general' || type === 'system_design') return 'reading';
  if (type === 'language') return 'language';
  if (type === 'review') return 'review';
  return 'coding';
};

export const Tasks = () => {
  const { toast } = useToast();
  const [plan, setPlan] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [filterCategory, setFilterCategory] = useState('ALL');
  const [viewMode, setViewMode] = useState('categorized');
  const [collapsedCategories, setCollapsedCategories] = useState({});
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Custom task creation state
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDesc, setNewTaskDesc] = useState('');
  const [newTaskType, setNewTaskType] = useState('leetcode');
  const [newTaskMinutes, setNewTaskMinutes] = useState(30);
  const [newTaskDiff, setNewTaskDiff] = useState('Medium');
  const [newTaskUrl, setNewTaskUrl] = useState('');
  const [addingTask, setAddingTask] = useState(false);
  const [sendingReport, setSendingReport] = useState(false);

  const fetchTasks = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.get('/tasks/today/');
      if (res?.plan) {
        setPlan(res.plan);
        setTasks(res.plan.tasks || []);
      } else if (res?.tasks) {
        setTasks(res.tasks);
      } else if (Array.isArray(res)) {
        setTasks(res);
      }
    } catch (err) {
      setErrorMsg(err.message || 'Failed to fetch tasks.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleToggleTask = async (taskId) => {
    try {
      const res = await api.post(`/tasks/${taskId}/toggle/`);
      const updated = res?.task || res;
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, is_completed: updated.is_completed ?? !t.is_completed } : t))
      );
      if (updated.is_completed || updated.status === 'completed') {
        toast.success(`Completed "${updated.title || 'Task'}"! Logged ${updated.estimated_minutes || 30} mins.`, 'Task Completed');
      } else {
        toast.info(`Task "${updated.title || 'Task'}" moved back to pending.`, 'Task Reopened');
      }
      if (res?.plan) {
        setPlan(res.plan);
      } else {
        fetchTasks();
      }
    } catch (err) {
      const msg = err.message || 'Failed to update task.';
      setErrorMsg(msg);
      toast.error(msg, 'Task Update Error');
    }
  };

  const [deletingTaskId, setDeletingTaskId] = useState(null);

  const handleDeleteTask = async (taskId) => {
    setDeletingTaskId(taskId);
    setErrorMsg(null);
    try {
      const res = await api.delete(`/tasks/${taskId}/`);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
      if (res?.plan) {
        setPlan(res.plan);
      } else {
        await fetchTasks();
      }
      toast.info('Task removed from schedule.', 'Task Deleted');
      setSuccessMsg('Task removed from schedule.');
    } catch (err) {
      const msg = err.message || 'Failed to delete task.';
      setErrorMsg(msg);
      toast.error(msg, 'Delete Error');
    } finally {
      setDeletingTaskId(null);
    }
  };

  const handleGeneratePlan = async () => {
    setGenerating(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    toast.info('Generating dynamic, date-sequenced study plan for today...', 'Generating Plan');
    try {
      const res = await api.post('/tasks/generate/');
      toast.success('Generated a fresh, dynamic daily task schedule tailored to today!', 'Schedule Updated');
      setSuccessMsg('Generated new adaptive daily task plan tailored to your profile!');
      if (res?.plan) {
        setPlan(res.plan);
        setTasks(res.plan.tasks || []);
      } else {
        await fetchTasks();
      }
    } catch (err) {
      const msg = err.message || 'Failed to generate task plan.';
      setErrorMsg(msg);
      toast.error(msg, 'Plan Error');
    } finally {
      setGenerating(false);
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;
    setAddingTask(true);
    setErrorMsg(null);
    try {
      await api.post('/tasks/', {
        title: newTaskTitle.trim(),
        description: newTaskDesc.trim(),
        task_type: newTaskType,
        estimated_minutes: newTaskMinutes,
        difficulty: newTaskDiff,
        external_url: newTaskUrl.trim() || undefined,
      });
      toast.success('Added new custom task to today\'s schedule!', 'Task Added');
      setSuccessMsg('Added new task to your schedule!');
      setShowAddModal(false);
      setNewTaskTitle('');
      setNewTaskDesc('');
      setNewTaskUrl('');
      await fetchTasks();
    } catch (err) {
      const msg = err.message || 'Failed to create task.';
      setErrorMsg(msg);
      toast.error(msg, 'Task Error');
    } finally {
      setAddingTask(false);
    }
  };

  const handleSendDailyReport = async () => {
    setSendingReport(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    const hasIncomplete = tasks.length > 0 && tasks.filter((t) => !t.is_completed).length > 0;
    try {
      const res = await api.post('/tasks/send-daily-report/', {
        force: true,
        type: hasIncomplete ? 'incomplete' : 'completion',
      });
      if (res.report_type === 'completion') {
        const msg = `Daily task completion report dispatched to your verified email (${res.recipient})!`;
        setSuccessMsg(msg);
        toast.success(msg, 'Email Dispatched');
      } else {
        const msg = `Incomplete tasks alert dispatched to your verified email (${res.recipient})!`;
        setSuccessMsg(msg);
        toast.info(msg, 'Reminder Dispatched');
      }
    } catch (err) {
      const msg = err.message || 'Failed to dispatch daily report email.';
      setErrorMsg(msg);
      toast.error(msg, 'Email Error');
    } finally {
      setSendingReport(false);
    }
  };

  const targetMinutes = plan?.target_minutes || 120;
  const completedMinutes = plan?.completed_minutes || tasks.filter((t) => t.is_completed).reduce((acc, t) => acc + (t.estimated_minutes || 0), 0);
  const percentComplete = Math.min(100, Math.round((completedMinutes / (targetMinutes || 1)) * 100));

  // Compute category breakdown metrics across all plan tasks
  const categoryOverview = React.useMemo(() => {
    const map = {};
    for (const t of tasks) {
      const catKey = resolveCategoryKey(t.task_type);
      if (!map[catKey]) {
        map[catKey] = { total: 0, completed: 0, minutes: 0 };
      }
      map[catKey].total += 1;
      if (t.is_completed) map[catKey].completed += 1;
      map[catKey].minutes += t.estimated_minutes || 0;
    }
    return map;
  }, [tasks]);

  const filteredTasks = tasks.filter((t) => {
    if (filterStatus === 'PENDING' && t.is_completed) return false;
    if (filterStatus === 'COMPLETED' && !t.is_completed) return false;
    if (filterCategory !== 'ALL' && resolveCategoryKey(t.task_type) !== filterCategory) return false;
    return true;
  });

  // Group filtered tasks by resolved category
  const categorizedTasks = React.useMemo(() => {
    const groups = {};
    for (const task of filteredTasks) {
      const catKey = resolveCategoryKey(task.task_type);
      if (!groups[catKey]) {
        groups[catKey] = [];
      }
      groups[catKey].push(task);
    }
    return groups;
  }, [filteredTasks]);

  const toggleCategoryCollapse = (catKey) => {
    setCollapsedCategories((prev) => ({ ...prev, [catKey]: !prev[catKey] }));
  };

  const renderTaskCard = (task) => {
    const cat = CATEGORY_DEFINITIONS[resolveCategoryKey(task.task_type)] || CATEGORY_DEFINITIONS.coding;
    const CatIcon = cat.icon;

    return (
      <div
        key={task.id}
        className={`p-4 rounded-2xl border transition-all duration-200 flex items-start justify-between gap-4 ${
          task.is_completed
            ? 'bg-slate-900/30 border-slate-800/60 opacity-60'
            : 'bg-slate-900/90 border-slate-800 hover:border-slate-700 shadow-md'
        }`}
      >
        <div className="flex items-start gap-3.5 flex-1">
          <button
            onClick={() => handleToggleTask(task.id)}
            className="mt-0.5 text-slate-400 hover:text-brand-400 transition"
          >
            {task.is_completed ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400 fill-emerald-400/20" />
            ) : (
              <Square className="w-5 h-5 text-slate-600 hover:text-slate-400" />
            )}
          </button>

          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h4
                className={`text-sm font-bold ${
                  task.is_completed ? 'line-through text-slate-400' : 'text-white'
                }`}
              >
                {task.title}
              </h4>

              <span
                className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full border ${cat.badgeBg}`}
              >
                <CatIcon className="w-3 h-3" />
                {cat.shortLabel}
              </span>

              {task.difficulty && (
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    task.difficulty.toUpperCase() === 'EASY'
                      ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20'
                      : task.difficulty.toUpperCase() === 'MEDIUM'
                      ? 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
                      : 'bg-rose-500/10 text-rose-300 border border-rose-500/20'
                  }`}
                >
                  {task.difficulty}
                </span>
              )}
            </div>

            {task.description && (
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">{task.description}</p>
            )}

            <div className="flex items-center gap-4 mt-2.5 text-[11px] text-slate-400">
              <div className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                <span>{task.estimated_minutes} mins</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {task.external_url && (
            <a
              href={task.external_url}
              target="_blank"
              rel="noreferrer"
              className="p-2 rounded-xl bg-slate-800/80 hover:bg-brand-600 text-slate-300 hover:text-white transition"
              title="Open problem / resource"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
          <button
            onClick={() => handleDeleteTask(task.id)}
            disabled={deletingTaskId === task.id}
            className="p-2 rounded-xl bg-slate-800/40 hover:bg-rose-500/20 text-slate-500 hover:text-rose-400 transition"
            title="Remove task from schedule"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-3">
            <CheckSquare className="w-7 h-7 text-brand-400" />
            Adaptive Daily Tasks
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            AI-sequenced study schedule aligning with your target role, platform gaps, and study budget.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
          >
            <Plus className="w-4 h-4 text-emerald-400" />
            Custom Task
          </button>
          <button
            onClick={handleGeneratePlan}
            disabled={generating}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-brand-500/25 transition disabled:opacity-50"
          >
            <Sparkles className={`w-3.5 h-3.5 ${generating ? 'animate-spin' : ''}`} />
            <span>{generating ? 'Planning...' : 'Regenerate Plan'}</span>
          </button>
        </div>
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

      {/* Progress & Target Card */}
      <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-slate-850 border border-slate-700/80 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
              <Calendar className="w-4 h-4 text-brand-400" />
              <span>Today's Study Commitment</span>
            </div>
            <div className="flex items-baseline gap-3 mt-2">
              <span className="text-3xl font-black text-white">{completedMinutes}m</span>
              <span className="text-sm font-semibold text-slate-400">/ {targetMinutes}m target</span>
              <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30">
                {percentComplete}% completed
              </span>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="text-right hidden sm:block">
              <div className="text-xs text-slate-400">Tasks Completed</div>
              <div className="text-lg font-black text-white mt-0.5">
                {tasks.filter((t) => t.is_completed).length} of {tasks.length}
              </div>
            </div>
            <div className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300">
              <Flame className="w-5 h-5 text-amber-400 fill-amber-400" />
              <div>
                <div className="text-[10px] uppercase font-bold tracking-wider text-amber-400/80">Streak Guard</div>
                <div className="text-xs font-extrabold text-white">Active Daily Pace</div>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-5 w-full bg-slate-800 rounded-full h-3 overflow-hidden p-0.5 border border-slate-700/50">
          <div
            className="h-full rounded-full bg-gradient-to-r from-brand-500 via-indigo-500 to-emerald-400 transition-all duration-500"
            style={{ width: `${percentComplete}%` }}
          />
        </div>
      </div>

      {/* Category Overview Cards */}
      {Object.keys(categoryOverview).length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-3.5 h-3.5 text-brand-400" />
              Domain Breakdown
            </span>
            <span className="text-[11px] text-slate-500">Click any card to filter by domain</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {Object.entries(categoryOverview).map(([catKey, stats]) => {
              const cat = CATEGORY_DEFINITIONS[catKey] || CATEGORY_DEFINITIONS.coding;
              const Icon = cat.icon;
              const pct = Math.round((stats.completed / (stats.total || 1)) * 100);
              const isSelected = filterCategory === catKey;

              return (
                <button
                  key={catKey}
                  onClick={() => setFilterCategory(isSelected ? 'ALL' : catKey)}
                  className={`p-3.5 rounded-2xl border text-left transition-all duration-200 relative overflow-hidden group ${
                    isSelected
                      ? `${cat.badgeBg} ring-2 ring-brand-500 shadow-lg`
                      : 'bg-slate-900/70 border-slate-800 hover:border-slate-700 hover:bg-slate-850'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <div className={`p-2 rounded-xl bg-slate-800/80 border border-slate-700/60 ${cat.accent}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    {stats.completed === stats.total && stats.total > 0 ? (
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" /> Done
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold text-slate-400">
                        {pct}%
                      </span>
                    )}
                  </div>
                  <div className="text-xs font-bold text-white truncate group-hover:text-brand-300 transition">
                    {cat.shortLabel}
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5 flex items-center justify-between">
                    <span>{stats.completed}/{stats.total} tasks</span>
                    <span>{stats.minutes}m</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1 mt-2.5 overflow-hidden">
                    <div
                      className={`h-full rounded-full bg-gradient-to-r ${cat.progressColor} transition-all duration-300`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Automated Email Report Status Banner */}
      <div className={`p-4 rounded-2xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition shadow-lg ${
        tasks.length > 0 && tasks.filter((t) => !t.is_completed).length === 0
          ? 'bg-emerald-950/40 border-emerald-500/30'
          : 'bg-slate-900/70 border-slate-800'
      }`}>
        <div className="flex items-center gap-3.5">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
            tasks.length > 0 && tasks.filter((t) => !t.is_completed).length === 0
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
          }`}>
            <Mail className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs font-bold text-white flex items-center gap-2">
              <span>Automated Daily Email Reports</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                Verified Email
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              {tasks.length > 0 && tasks.filter((t) => !t.is_completed).length === 0
                ? 'All tasks completed! Your full daily study completion report is automatically dispatched to your email.'
                : 'Complete all tasks to automatically receive your full report, or trigger a summary of pending tasks to your email.'}
            </p>
          </div>
        </div>

        <button
          onClick={handleSendDailyReport}
          disabled={sendingReport || tasks.length === 0}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold shrink-0 transition disabled:opacity-50 ${
            tasks.length > 0 && tasks.filter((t) => !t.is_completed).length === 0
              ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20'
              : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
          }`}
        >
          <Send className={`w-3.5 h-3.5 ${sendingReport ? 'animate-spin' : ''}`} />
          <span>
            {sendingReport
              ? 'Sending Report...'
              : tasks.length > 0 && tasks.filter((t) => !t.is_completed).length === 0
              ? 'Resend Completion Report'
              : 'Email Pending Tasks Alert'}
          </span>
        </button>
      </div>

      {/* Filter Tabs & View Mode Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-2 flex-wrap">
          {/* Status Tabs */}
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800">
            {['ALL', 'PENDING', 'COMPLETED'].map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition ${
                  filterStatus === status
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                {status.charAt(0) + status.slice(1).toLowerCase()}
              </button>
            ))}
          </div>

          {/* View Mode Switcher */}
          <div className="flex items-center gap-1 p-1 rounded-xl bg-slate-900 border border-slate-800">
            <button
              onClick={() => setViewMode('categorized')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                viewMode === 'categorized'
                  ? 'bg-slate-700 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
              title="Group tasks by category"
            >
              <LayoutGrid className="w-3.5 h-3.5" />
              <span>Categorized</span>
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                viewMode === 'list'
                  ? 'bg-slate-700 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
              title="Flat list of tasks"
            >
              <List className="w-3.5 h-3.5" />
              <span>List</span>
            </button>
          </div>
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          <button
            onClick={() => setFilterCategory('ALL')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition ${
              filterCategory === 'ALL'
                ? 'bg-slate-700 text-white'
                : 'bg-slate-900/60 text-slate-400 border border-slate-800 hover:text-white'
            }`}
          >
            All ({filteredTasks.length})
          </button>
          {Object.entries(CATEGORY_DEFINITIONS).map(([key, cat]) => {
            const count = tasks.filter((t) => resolveCategoryKey(t.task_type) === key).length;
            if (count === 0) return null;
            return (
              <button
                key={key}
                onClick={() => setFilterCategory(key)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition flex items-center gap-1.5 ${
                  filterCategory === key
                    ? 'bg-brand-600 text-white'
                    : 'bg-slate-900/60 text-slate-400 border border-slate-800 hover:text-white'
                }`}
              >
                <span>{cat.shortLabel}</span>
                <span className="text-[10px] opacity-75 font-mono">({count})</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Task List / Categorized Groups */}
      <div className="space-y-6">
        {loading ? (
          <div className="py-20 text-center text-slate-400">
            <RefreshCw className="w-7 h-7 animate-spin mx-auto mb-2 text-brand-400" />
            Loading your daily task schedule...
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="py-20 text-center rounded-2xl bg-slate-900/40 border border-slate-800/80 p-8">
            <CheckSquare className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="font-bold text-white text-base">No tasks match your filter</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
              {tasks.length === 0
                ? 'Click "Regenerate Plan" above to create your custom daily schedule based on your target role!'
                : 'Try adjusting your status or category filters to view other scheduled tasks.'}
            </p>
          </div>
        ) : viewMode === 'categorized' ? (
          /* Categorized Grouped View */
          Object.entries(categorizedTasks).map(([catKey, groupTasks]) => {
            const cat = CATEGORY_DEFINITIONS[catKey] || CATEGORY_DEFINITIONS.coding;
            const CatIcon = cat.icon;
            const isCollapsed = Boolean(collapsedCategories[catKey]);
            const completedCount = groupTasks.filter((t) => t.is_completed).length;
            const totalMinutes = groupTasks.reduce((acc, t) => acc + (t.estimated_minutes || 0), 0);
            const isAllCompleted = completedCount === groupTasks.length && groupTasks.length > 0;

            return (
              <div
                key={catKey}
                className={`rounded-2xl border ${cat.borderColor} bg-slate-900/60 overflow-hidden shadow-xl transition-all duration-200`}
              >
                {/* Category Section Header Banner */}
                <div
                  className={`p-4 bg-gradient-to-r ${cat.cardBg} border-b ${cat.borderColor} flex items-center justify-between gap-4 cursor-pointer select-none`}
                  onClick={() => toggleCategoryCollapse(catKey)}
                >
                  <div className="flex items-center gap-3.5">
                    <div className={`p-2.5 rounded-xl bg-slate-900/90 border ${cat.borderColor} ${cat.accent} shadow-md`}>
                      <CatIcon className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="text-sm font-bold text-white tracking-wide">{cat.label}</h3>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${cat.badgeBg}`}>
                          {groupTasks.length} {groupTasks.length === 1 ? 'task' : 'tasks'}
                        </span>
                        {isAllCompleted ? (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" /> Section Completed
                          </span>
                        ) : (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                            {completedCount}/{groupTasks.length} Done
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-400 mt-0.5">{cat.tagline}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <div className="text-right hidden sm:block text-xs font-semibold text-slate-400">
                      <span>{totalMinutes} mins</span>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleCategoryCollapse(catKey);
                      }}
                      className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white transition"
                      title={isCollapsed ? 'Expand category' : 'Collapse category'}
                    >
                      {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Task Cards in this Category */}
                {!isCollapsed && (
                  <div className="p-4 space-y-3 bg-slate-950/40">
                    {groupTasks.map(renderTaskCard)}
                  </div>
                )}
              </div>
            );
          })
        ) : (
          /* Flat List View */
          <div className="space-y-3">
            {filteredTasks.map(renderTaskCard)}
          </div>
        )}
      </div>

      {/* Add Custom Task Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md p-6 shadow-2xl relative">
            <h3 className="font-bold text-white text-lg">Add Custom Task</h3>
            <p className="text-xs text-slate-400 mt-0.5">Schedule a personal study or coding target</p>

            <form onSubmit={handleCreateTask} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Task Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Implement Binary Search Tree in Python"
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  className="w-full px-3.5 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white focus:border-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Description / Notes</label>
                <textarea
                  rows={2}
                  placeholder="Details, key invariants, or specific test cases..."
                  value={newTaskDesc}
                  onChange={(e) => setNewTaskDesc(e.target.value)}
                  className="w-full px-3.5 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white focus:border-brand-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Category</label>
                  <select
                    value={newTaskType}
                    onChange={(e) => setNewTaskType(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white focus:border-brand-500 focus:outline-none"
                  >
                    <option value="leetcode">DSA & Coding Practice</option>
                    <option value="github">Projects & Portfolio Building</option>
                    <option value="interview">Interview Readiness & Behavioral</option>
                    <option value="general">System Design & Technical Reading</option>
                    <option value="language">Language & Fluency Practice</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Est. Minutes</label>
                  <input
                    type="number"
                    min="5"
                    max="300"
                    step="5"
                    value={newTaskMinutes}
                    onChange={(e) => setNewTaskMinutes(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white focus:border-brand-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Difficulty</label>
                  <select
                    value={newTaskDiff}
                    onChange={(e) => setNewTaskDiff(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white focus:border-brand-500 focus:outline-none"
                  >
                    <option value="Easy">Easy</option>
                    <option value="Medium">Medium</option>
                    <option value="Hard">Hard</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Resource URL (Optional)</label>
                  <input
                    type="url"
                    placeholder="https://..."
                    value={newTaskUrl}
                    onChange={(e) => setNewTaskUrl(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white focus:border-brand-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="pt-3 flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 py-2 px-4 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-700 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={addingTask}
                  className="flex-1 py-2 px-4 rounded-xl bg-brand-600 text-white text-xs font-semibold hover:bg-brand-500 transition shadow-md shadow-brand-500/20 disabled:opacity-50"
                >
                  {addingTask ? 'Saving...' : 'Add Task'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
