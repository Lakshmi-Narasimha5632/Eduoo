import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  CheckCircle2,
  Clock,
  Check,
  X,
  Plus,
  RefreshCw,
  AlertCircle,
  HelpCircle,
  FolderGit2,
  Code2,
  Filter,
  Award,
  MessagesSquare,
  FileText,
  Layers,
} from 'lucide-react';
import { api } from '../api/client';

const CATEGORY_CONFIG = {
  all: {
    label: 'All Suggestions',
    icon: Sparkles,
    color: 'text-brand-400',
    badge: 'bg-brand-500/10 text-brand-300 border-brand-500/30',
  },
  coding: {
    label: 'Coding & DSA',
    icon: Code2,
    color: 'text-emerald-400',
    badge: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
  },
  project: {
    label: 'Projects',
    icon: FolderGit2,
    color: 'text-sky-400',
    badge: 'bg-sky-500/10 text-sky-300 border-sky-500/30',
  },
  interview: {
    label: 'Interview',
    icon: MessagesSquare,
    color: 'text-amber-400',
    badge: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
  },
  resume: {
    label: 'Resume ATS',
    icon: FileText,
    color: 'text-purple-400',
    badge: 'bg-purple-500/10 text-purple-300 border-purple-500/30',
  },
  platform: {
    label: 'Platforms',
    icon: Award,
    color: 'text-indigo-400',
    badge: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30',
  },
  skills: {
    label: 'Skills',
    icon: Layers,
    color: 'text-teal-400',
    badge: 'bg-teal-500/10 text-teal-300 border-teal-500/30',
  },
};

export const Recommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [filterCategory, setFilterCategory] = useState('ALL');
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const fetchRecommendations = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.get('/recommendations/');
      const list = Array.isArray(res?.recommendations)
        ? res.recommendations
        : Array.isArray(res)
        ? res
        : [];
      setRecommendations(list);
    } catch (err) {
      setErrorMsg(err?.message || 'Failed to fetch recommendations.');
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await api.post('/recommendations/generate/');
      setSuccessMsg('Personalized recommendations generated across all learning categories!');
      await fetchRecommendations();
    } catch (err) {
      setErrorMsg(err?.message || 'Failed to generate recommendations.');
    } finally {
      setGenerating(false);
    }
  };

  const handleStatusChange = async (id, newStatus) => {
    try {
      await api.post(`/recommendations/${id}/status/`, { status: newStatus });
      if (newStatus === 'dismissed') {
        setRecommendations((prev) => prev.filter((r) => r.id !== id));
      } else {
        setRecommendations((prev) =>
          prev.map((r) => (r.id === id ? { ...r, status: newStatus } : r))
        );
      }
    } catch {
      // Local fallback
      if (newStatus === 'dismissed') {
        setRecommendations((prev) => prev.filter((r) => r.id !== id));
      } else {
        setRecommendations((prev) =>
          prev.map((r) => (r.id === id ? { ...r, status: newStatus } : r))
        );
      }
    }
  };

  const [addedTasks, setAddedTasks] = useState({});
  const [addingTaskId, setAddingTaskId] = useState(null);

  const handleAddToTasks = async (item) => {
    setAddingTaskId(item.id);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await api.post('/tasks/', {
        title: item.title,
        description: item.description,
        task_type: item.category || 'general',
        estimated_minutes: item.estimated_time_minutes || 30,
        difficulty: item.priority === 'high' ? 'Hard' : item.priority === 'low' ? 'Easy' : 'Medium',
      });
      setAddedTasks((prev) => ({ ...prev, [item.id]: true }));
      setSuccessMsg(`Added "${item.title}" to today's daily study tasks!`);
      if (item.status === 'pending') {
        await handleStatusChange(item.id, 'in_progress');
      }
    } catch (err) {
      setErrorMsg(err?.message || 'Failed to add recommendation to tasks.');
    } finally {
      setAddingTaskId(null);
    }
  };

  const getNormalizedCategory = (item) => {
    const raw = (item.category || '').toLowerCase();
    if (['coding', 'dsa'].includes(raw)) return 'coding';
    if (['project', 'projects'].includes(raw)) return 'project';
    if (['interview'].includes(raw)) return 'interview';
    if (['resume'].includes(raw)) return 'resume';
    if (['platform', 'platforms'].includes(raw)) return 'platform';
    if (['skills', 'skill', 'skill_gap'].includes(raw)) return 'skills';
    return 'coding';
  };

  const categoryCounts = recommendations.reduce((acc, curr) => {
    const cat = getNormalizedCategory(curr);
    acc[cat] = (acc[cat] || 0) + 1;
    return acc;
  }, {});

  const filtered = recommendations.filter((r) => {
    if (filterStatus !== 'ALL' && r.status.toLowerCase() !== filterStatus.toLowerCase()) return false;
    if (filterCategory !== 'ALL') {
      const norm = getNormalizedCategory(r);
      if (norm !== filterCategory.toLowerCase()) return false;
    }
    return true;
  });

  const categories = ['ALL', 'coding', 'project', 'interview', 'resume', 'platform', 'skills'];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-3">
            <Sparkles className="w-7 h-7 text-indigo-400" />
            Category-Wise AI Recommendations
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Data-backed action steps covering coding agility, portfolio depth, interview communication, and ATS resume polish.
          </p>
        </div>

        <button
          onClick={handleGenerate}
          disabled={generating}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-brand-500/25 transition disabled:opacity-50"
        >
          <Sparkles className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
          <span>{generating ? 'Formulating...' : 'Generate Suggestions'}</span>
        </button>
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

      {/* Overview Counts */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">Total</span>
          <div className="text-2xl font-black text-white mt-1">{recommendations.length}</div>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">Pending</span>
          <div className="text-2xl font-black text-amber-400 mt-1">
            {recommendations.filter((r) => r.status === 'pending').length}
          </div>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">In Progress</span>
          <div className="text-2xl font-black text-brand-400 mt-1">
            {recommendations.filter((r) => r.status === 'in_progress').length}
          </div>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">Completed</span>
          <div className="text-2xl font-black text-emerald-400 mt-1">
            {recommendations.filter((r) => r.status === 'completed').length}
          </div>
        </div>
      </div>

      {/* Category Tabs & Status Filters */}
      <div className="p-2 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
        <div className="flex items-center justify-between px-2 pt-1 pb-2 border-b border-slate-800/80">
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Categories:</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] text-slate-400 font-medium mr-1">Status:</span>
            {['ALL', 'PENDING', 'IN_PROGRESS', 'COMPLETED'].map((s) => (
              <button
                key={s}
                onClick={() => setFilterStatus(s)}
                className={`px-2.5 py-0.5 rounded-lg text-[11px] font-bold transition ${
                  filterStatus === s ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-400 hover:text-white bg-slate-800/70'
                }`}
              >
                {s.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {categories.map((catKey) => {
            const isAll = catKey === 'ALL';
            const normKey = catKey.toLowerCase();
            const cfg = CATEGORY_CONFIG[normKey] || CATEGORY_CONFIG.coding;
            const Icon = cfg.icon;
            const count = isAll ? recommendations.length : categoryCounts[normKey] || 0;
            const isSelected = filterCategory === catKey;

            return (
              <button
                key={catKey}
                onClick={() => setFilterCategory(catKey)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                  isSelected
                    ? 'bg-brand-600 text-white shadow-md shadow-brand-600/30'
                    : 'bg-slate-800/60 text-slate-300 hover:text-white hover:bg-slate-800 border border-slate-800'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isSelected ? 'text-white' : cfg.color}`} />
                <span>{cfg.label}</span>
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full font-extrabold ${
                    isSelected ? 'bg-brand-700/80 text-white' : 'bg-slate-700/80 text-slate-300'
                  }`}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Recommendations Cards Grid */}
      <div className="space-y-4">
        {loading ? (
          <div className="py-20 text-center text-slate-400">
            <RefreshCw className="w-7 h-7 animate-spin mx-auto mb-2 text-brand-400" />
            Loading career recommendations...
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-20 text-center rounded-2xl bg-slate-900/40 border border-slate-800/80 p-8">
            <Sparkles className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="font-bold text-white text-base">No recommendations in this category</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
              Click "Generate Suggestions" to formulate next actions for your learning schedule.
            </p>
          </div>
        ) : (
          filtered.map((item) => {
            const isCompleted = item.status === 'completed';
            const isInProgress = item.status === 'in_progress';
            const catNorm = getNormalizedCategory(item);
            const cfg = CATEGORY_CONFIG[catNorm] || CATEGORY_CONFIG.coding;
            const CatIcon = cfg.icon;

            return (
              <div
                key={item.id}
                className={`p-6 rounded-2xl border transition-all duration-200 bg-slate-900/90 shadow-md ${
                  isCompleted
                    ? 'border-emerald-500/20 opacity-70'
                    : isInProgress
                    ? 'border-brand-500/50'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      {/* Category Tag */}
                      <span
                        className={`inline-flex items-center gap-1.5 text-xs font-bold px-2.5 py-0.5 rounded-full border ${cfg.badge}`}
                      >
                        <CatIcon className="w-3 h-3" />
                        <span>{cfg.label}</span>
                      </span>

                      {item.estimated_time_minutes && (
                        <span className="flex items-center gap-1 text-[11px] font-semibold text-slate-400">
                          <Clock className="w-3.5 h-3.5 text-slate-500" />
                          {item.estimated_time_minutes} mins
                        </span>
                      )}

                      <span
                        className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                          isCompleted
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : isInProgress
                            ? 'bg-brand-500/10 text-brand-300 border border-brand-500/20'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {item.status.replace('_', ' ')}
                      </span>
                    </div>

                    <h3 className={`text-base font-bold mt-2.5 ${isCompleted ? 'line-through text-slate-400' : 'text-white'}`}>
                      {item.title}
                    </h3>
                    <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">{item.description}</p>

                    {item.reason && (
                      <div className="mt-3 p-2.5 rounded-lg bg-slate-800/40 border border-slate-700/30 text-xs text-brand-300 flex items-start gap-2">
                        <HelpCircle className="w-4 h-4 shrink-0 text-brand-400 mt-0.5" />
                        <span><strong>Impact:</strong> {item.reason}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex flex-row md:flex-col items-center gap-2 shrink-0">
                    <button
                      onClick={() => handleAddToTasks(item)}
                      disabled={addingTaskId === item.id || addedTasks[item.id]}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition disabled:opacity-60"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>{addedTasks[item.id] ? 'Added to Tasks' : 'Add to Tasks'}</span>
                    </button>

                    <div className="flex items-center gap-1">
                      {!isCompleted ? (
                        <button
                          onClick={() => handleStatusChange(item.id, 'completed')}
                          title="Mark complete"
                          className="p-1.5 rounded-lg text-slate-400 hover:text-emerald-400 hover:bg-slate-800 transition"
                        >
                          <Check className="w-4 h-4" />
                        </button>
                      ) : (
                        <button
                          onClick={() => handleStatusChange(item.id, 'pending')}
                          title="Reopen recommendation"
                          className="p-1.5 rounded-lg text-emerald-400 hover:bg-slate-800 transition"
                        >
                          <CheckCircle2 className="w-4 h-4" />
                        </button>
                      )}

                      <button
                        onClick={() => handleStatusChange(item.id, 'dismissed')}
                        title="Dismiss recommendation"
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default Recommendations;
