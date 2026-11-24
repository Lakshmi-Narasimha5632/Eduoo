import React, { useState, useEffect } from 'react';
import {
  Cpu,
  RefreshCw,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Link2,
  Trash2,
  Search,
  Code2,
  Github,
  Award,
  Globe,
  BookOpen,
  X,
  Plus,
  Check,
} from 'lucide-react';
import { api } from '../api/client';

const PLATFORM_CONFIGS = {
  leetcode: {
    name: 'LeetCode',
    icon: Code2,
    color: 'from-amber-500 to-orange-600',
    desc: 'Problem solving stats, difficulty breakdown, and recent submissions.',
    authType: 'username',
  },
  github: {
    name: 'GitHub',
    icon: Github,
    color: 'from-slate-700 to-slate-900',
    desc: 'Repositories, stars, programming languages, and commit activity.',
    authType: 'username',
  },
  duolingo: {
    name: 'Duolingo',
    icon: Globe,
    color: 'from-emerald-500 to-green-600',
    desc: 'Language learning streak, XP progress, and active languages.',
    authType: 'username',
  },
  hackerrank: {
    name: 'HackerRank',
    icon: Award,
    color: 'from-green-600 to-teal-700',
    desc: 'Skill badges, competitive programming badges, and profile score.',
    authType: 'username',
  },
  codechef: {
    name: 'CodeChef',
    icon: Award,
    color: 'from-yellow-600 to-amber-700',
    desc: 'Global rating, star division, and contest participation stats.',
    authType: 'username',
  },
  linkedin: {
    name: 'LinkedIn',
    icon: Globe,
    color: 'from-blue-600 to-indigo-700',
    desc: 'Professional profile connection and industry networking tracking.',
    authType: 'oauth',
  },
};

export const Platforms = () => {
  const [accounts, setAccounts] = useState([]);
  const [unified, setUnified] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncingPlatform, setSyncingPlatform] = useState(null);
  const [syncAllLoading, setSyncAllLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Connect Modal State
  const [connectModalPlatform, setConnectModalPlatform] = useState(null);
  const [usernameInput, setUsernameInput] = useState('');
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [submittingConnect, setSubmittingConnect] = useState(false);

  // Disconnect State
  const [disconnectingPlatform, setDisconnectingPlatform] = useState(null);
  const [confirmDisconnectPlatform, setConfirmDisconnectPlatform] = useState(null);

  // LeetCode Catalog Modal State
  const [showCatalogModal, setShowCatalogModal] = useState(false);
  const [catalogProblems, setCatalogProblems] = useState([]);
  const [catalogSearch, setCatalogSearch] = useState('');
  const [catalogDifficulty, setCatalogDifficulty] = useState('ALL');
  const [loadingCatalog, setLoadingCatalog] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const [accRes, uniRes] = await Promise.all([
        api.get('/platforms/'),
        api.get('/platforms/unified/'),
      ]);
      const list = Array.isArray(accRes?.platforms)
        ? accRes.platforms
        : (Array.isArray(accRes?.accounts) ? accRes.accounts : (Array.isArray(accRes) ? accRes : []));
      setAccounts(list);
      setUnified(uniRes?.analytics || uniRes || null);
    } catch (err) {
      setErrorMsg(err?.message || 'Failed to load platforms data.');
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSync = async (platformKey) => {
    setSyncingPlatform(platformKey);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await api.post(`/platforms/${platformKey}/sync/`);
      setSuccessMsg(`Successfully synced ${PLATFORM_CONFIGS[platformKey]?.name || platformKey}!`);
      await fetchData();
    } catch (err) {
      setErrorMsg(err?.message || `Failed to sync ${platformKey}.`);
    } finally {
      setSyncingPlatform(null);
    }
  };

  const handleSyncAll = async () => {
    setSyncAllLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await api.post('/platforms/sync-all/');
      setSuccessMsg('Successfully synced all connected platforms!');
      await fetchData();
    } catch (err) {
      setErrorMsg(err?.message || 'Failed to sync all platforms.');
    } finally {
      setSyncAllLoading(false);
    }
  };

  const handleConnectSubmit = async (e) => {
    e.preventDefault();
    if (!connectModalPlatform || !usernameInput.trim()) return;

    setSubmittingConnect(true);
    setErrorMsg(null);
    try {
      await api.post(`/platforms/${connectModalPlatform}/connect/`, {
        username: usernameInput.trim(),
        api_key: apiKeyInput.trim() || undefined,
      });
      setSuccessMsg(`Connected ${PLATFORM_CONFIGS[connectModalPlatform].name} successfully!`);
      setConnectModalPlatform(null);
      setUsernameInput('');
      setApiKeyInput('');
      await fetchData();
    } catch (err) {
      setErrorMsg(err?.message || 'Failed to connect platform.');
    } finally {
      setSubmittingConnect(false);
    }
  };

  const handleDisconnect = (platformKey) => {
    setConfirmDisconnectPlatform(platformKey);
  };

  const executeDisconnect = async (platformKey) => {
    setDisconnectingPlatform(platformKey);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await api.delete(`/platforms/${platformKey}/disconnect/`);
      setSuccessMsg(`Disconnected ${PLATFORM_CONFIGS[platformKey]?.name || platformKey} successfully.`);
      setConfirmDisconnectPlatform(null);
      await fetchData();
    } catch (err) {
      setErrorMsg(err?.message || `Failed to disconnect ${platformKey}.`);
    } finally {
      setDisconnectingPlatform(null);
    }
  };

  const openCatalog = async () => {
    setShowCatalogModal(true);
    setLoadingCatalog(true);
    try {
      const res = await api.get('/platforms/leetcode/catalog/');
      setCatalogProblems(res.catalog || res || []);
    } catch {
      // Fallback
    } finally {
      setLoadingCatalog(false);
    }
  };

  const [addedCatalogProblems, setAddedCatalogProblems] = useState({});
  const [addingProblemSlug, setAddingProblemSlug] = useState(null);

  const handleAddProblemToTasks = async (problem) => {
    setAddingProblemSlug(problem.title_slug);
    try {
      await api.post('/tasks/', {
        title: `LeetCode: ${problem.title}`,
        description: `Solve ${problem.title} (${problem.difficulty}) to strengthen algorithm problem solving.`,
        task_type: 'coding',
        difficulty: problem.difficulty.toLowerCase(),
        estimated_minutes:
          problem.difficulty.toLowerCase() === 'hard'
            ? 45
            : problem.difficulty.toLowerCase() === 'easy'
            ? 20
            : 30,
        external_url: problem.url || `https://leetcode.com/problems/${problem.title_slug}/`,
      });
      setAddedCatalogProblems((prev) => ({ ...prev, [problem.title_slug]: true }));
      setSuccessMsg(`Added "${problem.title}" to today's study plan!`);
    } catch (err) {
      setErrorMsg(err?.message || 'Failed to add problem to tasks.');
    } finally {
      setAddingProblemSlug(null);
    }
  };

  const filteredCatalog = catalogProblems.filter((p) => {
    const matchesSearch = p.title.toLowerCase().includes(catalogSearch.toLowerCase()) ||
      p.topic_tags?.some((t) => t.toLowerCase().includes(catalogSearch.toLowerCase()));
    const matchesDiff = catalogDifficulty === 'ALL' || p.difficulty.toUpperCase() === catalogDifficulty;
    return matchesSearch && matchesDiff;
  });

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-3">
            <Cpu className="w-7 h-7 text-brand-400" />
            Platform Integrations
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Connect your developer, problem-solving, and language platforms for automated 360° career tracking.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={openCatalog}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition shadow-sm"
          >
            <BookOpen className="w-4 h-4 text-amber-400" />
            LeetCode Catalog
          </button>
          <button
            onClick={handleSyncAll}
            disabled={syncAllLoading}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-brand-500/25 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncAllLoading ? 'animate-spin' : ''}`} />
            <span>{syncAllLoading ? 'Syncing All...' : 'Sync All Platforms'}</span>
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

      {/* Unified Stats Banner */}
      {unified && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-5 rounded-2xl bg-gradient-to-br from-slate-900/90 to-slate-800/80 border border-slate-700/60 shadow-xl">
          <div className="border-r border-slate-800/80 pr-4">
            <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Solved</div>
            <div className="text-2xl font-black text-white mt-1">{unified.total_problems_solved || 0}</div>
            <div className="text-[11px] text-brand-400 mt-0.5">Across coding platforms</div>
          </div>
          <div className="border-r border-slate-800/80 pr-4">
            <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">GitHub Repos</div>
            <div className="text-2xl font-black text-white mt-1">{unified.total_repositories || 0}</div>
            <div className="text-[11px] text-emerald-400 mt-0.5">Tracked repositories</div>
          </div>
          <div className="border-r border-slate-800/80 pr-4">
            <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">Language XP</div>
            <div className="text-2xl font-black text-white mt-1">{unified.total_language_xp?.toLocaleString() || 0}</div>
            <div className="text-[11px] text-amber-400 mt-0.5">Duolingo progress</div>
          </div>
          <div>
            <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">Connected</div>
            <div className="text-2xl font-black text-white mt-1">
              {accounts.filter((a) => Boolean(a.connected || a.is_active)).length} / 6
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5">Platforms active</div>
          </div>
        </div>
      )}

      {/* Platform Cards Grid */}
      {loading ? (
        <div className="py-20 text-center text-slate-400">
          <RefreshCw className="w-7 h-7 animate-spin mx-auto mb-2 text-brand-400" />
          Loading platform integrations...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(PLATFORM_CONFIGS).map(([key, config]) => {
          const account = accounts.find(
            (a) => a.platform.toLowerCase() === key.toLowerCase() && Boolean(a.connected || a.is_active)
          );
          const isConnected = !!account;
          const Icon = config.icon;
          const isSyncing = syncingPlatform === key;

          return (
            <div
              key={key}
              className={`rounded-2xl border transition-all duration-300 flex flex-col justify-between p-6 ${
                isConnected
                  ? 'bg-slate-900/90 border-slate-700/80 shadow-lg shadow-black/20 hover:border-slate-600'
                  : 'bg-slate-900/40 border-slate-800/60 opacity-85 hover:opacity-100 hover:border-slate-700'
              }`}
            >
              <div>
                {/* Header */}
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-11 h-11 rounded-xl bg-gradient-to-tr ${config.color} flex items-center justify-center text-white shadow-md`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-white text-base">{config.name}</h3>
                      <div className="flex items-center gap-1.5 mt-0.5">
                        <span
                          className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`}
                        />
                        <span className={`text-xs font-medium ${isConnected ? 'text-emerald-400' : 'text-slate-500'}`}>
                          {isConnected ? 'Connected' : 'Not Connected'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {isConnected && (
                    <button
                      onClick={() => handleDisconnect(key)}
                      disabled={disconnectingPlatform === key}
                      title="Disconnect platform"
                      className="text-slate-500 hover:text-rose-400 transition p-1.5 rounded-lg hover:bg-slate-800 disabled:opacity-50"
                    >
                      {disconnectingPlatform === key ? (
                        <RefreshCw className="w-4 h-4 animate-spin text-rose-400" />
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </button>
                  )}
                </div>

                {/* Description */}
                <p className="text-xs text-slate-400 mt-4 leading-relaxed">{config.desc}</p>

                {/* Connected Details / Metrics */}
                {isConnected && account && (
                  <div className="mt-4 p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/50 text-xs space-y-1.5">
                    <div className="flex justify-between text-slate-300">
                      <span className="text-slate-400">Username:</span>
                      <span className="font-semibold text-white font-mono">{account.username}</span>
                    </div>
                    {account.last_synced_at && (
                      <div className="flex justify-between text-slate-400 text-[11px]">
                        <span>Last Synced:</span>
                        <span>{new Date(account.last_synced_at).toLocaleDateString()}</span>
                      </div>
                    )}
                    {account.raw_data && key === 'leetcode' && (
                      <div className="flex justify-between text-amber-300 font-semibold pt-1 border-t border-slate-700/50">
                        <span>Problems Solved:</span>
                        <span>{account.raw_data.total_solved || account.raw_data.solved || 'Synced'}</span>
                      </div>
                    )}
                    {account.raw_data && key === 'github' && (
                      <div className="flex justify-between text-emerald-300 font-semibold pt-1 border-t border-slate-700/50">
                        <span>Public Repos:</span>
                        <span>{account.raw_data.total_repositories ?? account.raw_data.public_repos ?? 'Synced'}</span>
                      </div>
                    )}
                    {account.raw_data && key === 'hackerrank' && (
                      <div className="space-y-1 pt-1 border-t border-slate-700/50">
                        <div className="flex justify-between text-teal-300 font-semibold">
                          <span>Problems Solved:</span>
                          <span>{account.raw_data.total_solved ?? account.raw_data.problems_solved ?? account.raw_data.challenges ?? 'Synced'}</span>
                        </div>
                        <div className="flex justify-between text-slate-300 text-[11px]">
                          <span>Skill Badges:</span>
                          <span className="font-bold text-amber-400">
                            {account.raw_data.badges ?? 0} {account.raw_data.stars ? `(${account.raw_data.stars}★)` : ''}
                          </span>
                        </div>
                      </div>
                    )}
                    {account.raw_data && key === 'codechef' && (
                      <div className="space-y-1 pt-1 border-t border-slate-700/50">
                        <div className="flex justify-between text-amber-300 font-semibold">
                          <span>Rating:</span>
                          <span>{account.raw_data.rating ? `${account.raw_data.rating} (${account.raw_data.stars ? `${account.raw_data.stars}★` : 'Div 3'})` : 'Active'}</span>
                        </div>
                        <div className="flex justify-between text-slate-300 text-[11px]">
                          <span>Problems Solved:</span>
                          <span className="font-bold text-white">
                            {account.raw_data.total_solved ?? account.raw_data.solved_problems ?? 0}
                          </span>
                        </div>
                        {account.raw_data.global_rank && (
                          <div className="flex justify-between text-slate-400 text-[11px]">
                            <span>Global Rank:</span>
                            <span className="font-mono text-slate-200">#{account.raw_data.global_rank}</span>
                          </div>
                        )}
                      </div>
                    )}
                    {account.raw_data && key === 'duolingo' && (
                      <div className="flex justify-between text-emerald-300 font-semibold pt-1 border-t border-slate-700/50">
                        <span>Language XP:</span>
                        <span>{account.raw_data.total_xp ?? account.raw_data.xp ?? 'Synced'}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="mt-6 pt-4 border-t border-slate-800/80">
                {isConnected ? (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleSync(key)}
                      disabled={isSyncing || disconnectingPlatform === key}
                      className="flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition disabled:opacity-50"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 text-brand-400 ${isSyncing ? 'animate-spin' : ''}`} />
                      <span>{isSyncing ? 'Syncing...' : 'Sync Now'}</span>
                    </button>
                    <button
                      onClick={() => handleDisconnect(key)}
                      disabled={disconnectingPlatform === key || isSyncing}
                      className="flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 hover:text-rose-300 text-xs font-semibold border border-rose-500/20 transition disabled:opacity-50"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      <span>Disconnect</span>
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => {
                      setConnectModalPlatform(key);
                      setUsernameInput('');
                      setApiKeyInput('');
                    }}
                    className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition"
                  >
                    <Link2 className="w-3.5 h-3.5" />
                    <span>Connect {config.name}</span>
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
      )}

      {/* Disconnect Confirmation Modal */}
      {confirmDisconnectPlatform && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-sm p-6 shadow-2xl relative animate-in fade-in zoom-in duration-150">
            <h3 className="text-lg font-bold text-white mb-2">Disconnect Platform?</h3>
            <p className="text-sm text-slate-300 mb-6 leading-relaxed">
              Are you sure you want to disconnect <span className="font-semibold text-white">{PLATFORM_CONFIGS[confirmDisconnectPlatform]?.name || confirmDisconnectPlatform}</span>?
              Your platform username and cached telemetry will be cleared.
            </p>
            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setConfirmDisconnectPlatform(null)}
                disabled={disconnectingPlatform === confirmDisconnectPlatform}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-800 transition"
              >
                Cancel
              </button>
              <button
                onClick={() => executeDisconnect(confirmDisconnectPlatform)}
                disabled={disconnectingPlatform === confirmDisconnectPlatform}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-lg shadow-rose-600/30 transition disabled:opacity-50"
              >
                {disconnectingPlatform === confirmDisconnectPlatform && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                <span>{disconnectingPlatform === confirmDisconnectPlatform ? 'Disconnecting...' : 'Yes, Disconnect'}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Connect Modal */}
      {connectModalPlatform && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md p-6 shadow-2xl relative animate-in fade-in zoom-in duration-150">
            <button
              onClick={() => setConnectModalPlatform(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3 mb-5">
              <div
                className={`w-10 h-10 rounded-xl bg-gradient-to-tr ${
                  PLATFORM_CONFIGS[connectModalPlatform]?.color
                } flex items-center justify-center text-white`}
              >
                <Link2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-white text-lg">
                  Connect {PLATFORM_CONFIGS[connectModalPlatform]?.name}
                </h3>
                <p className="text-xs text-slate-400">Enter your public profile username or handle</p>
              </div>
            </div>

            <form onSubmit={handleConnectSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  {PLATFORM_CONFIGS[connectModalPlatform]?.name} Username
                </label>
                <input
                  type="text"
                  required
                  placeholder={`e.g. john_doe`}
                  value={usernameInput}
                  onChange={(e) => setUsernameInput(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-800/80 border border-slate-700 rounded-xl text-white text-sm focus:outline-none focus:border-brand-500 font-mono"
                />
              </div>

              {connectModalPlatform === 'github' && (
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">
                    Personal Access Token <span className="text-slate-500">(Optional for higher rate limits)</span>
                  </label>
                  <input
                    type="password"
                    placeholder="ghp_..."
                    value={apiKeyInput}
                    onChange={(e) => setApiKeyInput(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-800/80 border border-slate-700 rounded-xl text-white text-sm focus:outline-none focus:border-brand-500 font-mono"
                  />
                </div>
              )}

              <div className="pt-2 flex gap-3">
                <button
                  type="button"
                  onClick={() => setConnectModalPlatform(null)}
                  className="flex-1 py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingConnect}
                  className="flex-1 py-2.5 px-4 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition shadow-lg shadow-brand-500/25 disabled:opacity-50"
                >
                  {submittingConnect ? 'Connecting...' : 'Connect Account'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* LeetCode Catalog Modal */}
      {showCatalogModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl relative">
            {/* Header */}
            <div className="p-5 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <BookOpen className="w-6 h-6 text-amber-400" />
                <div>
                  <h3 className="font-bold text-white text-lg">LeetCode Curated Problem Catalog</h3>
                  <p className="text-xs text-slate-400">Search and practice interview-standard coding challenges</p>
                </div>
              </div>
              <button
                onClick={() => setShowCatalogModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Filter Bar */}
            <div className="p-4 bg-slate-855 border-b border-slate-800 flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  placeholder="Search problem title or topic tag (e.g. Dynamic Programming, Two Pointers)..."
                  value={catalogSearch}
                  onChange={(e) => setCatalogSearch(e.target.value)}
                  className="w-full pl-9 pr-3.5 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
                />
              </div>

              <div className="flex gap-2">
                {['ALL', 'EASY', 'MEDIUM', 'HARD'].map((diff) => (
                  <button
                    key={diff}
                    onClick={() => setCatalogDifficulty(diff)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                      catalogDifficulty === diff
                        ? 'bg-brand-600 text-white'
                        : 'bg-slate-800 text-slate-400 hover:text-white'
                    }`}
                  >
                    {diff}
                  </button>
                ))}
              </div>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-2.5">
              {loadingCatalog ? (
                <div className="py-16 text-center text-slate-400 text-sm">
                  <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-brand-400" />
                  Loading problem catalog...
                </div>
              ) : filteredCatalog.length === 0 ? (
                <div className="py-16 text-center text-slate-500 text-xs">
                  No problems match your filter criteria.
                </div>
              ) : (
                filteredCatalog.map((problem, i) => (
                  <div
                    key={i}
                    className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60 hover:border-slate-600 flex items-center justify-between gap-4 transition"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-mono text-slate-500 w-10">#{problem.frontend_id || i + 1}</span>
                      <div>
                        <div className="font-semibold text-white text-sm">{problem.title}</div>
                        <div className="flex flex-wrap gap-1.5 mt-1">
                          {problem.topic_tags?.map((t, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-0.5 rounded-md bg-slate-700/50 text-[10px] text-slate-300"
                            >
                              {t}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <span
                        className={`text-[11px] font-bold px-2.5 py-1 rounded-full ${
                          problem.difficulty?.toUpperCase() === 'EASY'
                            ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                            : problem.difficulty?.toUpperCase() === 'MEDIUM'
                            ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
                            : 'bg-rose-500/15 text-rose-300 border border-rose-500/30'
                        }`}
                      >
                        {problem.difficulty}
                      </span>
                      <button
                        onClick={() => handleAddProblemToTasks(problem)}
                        disabled={addingProblemSlug === problem.title_slug || addedCatalogProblems[problem.title_slug]}
                        className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 border transition ${
                          addedCatalogProblems[problem.title_slug]
                            ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                            : 'bg-slate-700/60 hover:bg-slate-700 text-slate-200 border-slate-600 hover:text-white'
                        }`}
                        title="Add problem directly to today's study plan"
                      >
                        {addedCatalogProblems[problem.title_slug] ? (
                          <>
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                            <span>Planned</span>
                          </>
                        ) : (
                          <>
                            <Plus className="w-3.5 h-3.5 text-brand-400" />
                            <span>{addingProblemSlug === problem.title_slug ? 'Adding...' : 'Add to Plan'}</span>
                          </>
                        )}
                      </button>
                      <a
                        href={problem.url || `https://leetcode.com/problems/${problem.title_slug}/`}
                        target="_blank"
                        rel="noreferrer"
                        className="p-2 rounded-lg bg-slate-700/60 hover:bg-brand-600 text-slate-300 hover:text-white transition"
                        title="Solve on LeetCode"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Platforms;
