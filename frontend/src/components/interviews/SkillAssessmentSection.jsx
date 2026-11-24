import React, { useState, useEffect, useCallback } from 'react';
import {
  Code2,
  Terminal,
  Play,
  Send,
  CheckCircle2,
  Clock,
  Flame,
  Award,
  Search,
  RefreshCw,
  Copy,
  Check,
  RotateCcw,
  BookOpen,
  BarChart2,
  AlertTriangle,
  Lightbulb,
  Volume2,
  VolumeX,
} from 'lucide-react';
import { api } from '../../api/client';
import { speechSpeaker } from '../../utils/speechService';
import { useToast } from '../../context/ToastContext';

const CATEGORIES = [
  { id: 'all', label: 'All Categories' },
  { id: 'arrays', label: 'Arrays' },
  { id: 'strings', label: 'Strings' },
  { id: 'linked_lists', label: 'Linked Lists' },
  { id: 'stacks_queues', label: 'Stacks & Queues' },
  { id: 'trees_graphs', label: 'Trees & Graphs' },
  { id: 'dynamic_programming', label: 'Dynamic Programming' },
  { id: 'searching_sorting', label: 'Searching & Sorting' },
  { id: 'recursion_backtracking', label: 'Recursion & Backtracking' },
  { id: 'sql', label: 'SQL' },
  { id: 'problem_solving', label: 'Problem Solving' },
];

const DIFFICULTIES = ['all', 'easy', 'medium', 'hard'];
const LANGUAGES = [
  { id: 'python', label: 'Python 3' },
  { id: 'javascript', label: 'JavaScript (Node.js)' },
  { id: 'java', label: 'Java' },
  { id: 'cpp', label: 'C++' },
  { id: 'c', label: 'C' },
  { id: 'sql', label: 'SQL' },
];

export const SkillAssessmentSection = () => {
  const { toast } = useToast();

  // Navigation tabs
  const [activeTab, setActiveTab] = useState('challenges'); // 'challenges' | 'workspace' | 'quizzes' | 'analytics'

  // Problems & Filters
  const [problems, setProblems] = useState([]);
  const [loadingProblems, setLoadingProblems] = useState(true);
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Workspace / Code Editor State
  const [activeProblem, setActiveProblem] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [code, setCode] = useState('');
  const [running, setRunning] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [runResults, setRunResults] = useState(null);
  const [submitResult, setSubmitResult] = useState(null);
  const [activeConsoleTab, setActiveConsoleTab] = useState('testcases'); // 'testcases' | 'output' | 'solution'
  const [copied, setCopied] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);

  // Technical Quizzes / MCQ State
  const [quizzes, setQuizzes] = useState([]);
  const [activeQuiz, setActiveQuiz] = useState(null);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [quizTimer, setQuizTimer] = useState(0);
  const [submittingQuiz, setSubmittingQuiz] = useState(false);
  const [quizReview, setQuizReview] = useState(null);

  // Analytics State
  const [analytics, setAnalytics] = useState(null);
  const [, setLoadingAnalytics] = useState(false);

  // Audio speech synthesis
  const [playingAudioKey, setPlayingAudioKey] = useState(null);

  const stopSpeaking = () => {
    speechSpeaker.stop();
    setPlayingAudioKey(null);
  };

  const speakText = (text, key) => {
    if (!text) return;
    if (playingAudioKey === key) {
      stopSpeaking();
      return;
    }
    setPlayingAudioKey(key);
    speechSpeaker.speak(text, {
      id: key,
      onStart: () => setPlayingAudioKey(key),
      onEnd: () => setPlayingAudioKey((curr) => (curr === key ? null : curr)),
      onError: (err) => {
        console.warn('Speech playback notice:', err);
        setPlayingAudioKey((curr) => (curr === key ? null : curr));
      },
    });
  };

  useEffect(() => {
    return () => stopSpeaking();
  }, []);

  // Fetch problems
  const fetchProblems = useCallback(async () => {
    setLoadingProblems(true);
    try {
      const params = new URLSearchParams();
      if (selectedDifficulty !== 'all') params.append('difficulty', selectedDifficulty);
      if (selectedCategory !== 'all') params.append('category', selectedCategory);
      if (searchQuery.trim()) params.append('search', searchQuery.trim());

      const res = await api.get(`/interviews/skills/problems/?${params.toString()}`);
      setProblems(res.problems || []);
    } catch (err) {
      console.error('Failed to fetch problems:', err);
    } finally {
      setLoadingProblems(false);
    }
  }, [selectedDifficulty, selectedCategory, searchQuery]);

  // Fetch quizzes
  const fetchQuizzes = useCallback(async () => {
    try {
      const res = await api.get('/interviews/skills/quizzes/');
      setQuizzes(res.quizzes || []);
    } catch (err) {
      console.error('Failed to fetch quizzes:', err);
    }
  }, []);

  // Fetch analytics
  const fetchAnalytics = useCallback(async () => {
    setLoadingAnalytics(true);
    try {
      const res = await api.get('/interviews/skills/analytics/');
      setAnalytics(res.analytics || null);
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
    } finally {
      setLoadingAnalytics(false);
    }
  }, []);

  useEffect(() => {
    fetchProblems();
    fetchQuizzes();
    fetchAnalytics();
  }, [fetchProblems, fetchQuizzes, fetchAnalytics]);

  // Timer effect for workspace
  useEffect(() => {
    let interval = null;
    if (isTimerRunning) {
      interval = setInterval(() => {
        setTimerSeconds((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isTimerRunning]);

  // Open problem in workspace
  const handleOpenProblem = async (slug) => {
    try {
      const res = await api.get(`/interviews/skills/problems/${slug}/`);
      const prob = res.problem;
      setActiveProblem(prob);

      // Set starter code for default language
      const defaultLang = prob.category === 'sql' ? 'sql' : 'python';
      setSelectedLanguage(defaultLang);
      const starter = prob.starter_templates?.[defaultLang] || '# Write your solution here\n';
      setCode(starter);

      setRunResults(null);
      setSubmitResult(null);
      setActiveConsoleTab('testcases');
      setTimerSeconds(0);
      setIsTimerRunning(true);
      setActiveTab('workspace');
      toast.info(`Opened "${prob.title}" in workspace`, 'Challenge Ready');
    } catch (err) {
      toast.error(err?.message || 'Failed to open problem', 'Challenge Load Error');
    }
  };

  // Change language in workspace
  const handleLanguageChange = (lang) => {
    setSelectedLanguage(lang);
    if (activeProblem?.starter_templates?.[lang]) {
      setCode(activeProblem.starter_templates[lang]);
    } else {
      setCode(`// Write solution in ${lang}\n`);
    }
    setRunResults(null);
    setSubmitResult(null);
  };

  // Run Code against sample test cases
  const handleRunCode = async () => {
    if (!activeProblem || running) return;
    setRunning(true);
    setRunResults(null);
    setActiveConsoleTab('output');
    toast.info('Executing code against sample test cases in sandbox...', 'Running Code');
    try {
      const res = await api.post(`/interviews/skills/problems/${activeProblem.slug}/run/`, {
        code,
        language: selectedLanguage,
      });
      setRunResults(res);
      if (res.all_passed) {
        toast.success(`Passed all ${res.passed_count || ''} sample test cases!`, 'Tests Passed');
      } else {
        toast.warning(
          `Sample tests finished: ${res.passed_count || 0}/${res.total_count || 0} passed. Check console for output.`,
          'Sample Tests Incomplete'
        );
      }
    } catch (err) {
      toast.error(err?.message || 'Code execution failed', 'Runtime Error');
      setRunResults({
        success: false,
        all_passed: false,
        results: [{ actual: '', stderr: err?.message || 'Run failed' }],
      });
    } finally {
      setRunning(false);
    }
  };

  // Submit Code against all test cases
  const handleSubmitCode = async () => {
    if (!activeProblem || submitting) return;
    setSubmitting(true);
    setSubmitResult(null);
    setActiveConsoleTab('output');
    toast.info('Evaluating solution against hidden test cases & performance benchmarks...', 'Submitting Code');
    try {
      const res = await api.post(`/interviews/skills/problems/${activeProblem.slug}/submit/`, {
        code,
        language: selectedLanguage,
      });
      setSubmitResult(res);
      fetchAnalytics();
      fetchProblems();
      if (res.is_accepted) {
        setIsTimerRunning(false);
        toast.success(`Accepted! All hidden test cases passed (+${res.points_awarded || 10} pts).`, 'Solution Accepted');
      } else {
        toast.error(`Solution Rejected: ${res.status || 'Failed test cases'}.`, 'Rejected');
      }
    } catch (err) {
      const msg = err?.message || 'Error executing submission';
      toast.error(msg, 'Submission Failed');
      setSubmitResult({
        success: false,
        status: 'Submission Failed',
        error_message: msg,
      });
    } finally {
      setSubmitting(false);
    }
  };

  // Format seconds to mm:ss
  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  // Start Quiz
  const handleStartQuiz = async (slug) => {
    try {
      const res = await api.get(`/interviews/skills/quizzes/${slug}/`);
      setActiveQuiz(res.quiz);
      setQuizAnswers({});
      setQuizReview(null);
      setQuizTimer(0);
      setActiveTab('quizzes');
      toast.info(`Loaded ${res.quiz.title} assessment`, 'Quiz Initialized');
    } catch (err) {
      toast.error(err?.message || 'Failed to load quiz', 'Quiz Load Error');
    }
  };

  // Submit Quiz
  const handleSubmitQuiz = async () => {
    if (!activeQuiz || submittingQuiz) return;
    setSubmittingQuiz(true);
    toast.info('Evaluating assessment answers and calculating score...', 'Grading Quiz');
    try {
      const res = await api.post(`/interviews/skills/quizzes/${activeQuiz.slug}/submit/`, {
        answers: quizAnswers,
        time_taken_seconds: quizTimer,
      });
      setQuizReview(res);
      fetchQuizzes();
      fetchAnalytics();
      if (res.passed) {
        toast.success(`Assessment Passed! Score: ${res.score_percentage}% (${res.score}/${res.total_questions})`, 'Passed');
      } else {
        toast.warning(`Assessment Completed with ${res.score_percentage}%. Review incorrect answers below.`, 'Completed');
      }
    } catch (err) {
      toast.error(err?.message || 'Failed to submit quiz', 'Quiz Submission Error');
    } finally {
      setSubmittingQuiz(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Skill Assessment Top Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-950/60 via-slate-900 to-purple-950/50 border border-indigo-500/20 p-6 md:p-8">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold mb-3">
              <Code2 className="w-3.5 h-3.5" />
              <span>LeetCode & HackerRank Technical Platform</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Coding Challenges & Skill Assessment
            </h2>
            <p className="text-sm md:text-base text-slate-300 mt-2 leading-relaxed">
              Test your algorithmic problem-solving in Python, JavaScript, Java, C++, and SQL with an integrated online code editor, live test case execution, and technical diagnostic tests.
            </p>
          </div>

          {/* Quick Metrics Badges */}
          {analytics && (
            <div className="flex items-center gap-3 shrink-0">
              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-indigo-500/30 text-center min-w-[90px]">
                <div className="flex items-center justify-center gap-1 text-indigo-400 mb-0.5">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span className="text-[10px] font-bold uppercase">Solved</span>
                </div>
                <div className="text-xl font-extrabold text-white">
                  {analytics.total_solved} <span className="text-xs text-slate-400 font-normal">/ {analytics.total_problems}</span>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-amber-500/30 text-center min-w-[90px]">
                <div className="flex items-center justify-center gap-1 text-amber-400 mb-0.5">
                  <Flame className="w-3.5 h-3.5" />
                  <span className="text-[10px] font-bold uppercase">Streak</span>
                </div>
                <div className="text-xl font-extrabold text-white">{analytics.streak_days}d</div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-emerald-500/30 text-center min-w-[90px]">
                <div className="flex items-center justify-center gap-1 text-emerald-400 mb-0.5">
                  <Award className="w-3.5 h-3.5" />
                  <span className="text-[10px] font-bold uppercase">Accuracy</span>
                </div>
                <div className="text-xl font-extrabold text-white">{analytics.accuracy_pct}%</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Section Sub-Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab('challenges')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'challenges'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          <Code2 className="w-4 h-4" />
          <span>Coding Problems</span>
        </button>

        {activeProblem && (
          <button
            onClick={() => setActiveTab('workspace')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 whitespace-nowrap ${
              activeTab === 'workspace'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Terminal className="w-4 h-4" />
            <span>IDE Workspace ({activeProblem.title})</span>
          </button>
        )}

        <button
          onClick={() => setActiveTab('quizzes')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'quizzes'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          <BookOpen className="w-4 h-4" />
          <span>Technical MCQs & Assessments</span>
        </button>

        <button
          onClick={() => setActiveTab('analytics')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'analytics'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          <BarChart2 className="w-4 h-4" />
          <span>Performance Analytics</span>
        </button>
      </div>

      {/* ==================================================================== */}
      {/* TAB 1: CODING PROBLEMS CATALOG */}
      {/* ==================================================================== */}
      {activeTab === 'challenges' && (
        <div className="space-y-5">
          {/* Filters Bar */}
          <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
              <input
                type="text"
                placeholder="Search coding problems or topics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500 placeholder-slate-500"
              />
            </div>

            {/* Category Filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
            >
              {CATEGORIES.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.label}
                </option>
              ))}
            </select>

            {/* Difficulty Filter */}
            <div className="flex items-center gap-1 bg-slate-800/80 p-1 rounded-xl border border-slate-700">
              {DIFFICULTIES.map((d) => (
                <button
                  key={d}
                  onClick={() => setSelectedDifficulty(d)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold capitalize transition-all ${
                    selectedDifficulty === d
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {/* Problems Table */}
          {loadingProblems ? (
            <div className="p-12 text-center text-slate-400">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-400" />
              <span className="text-xs">Loading coding problems...</span>
            </div>
          ) : (
            <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-800/70 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Title</th>
                    <th className="py-3 px-4">Category</th>
                    <th className="py-3 px-4">Difficulty</th>
                    <th className="py-3 px-4">Acceptance</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {problems.map((prob) => {
                    const isSolved = prob.user_status === 'Solved';
                    const isAttempted = prob.user_status === 'Attempted';
                    return (
                      <tr key={prob.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-3 px-4">
                          {isSolved ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          ) : isAttempted ? (
                            <Clock className="w-4 h-4 text-amber-400" />
                          ) : (
                            <div className="w-3 h-3 rounded-full border border-slate-600" />
                          )}
                        </td>
                        <td className="py-3 px-4 font-bold text-white hover:text-indigo-300 cursor-pointer" onClick={() => handleOpenProblem(prob.slug)}>
                          {prob.title}
                        </td>
                        <td className="py-3 px-4 text-slate-400 capitalize">
                          {prob.category?.replace('_', ' ')}
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                              prob.difficulty === 'easy'
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                : prob.difficulty === 'medium'
                                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                                : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            }`}
                          >
                            {prob.difficulty}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-slate-400">{prob.acceptance_rate}%</td>
                        <td className="py-3 px-4 text-right">
                          <button
                            onClick={() => handleOpenProblem(prob.slug)}
                            className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition-colors shadow-sm"
                          >
                            Solve
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB 2: ONLINE CODE EDITOR WORKSPACE */}
      {/* ==================================================================== */}
      {activeTab === 'workspace' && activeProblem && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 h-[80vh]">
          {/* Left Problem Description Pane (5 cols) */}
          <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                    activeProblem.difficulty === 'easy'
                      ? 'bg-emerald-500/10 text-emerald-400'
                      : activeProblem.difficulty === 'medium'
                      ? 'bg-amber-500/10 text-amber-400'
                      : 'bg-rose-500/10 text-rose-400'
                  }`}
                >
                  {activeProblem.difficulty}
                </span>
                <h3 className="text-sm font-bold text-white truncate max-w-[200px]">
                  {activeProblem.title}
                </h3>
                <button
                  onClick={() => speakText(`${activeProblem.title}. ${activeProblem.description}`, `prob-${activeProblem.id}`)}
                  className="p-1 rounded text-slate-400 hover:text-indigo-400 transition-colors"
                  title={playingAudioKey === `prob-${activeProblem.id}` ? 'Stop audio' : 'Listen to problem description'}
                >
                  {playingAudioKey === `prob-${activeProblem.id}` ? (
                    <VolumeX className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
                  ) : (
                    <Volume2 className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
              <div className="text-xs text-slate-400 font-mono flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-indigo-400" />
                <span>{formatTime(timerSeconds)}</span>
              </div>
            </div>

            <div className="flex-1 p-5 overflow-y-auto space-y-4 text-xs leading-relaxed text-slate-300">
              <div className="whitespace-pre-line font-sans">{activeProblem.description}</div>

              {activeProblem.input_format && (
                <div>
                  <h4 className="font-bold text-white text-xs mb-1">Input Format:</h4>
                  <pre className="p-2.5 rounded-lg bg-slate-950 text-slate-300 font-mono text-[11px] border border-slate-800">
                    {activeProblem.input_format}
                  </pre>
                </div>
              )}

              {activeProblem.output_format && (
                <div>
                  <h4 className="font-bold text-white text-xs mb-1">Output Format:</h4>
                  <pre className="p-2.5 rounded-lg bg-slate-950 text-slate-300 font-mono text-[11px] border border-slate-800">
                    {activeProblem.output_format}
                  </pre>
                </div>
              )}

              {activeProblem.constraints && (
                <div>
                  <h4 className="font-bold text-white text-xs mb-1">Constraints:</h4>
                  <pre className="p-2.5 rounded-lg bg-slate-950 text-slate-400 font-mono text-[11px] border border-slate-800">
                    {activeProblem.constraints}
                  </pre>
                </div>
              )}

              {/* Sample Test Cases */}
              {activeProblem.sample_test_cases?.length > 0 && (
                <div>
                  <h4 className="font-bold text-white text-xs mb-2">Example Cases:</h4>
                  <div className="space-y-2">
                    {activeProblem.sample_test_cases.map((tc, idx) => (
                      <div key={idx} className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 font-mono text-[11px]">
                        <div className="text-slate-400 font-sans font-bold text-[10px] uppercase mb-1">
                          Example #{idx + 1}
                        </div>
                        {tc.input_data && <div><span className="text-slate-500">Input:</span> {tc.input_data}</div>}
                        <div><span className="text-slate-500">Expected:</span> {tc.expected_output}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Editor & Console Pane (7 cols) */}
          <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col overflow-hidden">
            {/* Top Toolbar */}
            <div className="p-3 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
              <div className="flex items-center gap-2">
                <select
                  value={selectedLanguage}
                  onChange={(e) => handleLanguageChange(e.target.value)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs font-semibold focus:outline-none focus:border-indigo-500"
                >
                  {LANGUAGES.map((l) => (
                    <option key={l.id} value={l.id}>
                      {l.label}
                    </option>
                  ))}
                </select>

                <button
                  onClick={() => {
                    if (activeProblem?.starter_templates?.[selectedLanguage]) {
                      setCode(activeProblem.starter_templates[selectedLanguage]);
                      toast.info(`Reset to default ${selectedLanguage} template`, 'Code Template Reset');
                    }
                  }}
                  className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                  title="Reset Code Template"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>

                <button
                  onClick={() => {
                    navigator.clipboard.writeText(code);
                    setCopied(true);
                    toast.success('Code copied to clipboard!', 'Copied');
                    setTimeout(() => setCopied(false), 2000);
                  }}
                  className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                  title="Copy Code"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleRunCode}
                  disabled={running || submitting}
                  className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white font-semibold text-xs flex items-center gap-1.5 transition-colors disabled:opacity-50"
                >
                  {running ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5 text-emerald-400" />}
                  <span>Run Code</span>
                </button>

                <button
                  onClick={handleSubmitCode}
                  disabled={running || submitting}
                  className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-md shadow-emerald-600/20 disabled:opacity-50"
                >
                  {submitting ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                  <span>Submit Code</span>
                </button>
              </div>
            </div>

            {/* Code Editor Area */}
            <div className="flex-1 bg-slate-950 p-2 overflow-hidden flex flex-col font-mono text-xs">
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                spellCheck={false}
                className="w-full flex-1 bg-transparent text-emerald-300 font-mono text-xs leading-relaxed resize-none focus:outline-none p-3 select-text"
                placeholder="// Write your code here..."
              />
            </div>

            {/* Bottom Console / Output Drawer */}
            <div className="h-44 border-t border-slate-800 bg-slate-900/95 flex flex-col">
              {/* Console Tabs */}
              <div className="flex items-center gap-4 px-4 py-2 border-b border-slate-800 text-xs">
                <button
                  onClick={() => setActiveConsoleTab('output')}
                  className={`font-semibold pb-0.5 border-b-2 transition-all ${
                    activeConsoleTab === 'output' ? 'border-indigo-500 text-white' : 'border-transparent text-slate-400'
                  }`}
                >
                  Execution Results
                </button>
                <button
                  onClick={() => setActiveConsoleTab('testcases')}
                  className={`font-semibold pb-0.5 border-b-2 transition-all ${
                    activeConsoleTab === 'testcases' ? 'border-indigo-500 text-white' : 'border-transparent text-slate-400'
                  }`}
                >
                  Sample Test Cases
                </button>
                <button
                  onClick={() => setActiveConsoleTab('solution')}
                  className={`font-semibold pb-0.5 border-b-2 transition-all flex items-center gap-1 ${
                    activeConsoleTab === 'solution' ? 'border-indigo-500 text-white' : 'border-transparent text-slate-400'
                  }`}
                >
                  <Lightbulb className="w-3 h-3 text-amber-400" />
                  <span>Solutions & Explanation</span>
                </button>
              </div>

              {/* Console Body */}
              <div className="flex-1 p-3 overflow-y-auto font-mono text-xs text-slate-300">
                {activeConsoleTab === 'output' && (
                  <div>
                    {running || submitting ? (
                      <div className="flex items-center gap-2 text-slate-400">
                        <RefreshCw className="w-3.5 h-3.5 animate-spin text-indigo-400" />
                        <span>Running code in sandbox...</span>
                      </div>
                    ) : submitResult ? (
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                              submitResult.is_accepted ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                            }`}
                          >
                            {submitResult.status}
                          </span>
                          <span className="text-[11px] text-slate-400">
                            Passed {submitResult.passed_test_cases} / {submitResult.total_test_cases} test cases
                          </span>
                        </div>
                        {submitResult.error_message && (
                          <div className="text-rose-400 text-[11px]">{submitResult.error_message}</div>
                        )}
                      </div>
                    ) : runResults ? (
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                              runResults.all_passed ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                            }`}
                          >
                            {runResults.all_passed ? 'Accepted' : 'Wrong Answer / Error'}
                          </span>
                          <span className="text-[11px] text-slate-400">
                            Average Runtime: {runResults.average_runtime_ms || 1}ms
                          </span>
                        </div>
                        {runResults.results?.map((res, i) => (
                          <div key={i} className="p-2 rounded bg-slate-950 border border-slate-800 text-[11px] space-y-1">
                            <div><span className="text-slate-500">Output:</span> {res.actual || res.stderr || 'No stdout'}</div>
                            {res.expected && <div><span className="text-slate-500">Expected:</span> {res.expected}</div>}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-slate-500 italic">Click 'Run Code' or 'Submit Code' to test your solution.</div>
                    )}
                  </div>
                )}

                {activeConsoleTab === 'testcases' && (
                  <div className="space-y-2">
                    {activeProblem.sample_test_cases?.map((tc, i) => (
                      <div key={i} className="p-2 rounded bg-slate-950 border border-slate-800 text-[11px]">
                        <div><span className="text-slate-500">Input:</span> {tc.input_data || 'None'}</div>
                        <div><span className="text-slate-500">Expected:</span> {tc.expected_output}</div>
                      </div>
                    ))}
                  </div>
                )}

                {activeConsoleTab === 'solution' && (
                  <div className="font-sans space-y-3 text-xs leading-relaxed text-slate-300">
                    {activeProblem.solution_explanation ? (
                      <div className="whitespace-pre-line">{activeProblem.solution_explanation}</div>
                    ) : (
                      <div className="text-slate-500 italic">Submit an accepted solution to unlock full walkthrough.</div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB 3: TECHNICAL ASSESSMENTS & MCQS */}
      {/* ==================================================================== */}
      {activeTab === 'quizzes' && (
        <div className="space-y-6">
          {activeQuiz ? (
            /* Active Quiz Runner */
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div>
                  <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                    {activeQuiz.category?.toUpperCase()} Assessment
                  </span>
                  <h3 className="text-lg font-bold text-white">{activeQuiz.title}</h3>
                </div>
                <button
                  onClick={() => setActiveQuiz(null)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 text-xs font-semibold text-slate-300 hover:text-white"
                >
                  Exit Test
                </button>
              </div>

              {/* Questions List */}
              <div className="space-y-6">
                {activeQuiz.questions_data?.map((q, qIndex) => {
                  const qId = String(q.id);
                  const selectedOpt = quizAnswers[qId];

                  return (
                    <div key={q.id} className="p-5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
                      <div className="flex items-start justify-between gap-3">
                        <div className="font-semibold text-sm text-white">
                          <span className="text-indigo-400 mr-2">Q{qIndex + 1}.</span>
                          {q.question}
                        </div>
                        <button
                          type="button"
                          onClick={() => speakText(q.question, `quiz-q-${q.id}`)}
                          className="p-1 rounded text-slate-400 hover:text-indigo-400 transition-colors shrink-0"
                          title={playingAudioKey === `quiz-q-${q.id}` ? 'Stop audio' : 'Listen to question'}
                        >
                          {playingAudioKey === `quiz-q-${q.id}` ? (
                            <VolumeX className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
                          ) : (
                            <Volume2 className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 pt-2">
                        {q.options?.map((opt, optIndex) => {
                          const isSelected = selectedOpt === optIndex;
                          return (
                            <button
                              key={optIndex}
                              type="button"
                              onClick={() => setQuizAnswers((prev) => ({ ...prev, [qId]: optIndex }))}
                              className={`p-3 rounded-xl border text-left text-xs transition-all ${
                                isSelected
                                  ? 'bg-indigo-600/20 border-indigo-500 text-white font-semibold'
                                  : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700'
                              }`}
                            >
                              <span className="text-slate-500 font-bold mr-2">
                                {String.fromCharCode(65 + optIndex)}.
                              </span>
                              {opt}
                            </button>
                          );
                        })}
                      </div>

                      {/* If review is present, show explanation */}
                      {quizReview && (
                        <div className="mt-3 p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300">
                          <span className="font-bold text-indigo-400">Explanation:</span> {q.explanation}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Submit CTA */}
              <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
                <div>
                  {quizReview && (
                    <span className="text-sm font-bold text-emerald-400">
                      Score: {quizReview.score}% ({quizReview.total_correct}/{quizReview.total_questions} Correct)
                    </span>
                  )}
                </div>

                <button
                  onClick={handleSubmitQuiz}
                  disabled={submittingQuiz}
                  className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md shadow-indigo-600/20 disabled:opacity-50"
                >
                  {submittingQuiz ? 'Evaluating...' : 'Submit Assessment'}
                </button>
              </div>
            </div>
          ) : (
            /* Quizzes Catalog Cards */
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {quizzes.map((quiz) => (
                <div
                  key={quiz.id}
                  className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-indigo-500/40 transition-all flex flex-col justify-between"
                >
                  <div>
                    <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider block mb-1">
                      {quiz.category}
                    </span>
                    <h4 className="text-base font-bold text-white">{quiz.title}</h4>
                    <p className="text-xs text-slate-400 mt-2 line-clamp-3 leading-relaxed">
                      {quiz.description}
                    </p>
                    <div className="mt-4 flex items-center gap-3 text-xs text-slate-400">
                      <span>{quiz.total_questions} Questions</span>
                      <span>•</span>
                      <span>{quiz.time_limit_minutes} Mins</span>
                    </div>
                  </div>

                  <div className="mt-5 pt-3 border-t border-slate-800 flex items-center justify-between">
                    <span className="text-xs text-slate-500">
                      High Score: {quiz.user_highest_score !== null ? `${quiz.user_highest_score}%` : 'Not attempted'}
                    </span>
                    <button
                      onClick={() => handleStartQuiz(quiz.slug)}
                      className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-colors"
                    >
                      Start Test
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB 4: PERFORMANCE ANALYTICS */}
      {/* ==================================================================== */}
      {activeTab === 'analytics' && analytics && (
        <div className="space-y-6">
          {/* Key Metric Gauges */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800">
              <span className="text-xs text-slate-400 font-semibold block uppercase">Total Solved</span>
              <div className="text-3xl font-black text-white mt-2">
                {analytics.total_solved} <span className="text-xs text-slate-400 font-normal">/ {analytics.total_problems}</span>
              </div>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800">
              <span className="text-xs text-slate-400 font-semibold block uppercase">Accuracy</span>
              <div className="text-3xl font-black text-emerald-400 mt-2">{analytics.accuracy_pct}%</div>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800">
              <span className="text-xs text-slate-400 font-semibold block uppercase">Active Streak</span>
              <div className="text-3xl font-black text-amber-400 mt-2">{analytics.streak_days} Days</div>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800">
              <span className="text-xs text-slate-400 font-semibold block uppercase">Avg Solving Runtime</span>
              <div className="text-3xl font-black text-blue-400 mt-2">{analytics.average_runtime_ms} ms</div>
            </div>
          </div>

          {/* Difficulty Breakdown */}
          <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-4">
            <h4 className="text-sm font-bold text-white">Difficulty Breakdown</h4>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span className="text-emerald-400">Easy</span>
                  <span className="text-slate-300">
                    {analytics.difficulty_breakdown?.easy?.solved} / {analytics.difficulty_breakdown?.easy?.total}
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-emerald-500 rounded-full"
                    style={{
                      width: `${(analytics.difficulty_breakdown?.easy?.solved / Math.max(1, analytics.difficulty_breakdown?.easy?.total)) * 100}%`,
                    }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span className="text-amber-400">Medium</span>
                  <span className="text-slate-300">
                    {analytics.difficulty_breakdown?.medium?.solved} / {analytics.difficulty_breakdown?.medium?.total}
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-amber-500 rounded-full"
                    style={{
                      width: `${(analytics.difficulty_breakdown?.medium?.solved / Math.max(1, analytics.difficulty_breakdown?.medium?.total)) * 100}%`,
                    }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span className="text-rose-400">Hard</span>
                  <span className="text-slate-300">
                    {analytics.difficulty_breakdown?.hard?.solved} / {analytics.difficulty_breakdown?.hard?.total}
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-rose-500 rounded-full"
                    style={{
                      width: `${(analytics.difficulty_breakdown?.hard?.solved / Math.max(1, analytics.difficulty_breakdown?.hard?.total)) * 100}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Topic-Wise Performance Grid */}
          <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-4">
            <h4 className="text-sm font-bold text-white">Topic-Wise Performance</h4>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {analytics.topic_performance?.map((t) => (
                <div key={t.category} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
                  <span className="text-xs font-semibold text-slate-300 block truncate">{t.label}</span>
                  <div className="text-base font-extrabold text-white mt-1">{t.mastery_pct}%</div>
                  <span className="text-[10px] text-slate-500">{t.solved} / {t.total} solved</span>
                </div>
              ))}
            </div>
          </div>

          {/* Weak Topics */}
          {analytics.weak_topics?.length > 0 && (
            <div className="p-5 rounded-xl bg-amber-500/10 border border-amber-500/30 space-y-2">
              <h4 className="text-xs font-bold text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4" />
                <span>Identified Weak Areas & Recommended Focus</span>
              </h4>
              <div className="space-y-1.5 text-xs text-amber-200">
                {analytics.weak_topics.map((w, idx) => (
                  <div key={idx}>• {w.recommendation}</div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
