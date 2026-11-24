import React, { useState, useEffect } from 'react';
import {
  Lightbulb,
  AlertTriangle,
  Info,
  CheckCircle,
  RefreshCw,
  Sparkles,
  ArrowRight,
  Filter,
  X,
  Code2,
  Award,
  Layers,
  Flame,
  Briefcase,
  MessagesSquare,
  FolderGit2,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';

const CATEGORY_CONFIG = {
  all: {
    label: 'All Insights',
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
  platforms: {
    label: 'Platforms',
    icon: Award,
    color: 'text-indigo-400',
    badge: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30',
  },
  interview: {
    label: 'Interview',
    icon: MessagesSquare,
    color: 'text-amber-400',
    badge: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
  },
  career: {
    label: 'Career',
    icon: Briefcase,
    color: 'text-blue-400',
    badge: 'bg-blue-500/10 text-blue-300 border-blue-500/30',
  },
  consistency: {
    label: 'Consistency',
    icon: Flame,
    color: 'text-rose-400',
    badge: 'bg-rose-500/10 text-rose-300 border-rose-500/30',
  },
  skills: {
    label: 'Skills',
    icon: Layers,
    color: 'text-teal-400',
    badge: 'bg-teal-500/10 text-teal-300 border-teal-500/30',
  },
  projects: {
    label: 'Projects',
    icon: FolderGit2,
    color: 'text-sky-400',
    badge: 'bg-sky-500/10 text-sky-300 border-sky-500/30',
  },
};

export const Insights = () => {
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [filterPriority, setFilterPriority] = useState('ALL');
  const [filterCategory, setFilterCategory] = useState('ALL');
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const navigate = useNavigate();

  const fetchInsights = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.get('/insights/');
      const list = Array.isArray(res?.insights)
        ? res.insights
        : Array.isArray(res)
        ? res
        : [];
      setInsights(list);
    } catch (err) {
      setErrorMsg(err?.message || 'Failed to fetch insights.');
      setInsights([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await api.post('/insights/generate/');
      setSuccessMsg('Successfully analyzed your coding telemetry and formulated fresh category insights!');
      await fetchInsights();
    } catch (err) {
      setErrorMsg(err?.message || 'Failed to generate insights.');
    } finally {
      setGenerating(false);
    }
  };

  const handleDismiss = async (id) => {
    try {
      await api.post(`/insights/${id}/dismiss/`);
      setInsights((prev) => prev.filter((i) => i.id !== id));
    } catch {
      setInsights((prev) => prev.filter((i) => i.id !== id));
    }
  };

  // Normalize category helper
  const getNormalizedCategory = (item) => {
    const raw = (item.category || item.platform || '').toLowerCase();
    if (['coding', 'difficulty', 'topic', 'performance'].includes(raw)) return 'coding';
    if (['platform', 'platforms', 'activity'].includes(raw)) return 'platforms';
    if (['projects', 'project'].includes(raw)) return 'projects';
    if (['skills', 'skill_gap', 'skill'].includes(raw)) return 'skills';
    if (['career', 'interview', 'consistency'].includes(raw)) return raw;
    return 'career';
  };

  // Category counts
  const categoryCounts = insights.reduce((acc, curr) => {
    const cat = getNormalizedCategory(curr);
    acc[cat] = (acc[cat] || 0) + 1;
    return acc;
  }, {});

  const filteredInsights = insights.filter((item) => {
    if (filterPriority !== 'ALL' && item.priority?.toLowerCase() !== filterPriority.toLowerCase()) return false;
    if (filterCategory !== 'ALL') {
      const norm = getNormalizedCategory(item);
      if (norm !== filterCategory.toLowerCase()) return false;
    }
    return true;
  });

  const highCount = insights.filter((i) => i.priority?.toLowerCase() === 'high').length;
  const mediumCount = insights.filter((i) => i.priority?.toLowerCase() === 'medium').length;

  const categories = ['ALL', 'coding', 'platforms', 'interview', 'career', 'consistency', 'skills', 'projects'];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-3">
            <Lightbulb className="w-7 h-7 text-amber-400" />
            Category-Wise AI Insights
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Multidimensional intelligence analyzing your LeetCode, HackerRank, CodeChef, and GitHub signals across key domains.
          </p>
        </div>

        <button
          onClick={handleGenerate}
          disabled={generating}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-brand-500/25 transition disabled:opacity-50"
        >
          <Sparkles className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
          <span>{generating ? 'Synthesizing...' : 'Regenerate Insights'}</span>
        </button>
      </div>

      {/* Notifications */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}
      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-sm flex items-center gap-3">
          <CheckCircle className="w-5 h-5 shrink-0 text-emerald-400" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Stats Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Total Insights</span>
            <div className="text-2xl font-black text-white mt-1">{insights.length}</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-brand-500/10 flex items-center justify-center text-brand-400">
            <Lightbulb className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">High Priority</span>
            <div className="text-2xl font-black text-rose-400 mt-1">{highCount}</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-rose-500/10 flex items-center justify-center text-rose-400">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Medium Priority</span>
            <div className="text-2xl font-black text-amber-400 mt-1">{mediumCount}</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-400">
            <Info className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="p-2 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
        <div className="flex items-center justify-between px-2 pt-1 pb-2 border-b border-slate-800/80">
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Categories:</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] text-slate-400 font-medium mr-1">Priority:</span>
            {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map((p) => (
              <button
                key={p}
                onClick={() => setFilterPriority(p)}
                className={`px-2.5 py-0.5 rounded-lg text-[11px] font-bold transition ${
                  filterPriority === p ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-400 hover:text-white bg-slate-800/70'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {categories.map((catKey) => {
            const isAll = catKey === 'ALL';
            const normKey = catKey.toLowerCase();
            const cfg = CATEGORY_CONFIG[normKey] || CATEGORY_CONFIG.career;
            const Icon = cfg.icon;
            const count = isAll ? insights.length : (categoryCounts[normKey] || 0);
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

      {/* Insights Cards Grid */}
      <div className="space-y-4">
        {loading ? (
          <div className="py-20 text-center text-slate-400">
            <RefreshCw className="w-7 h-7 animate-spin mx-auto mb-2 text-brand-400" />
            Analyzing your platforms for category insights...
          </div>
        ) : filteredInsights.length === 0 ? (
          <div className="py-20 text-center rounded-2xl bg-slate-900/40 border border-slate-800/80 p-8">
            <Lightbulb className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="font-bold text-white text-base">No insights in this category</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
              {insights.length === 0
                ? 'Click "Regenerate Insights" to synthesize observations from your connected platforms.'
                : 'Try selecting a different category or priority filter.'}
            </p>
          </div>
        ) : (
          filteredInsights.map((insight) => {
            const isHigh = insight.priority?.toLowerCase() === 'high';
            const isMed = insight.priority?.toLowerCase() === 'medium';
            const catNorm = getNormalizedCategory(insight);
            const cfg = CATEGORY_CONFIG[catNorm] || CATEGORY_CONFIG.career;
            const CatIcon = cfg.icon;

            return (
              <div
                key={insight.id}
                className={`p-6 rounded-2xl border transition-all duration-200 bg-slate-900/90 shadow-md ${
                  isHigh
                    ? 'border-rose-500/30 hover:border-rose-500/50'
                    : isMed
                    ? 'border-amber-500/30 hover:border-amber-500/50'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      {/* Priority Tag */}
                      <span
                        className={`text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full border ${
                          isHigh
                            ? 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                            : isMed
                            ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                            : 'bg-sky-500/15 text-sky-300 border-sky-500/30'
                        }`}
                      >
                        {insight.priority} Priority
                      </span>

                      {/* Category Tag */}
                      <span
                        className={`inline-flex items-center gap-1.5 text-xs font-bold px-2.5 py-0.5 rounded-full border ${cfg.badge}`}
                      >
                        <CatIcon className="w-3 h-3" />
                        <span>{cfg.label}</span>
                      </span>

                      {/* Platform Tag if specific */}
                      {insight.platform && insight.platform.toLowerCase() !== 'eduoo_ai' && (
                        <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 uppercase">
                          {insight.platform}
                        </span>
                      )}

                      {insight.created_at && (
                        <span className="text-[11px] text-slate-500">
                          {new Date(insight.created_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>

                    <h3 className="text-base font-bold text-white mt-2.5">{insight.title}</h3>
                    <p className="text-xs text-slate-300 mt-2 leading-relaxed">{insight.description}</p>
                  </div>

                  <button
                    onClick={() => handleDismiss(insight.id)}
                    title="Dismiss insight"
                    className="text-slate-500 hover:text-slate-300 p-1.5 rounded-lg hover:bg-slate-800 transition"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                {/* Action Items */}
                {insight.action_items && insight.action_items.length > 0 && (
                  <div className="mt-4 p-3.5 rounded-xl bg-slate-800/50 border border-slate-700/40">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                      Suggested Action Steps:
                    </span>
                    <ul className="space-y-1.5">
                      {insight.action_items.map((action, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                          <CheckCircle className="w-3.5 h-3.5 text-brand-400 shrink-0 mt-0.5" />
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Footer Action */}
                <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-[11px] text-slate-500">Category Intelligence • Eduoo Career AI</span>
                  <button
                    onClick={() => navigate('/tasks')}
                    className="flex items-center gap-1.5 text-xs font-bold text-brand-400 hover:text-brand-300 transition"
                  >
                    <span>Apply to Daily Tasks</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default Insights;
