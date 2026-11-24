import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  FileText,
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Plus,
  Trash2,
  Edit3,
  Save,
  Check,
  Award,
  AlertCircle,
  Copy,
  Briefcase,
  GraduationCap,
  RefreshCw,
  TrendingUp,
} from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

const TARGET_ROLES = [
  'Full Stack Developer',
  'Frontend Developer',
  'Backend Developer',
  'Python Developer',
  'Data Scientist',
  'AI/ML Engineer',
  'Data Analyst',
  'DevOps Engineer',
  'Software Developer',
];

export const Resume = () => {
  const { user } = useAuth();
  const { toast } = useToast();

  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Editable parsed data state
  const [parsedData, setParsedData] = useState({
    full_name: '',
    email: '',
    phone: '',
    target_role: 'Full Stack Developer',
    github: '',
    linkedin: '',
    skills: [],
    education: [],
    experience: [],
    projects: [],
  });

  const [newSkillInput, setNewSkillInput] = useState('');
  const [savingParsed, setSavingParsed] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const fileInputRef = useRef(null);

  const hydrateData = useCallback((snap) => {
    if (!snap) return;
    const parsed = snap.parsed_data || {};
    const contact = parsed.contact || {};
    const profile = snap.profile || {};

    const fullName =
      parsed.full_name ||
      parsed.name ||
      profile.full_name ||
      user?.full_name ||
      user?.name ||
      '';

    const email =
      parsed.email ||
      contact.email ||
      profile.email ||
      user?.email ||
      '';

    const phone =
      parsed.phone ||
      contact.phone ||
      profile.phone ||
      user?.phone ||
      '';

    const targetRole =
      snap.target_role ||
      profile.target_role ||
      user?.target_role ||
      'Full Stack Developer';

    const github =
      parsed.github ||
      contact.github ||
      '';

    const linkedin =
      parsed.linkedin ||
      contact.linkedin ||
      '';

    setParsedData({
      full_name: fullName,
      email: email,
      phone: phone,
      target_role: targetRole,
      github: github,
      linkedin: linkedin,
      skills: parsed.skills || [],
      education: parsed.education || [],
      experience: parsed.experience || [],
      projects: parsed.projects || [],
    });
  }, [user]);

  const fetchResume = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.get('/resume/');
      const snap = res.snapshot || res;
      setSnapshot(snap);
      hydrateData(snap);
    } catch (err) {
      const msg = err?.message || 'Failed to fetch resume snapshot.';
      setErrorMsg(msg);
      toast.error(msg, 'Resume Fetch Notice');
    } finally {
      setLoading(false);
    }
  }, [hydrateData, toast]);

  useEffect(() => {
    fetchResume();
  }, [fetchResume]);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Please upload a PDF document format resume.', 'Unsupported Format');
      return;
    }

    setUploading(true);
    setErrorMsg(null);
    toast.info(`Parsing ${file.name} and extracting structured credentials...`, 'Processing Resume');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post('/resume/upload/', formData);
      const snap = res.snapshot || res;
      setSnapshot(snap);
      hydrateData(snap);
      toast.success(
        `Resume parsed! Extracted ${snap.parsed_data?.skills?.length || 0} skills and computed ATS score: ${snap.ats_score}/100`,
        'Resume Uploaded'
      );
      await fetchResume();
    } catch (err) {
      const msg = err?.message || 'Failed to upload and parse resume.';
      setErrorMsg(msg);
      toast.error(msg, 'Upload Failed');
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyzeATS = async (roleOverride) => {
    setAnalyzing(true);
    setErrorMsg(null);
    const chosenRole = roleOverride || parsedData.target_role || 'Full Stack Developer';
    toast.info(`Evaluating ATS match score and keyword gap for ${chosenRole}...`, 'Analyzing ATS');

    try {
      const res = await api.post('/resume/analyze/', { target_role: chosenRole });
      toast.success(
        `ATS Score recalculated: ${res.ats_score}/100 for ${chosenRole}!`,
        'Analysis Refreshed'
      );
      if (res?.ats_analysis || res?.snapshot) {
        setSnapshot(res.snapshot || res);
      }
      await fetchResume();
    } catch (err) {
      const msg = err?.message || 'Failed to analyze resume ATS compatibility.';
      setErrorMsg(msg);
      toast.error(msg, 'Analysis Error');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSaveParsed = async () => {
    setSavingParsed(true);
    setErrorMsg(null);
    try {
      await api.put('/resume/parsed/', { parsed_data: parsedData });
      await api.patch('/resume/', {
        full_name: parsedData.full_name,
        target_role: parsedData.target_role,
      });
      toast.success('Resume details and contact information saved successfully!', 'Saved');
      await fetchResume();
    } catch (err) {
      const msg = err?.message || 'Failed to save parsed resume data.';
      setErrorMsg(msg);
      toast.error(msg, 'Save Error');
    } finally {
      setSavingParsed(false);
    }
  };

  const handleAddSkill = () => {
    if (!newSkillInput.trim()) return;
    const skillToAdd = newSkillInput.trim();
    if (!parsedData.skills.includes(skillToAdd)) {
      setParsedData((prev) => ({
        ...prev,
        skills: [...prev.skills, skillToAdd],
      }));
      toast.success(`Added "${skillToAdd}" to skills`, 'Skill Added');
    }
    setNewSkillInput('');
  };

  const handleRemoveSkill = (skillToRemove) => {
    setParsedData((prev) => ({
      ...prev,
      skills: prev.skills.filter((s) => s !== skillToRemove),
    }));
  };

  const handleCopyRewrite = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    toast.success('Optimized bullet copied to clipboard!', 'Copied');
    setTimeout(() => setCopiedIndex(null), 2500);
  };

  const atsScore = snapshot?.ats_score || snapshot?.ats_analysis?.ats_score || 75;
  const atsAnalysis = snapshot?.ats_analysis || {};

  // Strictly based on the given resume
  const recommendations = atsAnalysis?.recommendations || [];
  const issues = atsAnalysis?.issues || [];
  const suggestions = atsAnalysis?.suggestions || [];
  const tailoredRewrites = atsAnalysis?.tailored_rewrites || [];
  const matchedSkills = atsAnalysis?.matched_skills || [];
  const missingSkills = atsAnalysis?.missing_skills || [];
  const extraSkills = atsAnalysis?.extra_skills || [];
  const sectionChecks = atsAnalysis?.section_checks || [];
  const fileName = snapshot?.file_name || (snapshot?.file ? String(snapshot.file).split('/').pop() : 'Uploaded_Resume.pdf');

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-black tracking-widest uppercase px-2 py-0.5 rounded-md bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-sm">
              ATS Intelligence
            </span>
            <span className="text-xs text-slate-400 font-semibold">• Real-Time Resume Optimizer</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <FileText className="w-7 h-7 text-blue-400" />
            <span>Resume & ATS Analytics</span>
          </h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Extract candidate credentials, check ATS screening pass-rates, and get personalized recommendations strictly based on your resume.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".pdf"
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 transition shadow-sm disabled:opacity-50"
          >
            <UploadCloud className={`w-4 h-4 text-blue-400 ${uploading ? 'animate-bounce' : ''}`} />
            <span>{uploading ? 'Parsing PDF...' : 'Upload Resume PDF'}</span>
          </button>
          <button
            onClick={() => handleAnalyzeATS()}
            disabled={analyzing}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-blue-500/25 transition disabled:opacity-50"
          >
            <Sparkles className={`w-3.5 h-3.5 ${analyzing ? 'animate-spin' : ''}`} />
            <span>{analyzing ? 'Analyzing...' : 'Refresh ATS Score'}</span>
          </button>
        </div>
      </div>

      {/* Error alert banner if any */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-3 animate-fadeIn">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}

      {loading ? (
        <div className="py-24 text-center text-slate-400 space-y-3">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-500" />
          <p className="text-base font-bold text-white">Loading resume intelligence...</p>
          <p className="text-xs text-slate-400">Extracting candidate data, entities, and ATS metrics.</p>
        </div>
      ) : (
        <>
          {/* Top Analytics Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* ATS Score Card */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-slate-850 border border-slate-700/80 shadow-xl flex flex-col justify-between relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-2xl pointer-events-none" />
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    ATS Match Score
                  </span>
                  <Award className="w-5 h-5 text-blue-400" />
                </div>
                <div className="flex items-baseline gap-3 mt-4">
                  <span
                    className={`text-5xl font-black tracking-tight ${
                      atsScore >= 80
                        ? 'text-emerald-400'
                        : atsScore >= 65
                        ? 'text-amber-400'
                        : 'text-rose-400'
                    }`}
                  >
                    {atsScore}
                  </span>
                  <span className="text-sm font-semibold text-slate-400">/ 100</span>
                </div>
                <div className="mt-3">
                  <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                    <span>Target Role: <strong className="text-white">{parsedData.target_role}</strong></span>
                    <span className="font-semibold text-blue-400">{atsAnalysis?.target_role_alignment || 'Calculated'}</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-2 rounded-full transition-all duration-500 ${
                        atsScore >= 80 ? 'bg-emerald-500' : atsScore >= 65 ? 'bg-amber-500' : 'bg-rose-500'
                      }`}
                      style={{ width: `${atsScore}%` }}
                    />
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
                <span>Active Resume:</span>
                <span className="font-semibold text-white truncate max-w-[160px]" title={fileName}>
                  {fileName}
                </span>
              </div>
            </div>

            {/* Real Section Completeness Checks */}
            <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl flex flex-col justify-between">
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-3">
                  Section Completeness Audit
                </span>
                <div className="space-y-2 text-xs">
                  {sectionChecks.length > 0 ? (
                    sectionChecks.map((item, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-2 rounded-lg bg-slate-800/60 border border-slate-800"
                      >
                        <div className="min-w-0 pr-2">
                          <span className="text-slate-300 font-medium block truncate">{item.label}</span>
                          <span className="text-[10px] text-slate-500 block truncate">{item.detail}</span>
                        </div>
                        {item.status ? (
                          <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                        ) : (
                          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                        )}
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-400 py-2">Upload a resume to audit section completeness.</p>
                  )}
                </div>
              </div>
            </div>

            {/* AI Actionable Recommendations based strictly on the given resume */}
            <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    Tailored Recommendations
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    Live Analysis
                  </span>
                </div>

                <div className="space-y-2.5">
                  {recommendations.length > 0 ? (
                    recommendations.slice(0, 3).map((rec, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-300 flex items-start gap-2.5"
                      >
                        <Sparkles className="w-4 h-4 shrink-0 text-blue-400 mt-0.5" />
                        <span className="leading-relaxed font-medium">{rec}</span>
                      </div>
                    ))
                  ) : issues.length > 0 ? (
                    issues.slice(0, 3).map((iss, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 flex items-start gap-2.5"
                      >
                        <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
                        <span className="leading-relaxed font-medium">{iss}</span>
                      </div>
                    ))
                  ) : (
                    <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 text-center text-xs text-slate-400">
                      Upload your resume PDF to receive personalized ATS recommendations tailored to your experience.
                    </div>
                  )}
                </div>
              </div>

              {suggestions.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-800">
                  <p className="text-[11px] text-slate-400 italic">
                    Tip: {suggestions[0]}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* AI Bullet Point Rewriting Studio (Strictly Based on Given Resume) */}
          {tailoredRewrites.length > 0 && (
            <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/20 to-slate-900 border border-indigo-500/20 shadow-xl space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <div>
                  <h3 className="text-base font-extrabold text-white flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-indigo-400" />
                    <span>AI Bullet Point Rewriting Studio</span>
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    We detected descriptive bullets from your resume that lack quantifiable metrics. Use these optimized versions to pass ATS screening.
                  </p>
                </div>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                  Google X-Y-Z Standard
                </span>
              </div>

              <div className="space-y-4">
                {tailoredRewrites.map((rw, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 flex flex-col md:flex-row md:items-start justify-between gap-4"
                  >
                    <div className="space-y-2 flex-1 min-w-0">
                      <div>
                        <span className="text-[10px] font-bold text-amber-400 uppercase tracking-wider block mb-0.5">
                          Original Bullet from Your Resume:
                        </span>
                        <p className="text-xs text-slate-300 italic bg-amber-500/5 p-2 rounded-lg border border-amber-500/15">
                          "{rw.original}"
                        </p>
                      </div>

                      <div>
                        <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider block mb-0.5">
                          AI-Optimized Metric Version:
                        </span>
                        <p className="text-xs text-white font-semibold bg-emerald-500/10 p-2.5 rounded-lg border border-emerald-500/30">
                          {rw.suggestion}
                        </p>
                      </div>

                      <p className="text-[11px] text-slate-400 flex items-center gap-1.5">
                        <span className="font-semibold text-slate-300">Why this works:</span>
                        <span>{rw.reason}</span>
                      </p>
                    </div>

                    <button
                      onClick={() => handleCopyRewrite(rw.suggestion, idx)}
                      className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white text-xs font-semibold border border-slate-700 flex items-center gap-1.5 shrink-0 transition"
                      title="Copy optimized bullet"
                    >
                      {copiedIndex === idx ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                          <span className="text-emerald-400">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5 text-indigo-400" />
                          <span>Copy Bullet</span>
                        </>
                      )}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Target Role Keyword Alignment Matrix */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Matched Skills */}
            <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Matched Skills for {parsedData.target_role}</span>
                </h4>
                <span className="text-xs font-bold text-emerald-400">
                  {matchedSkills.length} Matched
                </span>
              </div>
              <p className="text-xs text-slate-400">
                These keywords in your resume directly match standard job requirements for your target role.
              </p>
              <div className="flex flex-wrap gap-1.5 pt-2">
                {matchedSkills.length > 0 ? (
                  matchedSkills.map((sk, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-semibold"
                    >
                      <Check className="w-3 h-3 text-emerald-400" />
                      <span>{sk}</span>
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-500 italic">No exact role keyword matches yet.</span>
                )}
              </div>
            </div>

            {/* Missing Skills */}
            <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-rose-400" />
                  <span>Missing High-Demand Keywords</span>
                </h4>
                <span className="text-xs font-bold text-rose-400">
                  {missingSkills.length} Needed
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Adding these technologies to your projects and experience bullets will boost your ATS ranking.
              </p>
              <div className="flex flex-wrap gap-1.5 pt-2">
                {missingSkills.length > 0 ? (
                  missingSkills.map((sk, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs font-semibold"
                    >
                      <Plus className="w-3 h-3 text-rose-400" />
                      <span>{sk}</span>
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-emerald-400 font-semibold">
                    Great job! All core requirements for {parsedData.target_role} are matched.
                  </span>
                )}
              </div>
            </div>

            {/* Additional Complementary Skills */}
            {extraSkills.length > 0 && (
              <div className="md:col-span-2 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-1">
                  Additional Detected Competencies ({extraSkills.length})
                </span>
                <p className="text-[11px] text-slate-400 mb-2">
                  Valuable technical capabilities detected in your resume that complement your {parsedData.target_role} profile.
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {extraSkills.map((sk, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-0.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 text-xs font-medium"
                    >
                      {sk}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Parsed Resume Details & Editable Contact Fields */}
          <div className="p-6 md:p-8 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-base md:text-lg font-bold text-white flex items-center gap-2">
                  <Edit3 className="w-5 h-5 text-blue-400" />
                  <span>Parsed Resume Information & Credentials</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Verify your extracted details. All fields are pre-filled from your resume and can be updated anytime.
                </p>
              </div>

              <button
                onClick={handleSaveParsed}
                disabled={savingParsed}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-md shadow-emerald-500/20 transition disabled:opacity-50 shrink-0"
              >
                <Save className={`w-3.5 h-3.5 ${savingParsed ? 'animate-spin' : ''}`} />
                <span>{savingParsed ? 'Saving Changes...' : 'Save Profile Details'}</span>
              </button>
            </div>

            {/* Primary Details Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Full Name <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. John Doe"
                  value={parsedData.full_name}
                  onChange={(e) => setParsedData({ ...parsedData, full_name: e.target.value })}
                  className="w-full px-3.5 py-2.5 bg-slate-800/80 border border-slate-700 rounded-xl text-xs text-white focus:border-blue-500 focus:outline-none transition"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Email Address <span className="text-rose-400">*</span>
                </label>
                <input
                  type="email"
                  placeholder="e.g. candidate@example.com"
                  value={parsedData.email}
                  onChange={(e) => setParsedData({ ...parsedData, email: e.target.value })}
                  className="w-full px-3.5 py-2.5 bg-slate-800/80 border border-slate-700 rounded-xl text-xs text-white focus:border-blue-500 focus:outline-none transition"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Phone Number <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. +91 9876543210"
                  value={parsedData.phone}
                  onChange={(e) => setParsedData({ ...parsedData, phone: e.target.value })}
                  className="w-full px-3.5 py-2.5 bg-slate-800/80 border border-slate-700 rounded-xl text-xs text-white focus:border-blue-500 focus:outline-none transition"
                />
              </div>
            </div>

            {/* Secondary Role & Profiles Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Target Job Role <span className="text-blue-400">• ATS Benchmark</span>
                </label>
                <select
                  value={parsedData.target_role}
                  onChange={(e) => {
                    const newRole = e.target.value;
                    setParsedData({ ...parsedData, target_role: newRole });
                    handleAnalyzeATS(newRole);
                  }}
                  className="w-full px-3.5 py-2.5 bg-slate-800/80 border border-slate-700 rounded-xl text-xs text-white focus:border-blue-500 focus:outline-none transition"
                >
                  {TARGET_ROLES.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  GitHub Profile URL
                </label>
                <input
                  type="text"
                  placeholder="https://github.com/username"
                  value={parsedData.github}
                  onChange={(e) => setParsedData({ ...parsedData, github: e.target.value })}
                  className="w-full px-3.5 py-2.5 bg-slate-800/80 border border-slate-700 rounded-xl text-xs text-white focus:border-blue-500 focus:outline-none transition"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  LinkedIn Profile URL
                </label>
                <input
                  type="text"
                  placeholder="https://linkedin.com/in/username"
                  value={parsedData.linkedin}
                  onChange={(e) => setParsedData({ ...parsedData, linkedin: e.target.value })}
                  className="w-full px-3.5 py-2.5 bg-slate-800/80 border border-slate-700 rounded-xl text-xs text-white focus:border-blue-500 focus:outline-none transition"
                />
              </div>
            </div>

            {/* Extracted Skills Tag Cloud */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-xs font-semibold text-slate-300">
                  Extracted Technical Skills ({parsedData.skills?.length || 0})
                </label>
                <span className="text-[11px] text-slate-400">
                  Click 'x' to remove or add missing skills below
                </span>
              </div>

              <div className="flex flex-wrap gap-2 mb-3 max-h-48 overflow-y-auto p-3 bg-slate-950/60 rounded-xl border border-slate-800">
                {parsedData.skills?.map((skill, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-800 text-xs font-semibold text-blue-300 border border-slate-700 hover:border-slate-600 transition"
                  >
                    <span>{skill}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveSkill(skill)}
                      className="text-slate-500 hover:text-rose-400 p-0.5 transition"
                      title="Remove skill"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>

              <div className="flex items-center gap-2 max-w-md">
                <input
                  type="text"
                  placeholder="Add skill (e.g. PostgreSQL, Redis, Docker)..."
                  value={newSkillInput}
                  onChange={(e) => setNewSkillInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddSkill())}
                  className="flex-1 px-3.5 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-xs text-white focus:border-blue-500 focus:outline-none"
                />
                <button
                  type="button"
                  onClick={handleAddSkill}
                  className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center gap-1.5 transition"
                  title="Add skill tag"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add</span>
                </button>
              </div>
            </div>

            {/* Extracted Experience & Education Preview */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-slate-800">
              {/* Experience */}
              <div>
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-2">
                  <Briefcase className="w-3.5 h-3.5 text-blue-400" />
                  <span>Extracted Work History & Internships</span>
                </h4>
                <div className="space-y-2 max-h-56 overflow-y-auto p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-300">
                  {parsedData.experience?.length > 0 ? (
                    parsedData.experience.map((exp, idx) => (
                      <div key={idx} className="p-2 rounded-lg bg-slate-800/50 border border-slate-800/80">
                        <p className="leading-relaxed">{exp}</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-slate-500 italic">No experience entries found in uploaded resume.</p>
                  )}
                </div>
              </div>

              {/* Education */}
              <div>
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-2">
                  <GraduationCap className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Extracted Education & Academics</span>
                </h4>
                <div className="space-y-2 max-h-56 overflow-y-auto p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-300">
                  {parsedData.education?.length > 0 ? (
                    parsedData.education.map((edu, idx) => (
                      <div key={idx} className="p-2 rounded-lg bg-slate-800/50 border border-slate-800/80">
                        <p className="leading-relaxed">{edu}</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-slate-500 italic">No education entries found in uploaded resume.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Resume;
