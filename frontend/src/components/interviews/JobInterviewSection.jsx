import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bot,
  Play,
  Layers,
  Building2,
  ChevronRight,
  Clock,
  Award,
  Plus,
  Mic,
  MessageSquare,
  AlertCircle,
  X,
  RefreshCw,
} from 'lucide-react';
import { api } from '../../api/client';
import { AI_AGENTS } from '../../constants/aiAgents';
import { useToast } from '../../context/ToastContext';

const TARGET_ROLES = [
  'Full Stack Developer',
  'Frontend Developer',
  'Backend Developer',
  'Python Developer',
  'Data Scientist',
  'AI/ML Engineer',
  'DevOps Engineer',
  'Mobile Developer (React Native / Flutter)',
  'System Architect',
  'Cloud Engineer (AWS / GCP)',
];

const EXPERIENCE_LEVELS = [
  { id: 'fresher', label: 'Fresher', desc: '0 - 1 years (Entry Level)' },
  { id: 'intermediate', label: 'Intermediate', desc: '2 - 5 years (Mid-Level)' },
  { id: 'experienced', label: 'Experienced', desc: '5+ years (Senior / Staff)' },
];

const INTERVIEW_CATEGORIES = [
  {
    id: 'technical',
    title: 'Technical Interview',
    desc: 'Deep-dive into architecture, algorithms, databases, API design, and language internals.',
    badge: 'Core Tech',
    gradient: 'from-blue-600/20 to-cyan-600/20 border-cyan-500/30 text-cyan-300',
  },
  {
    id: 'hr',
    title: 'HR Interview',
    desc: 'Behavioral, culture-fit, situational judgment, conflict resolution, and leadership traits.',
    badge: 'Behavioral & STAR',
    gradient: 'from-amber-600/20 to-orange-600/20 border-amber-500/30 text-amber-300',
  },
  {
    id: 'project_based',
    title: 'Project-Based Interview',
    desc: 'Defense of real-world portfolio projects, trade-offs, scalability bottlenecks, and tech stack choices.',
    badge: 'Practical Architecture',
    gradient: 'from-emerald-600/20 to-teal-600/20 border-emerald-500/30 text-emerald-300',
  },
  {
    id: 'company_specific',
    title: 'Company-Specific Interview',
    desc: 'Tailored to FAANG and Tier-1 formats: Google, Amazon Leadership Principles, Microsoft, Meta, etc.',
    badge: 'Company Bar Raiser',
    gradient: 'from-purple-600/20 to-indigo-600/20 border-purple-500/30 text-purple-300',
  },
  {
    id: 'full_mock',
    title: 'Full Mock Interview',
    desc: 'End-to-end comprehensive round combining Technical, Behavioral, and System Architecture.',
    badge: 'Complete Simulation',
    gradient: 'from-rose-600/20 to-pink-600/20 border-rose-500/30 text-rose-300',
  },
];

const TARGET_COMPANIES = [
  'Google',
  'Amazon',
  'Microsoft',
  'Meta',
  'Netflix',
  'Apple',
  'Uber',
  'Stripe',
  'TCS',
  'Infosys',
];

export const JobInterviewSection = ({ interviews = [], onRefresh, userRole = '' }) => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [showModal, setShowModal] = useState(false);
  const [starting, setStarting] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Form State
  const [role, setRole] = useState(userRole || 'Full Stack Developer');
  const [customRole, setCustomRole] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('intermediate');
  const [category, setCategory] = useState('technical');
  const [companyName, setCompanyName] = useState('Google');
  const [interviewMode, setInterviewMode] = useState('voice_text');
  const [questionCount, setQuestionCount] = useState(5);
  const [selectedAgentId, setSelectedAgentId] = useState('alex_architect');
  const [strictness, setStrictness] = useState('balanced');

  const handleStartInterview = async (e) => {
    e.preventDefault();
    setStarting(true);
    setErrorMsg(null);
    toast.info('Initializing AI interview environment...', 'Setting Up Room');
    try {
      const finalRole = role === 'Other' && customRole.trim() ? customRole.trim() : role;
      const res = await api.post('/interviews/', {
        target_role: finalRole,
        role: finalRole,
        experience_level: experienceLevel,
        interview_type: category,
        company_name: category === 'company_specific' ? companyName : '',
        interview_mode: interviewMode,
        num_questions: questionCount,
        agent_persona: selectedAgentId,
        agent_strictness: strictness,
      });

      const interviewId = res.interview?.id;
      if (interviewId) {
        toast.success('Interview room initialized! Connecting now...', 'Interview Ready');
        navigate(`/interviews/${interviewId}`);
      } else {
        throw new Error('Interview ID not returned by server.');
      }
    } catch (err) {
      const msg = err?.message || 'Failed to initialize AI interview room.';
      setErrorMsg(msg);
      toast.error(msg, 'Launch Failed');
    } finally {
      setStarting(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-950/60 via-slate-900 to-indigo-950/50 border border-blue-500/20 p-6 md:p-8">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-semibold mb-3">
              <Bot className="w-3.5 h-3.5" />
              <span>Multi-Turn AI Interview Suite</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Real-World Job Interviews with AI
            </h2>
            <p className="text-sm md:text-base text-slate-300 mt-2 leading-relaxed">
              Experience authentic company hiring loops with realistic AI interviewers.
              Questions are asked one at a time with live speech or text, dynamic follow-up questions, and comprehensive multi-dimensional evaluations.
            </p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="inline-flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-sm shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 transition-all duration-200 shrink-0"
          >
            <Plus className="w-4 h-4" />
            <span>Start New Interview</span>
          </button>
        </div>
      </div>

      {/* Category Cards Showcase */}
      <div>
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Layers className="w-5 h-5 text-blue-400" />
          <span>Interview Categories</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {INTERVIEW_CATEGORIES.map((cat) => (
            <div
              key={cat.id}
              onClick={() => {
                setCategory(cat.id);
                setShowModal(true);
              }}
              className="group cursor-pointer rounded-xl bg-slate-900/70 border border-slate-800 hover:border-blue-500/50 p-5 flex flex-col justify-between transition-all duration-200 hover:-translate-y-1 hover:shadow-xl hover:shadow-blue-950/40"
            >
              <div>
                <span className={`inline-block text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-full border mb-3 ${cat.gradient}`}>
                  {cat.badge}
                </span>
                <h4 className="text-base font-bold text-white group-hover:text-blue-300 transition-colors">
                  {cat.title}
                </h4>
                <p className="text-xs text-slate-400 mt-2 line-clamp-3 leading-relaxed">
                  {cat.desc}
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-semibold text-blue-400 group-hover:text-blue-300">
                <span>Select & Launch</span>
                <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Past Interviews History */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Clock className="w-5 h-5 text-indigo-400" />
            <span>Interview History & Performance Reports</span>
          </h3>
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh</span>
            </button>
          )}
        </div>

        {interviews.length === 0 ? (
          <div className="rounded-2xl bg-slate-900/40 border border-slate-800/80 p-10 text-center">
            <Bot className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h4 className="text-base font-bold text-white">No interview sessions yet</h4>
            <p className="text-xs text-slate-400 max-w-md mx-auto mt-1 mb-5">
              Launch your first AI mock interview to practice answering role-specific questions and receive actionable feedback on your technical accuracy and communication.
            </p>
            <button
              onClick={() => setShowModal(true)}
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-colors"
            >
              Start First Interview
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {interviews.map((item) => {
              const isCompleted = item.status === 'completed';
              const score = item.overall_score;

              return (
                <div
                  key={item.id}
                  className="rounded-xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 p-5 flex flex-col justify-between transition-all"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider">
                        {item.interview_type?.replace('_', ' ')}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          isCompleted
                            ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-300'
                            : 'bg-amber-500/10 border border-amber-500/30 text-amber-300'
                        }`}
                      >
                        {isCompleted ? 'Completed' : 'In Progress'}
                      </span>
                    </div>
                    <h4 className="text-base font-bold text-white truncate">{item.target_role}</h4>
                    {item.company_name && (
                      <p className="text-xs text-indigo-300 mt-0.5 flex items-center gap-1">
                        <Building2 className="w-3 h-3" />
                        <span>Target: {item.company_name}</span>
                      </p>
                    )}
                    <p className="text-xs text-slate-400 mt-1">
                      Level: <span className="text-slate-200 capitalize">{item.experience_level || item.difficulty}</span> •{' '}
                      {item.questions_count || item.num_questions} Questions
                    </p>
                  </div>

                  <div className="mt-5 pt-3 border-t border-slate-800 flex items-center justify-between">
                    <div>
                      {score !== null && score !== undefined && score > 0 ? (
                        <div className="flex items-center gap-1.5">
                          <Award className="w-4 h-4 text-emerald-400" />
                          <span className="text-sm font-extrabold text-white">{score}</span>
                          <span className="text-[10px] text-slate-400">/ 100</span>
                        </div>
                      ) : (
                        <span className="text-xs text-slate-500 italic">No score yet</span>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {isCompleted ? (
                        <button
                          onClick={() => navigate(`/interviews/${item.id}/result`)}
                          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition-colors"
                        >
                          View Report
                        </button>
                      ) : (
                        <button
                          onClick={() => navigate(`/interviews/${item.id}`)}
                          className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white flex items-center gap-1 transition-colors"
                        >
                          <span>Resume</span>
                          <Play className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Start Interview Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 md:p-8 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
              <div>
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <Bot className="w-5 h-5 text-blue-400" />
                  <span>Configure Mock Interview</span>
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  Customize role, experience level, interviewer persona, and format.
                </p>
              </div>
              <button
                onClick={() => setShowModal(false)}
                className="w-8 h-8 rounded-lg bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {errorMsg && (
              <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <form onSubmit={handleStartInterview} className="space-y-5">
              {/* Target Job Role */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Target Job Role *
                </label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-white text-sm focus:outline-none focus:border-blue-500"
                >
                  {TARGET_ROLES.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                  <option value="Other">Other (Custom Role)</option>
                </select>
                {role === 'Other' && (
                  <input
                    type="text"
                    placeholder="Enter custom target role..."
                    value={customRole}
                    onChange={(e) => setCustomRole(e.target.value)}
                    required
                    className="w-full mt-2 px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-blue-500"
                  />
                )}
              </div>

              {/* Experience Level */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Experience Level *
                </label>
                <div className="grid grid-cols-3 gap-2.5">
                  {EXPERIENCE_LEVELS.map((lvl) => (
                    <button
                      key={lvl.id}
                      type="button"
                      onClick={() => setExperienceLevel(lvl.id)}
                      className={`p-3 rounded-xl border text-left transition-all ${
                        experienceLevel === lvl.id
                          ? 'bg-blue-600/15 border-blue-500 text-white shadow-sm'
                          : 'bg-slate-800/60 border-slate-700/80 text-slate-300 hover:border-slate-600'
                      }`}
                    >
                      <div className="text-xs font-bold">{lvl.label}</div>
                      <div className="text-[10px] text-slate-400 mt-0.5 leading-tight">{lvl.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Category */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Interview Category *
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {INTERVIEW_CATEGORIES.map((cat) => (
                    <button
                      key={cat.id}
                      type="button"
                      onClick={() => setCategory(cat.id)}
                      className={`p-3 rounded-xl border text-left transition-all ${
                        category === cat.id
                          ? 'bg-blue-600/15 border-blue-500 text-white shadow-sm'
                          : 'bg-slate-800/60 border-slate-700/80 text-slate-300 hover:border-slate-600'
                      }`}
                    >
                      <div className="text-xs font-bold">{cat.title}</div>
                      <div className="text-[10px] text-slate-400 mt-0.5 line-clamp-1">{cat.badge}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Company selection for Company-Specific */}
              {category === 'company_specific' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Target Company Format *
                  </label>
                  <select
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-white text-sm focus:outline-none focus:border-blue-500"
                  >
                    {TARGET_COMPANIES.map((c) => (
                      <option key={c} value={c}>
                        {c} Interview Loop
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Persona and Question Count */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    AI Interviewer Persona
                  </label>
                  <select
                    value={selectedAgentId}
                    onChange={(e) => setSelectedAgentId(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-white text-xs focus:outline-none focus:border-blue-500"
                  >
                    {AI_AGENTS.map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.name} ({a.company})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Strictness Bar
                  </label>
                  <select
                    value={strictness}
                    onChange={(e) => setStrictness(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-white text-xs focus:outline-none focus:border-blue-500"
                  >
                    <option value="supportive">Supportive & Mentorship</option>
                    <option value="balanced">Standard FAANG Standard</option>
                    <option value="rigorous">Rigorous Bar Raiser</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Question Count
                  </label>
                  <select
                    value={questionCount}
                    onChange={(e) => setQuestionCount(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-white text-xs focus:outline-none focus:border-blue-500"
                  >
                    <option value={3}>3 Questions (Quick Sprint)</option>
                    <option value={5}>5 Questions (Standard FAANG)</option>
                    <option value={8}>8 Questions (In-depth)</option>
                  </select>
                </div>
              </div>

              {/* Mode toggle */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Interview Mode
                </label>
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => setInterviewMode('voice_text')}
                    className={`flex-1 py-2.5 px-3 rounded-xl border flex items-center justify-center gap-2 text-xs font-semibold transition-all ${
                      interviewMode === 'voice_text'
                        ? 'bg-blue-600/20 border-blue-500 text-blue-300'
                        : 'bg-slate-800/50 border-slate-700 text-slate-400'
                    }`}
                  >
                    <Mic className="w-3.5 h-3.5" />
                    <span>Voice & Text (Recommended)</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setInterviewMode('text')}
                    className={`flex-1 py-2.5 px-3 rounded-xl border flex items-center justify-center gap-2 text-xs font-semibold transition-all ${
                      interviewMode === 'text'
                        ? 'bg-blue-600/20 border-blue-500 text-blue-300'
                        : 'bg-slate-800/50 border-slate-700 text-slate-400'
                    }`}
                  >
                    <MessageSquare className="w-3.5 h-3.5" />
                    <span>Text Only</span>
                  </button>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-800 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2.5 rounded-xl text-slate-400 hover:text-white text-xs font-semibold transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={starting}
                  className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs shadow-md shadow-blue-500/20 transition-all flex items-center gap-2 disabled:opacity-50"
                >
                  {starting ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Creating Room...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-3.5 h-3.5" />
                      <span>Launch AI Interview</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
