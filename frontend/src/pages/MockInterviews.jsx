import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Bot,
  MessageSquare,
  Code2,
  ArrowRight,
  Flame,
  CheckCircle2,
  Layers,
} from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { JobInterviewSection } from '../components/interviews/JobInterviewSection';
import { CommunicationSection } from '../components/interviews/CommunicationSection';
import { SkillAssessmentSection } from '../components/interviews/SkillAssessmentSection';

export const MockInterviews = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const currentTab = searchParams.get('tab') || 'hub';

  const [hubStats, setHubStats] = useState(null);
  const [interviews, setInterviews] = useState([]);
  const [, setLoading] = useState(true);
  const { user } = useAuth();

  const fetchHubData = async () => {
    setLoading(true);
    try {
      const [hubRes, interviewsRes] = await Promise.all([
        api.get('/interviews/hub/stats/'),
        api.get('/interviews/'),
      ]);
      setHubStats(hubRes.hub || null);
      setInterviews(interviewsRes.interviews || []);
    } catch (err) {
      console.error('Failed to load hub data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHubData();
  }, []);

  const setTab = (tabName) => {
    setSearchParams(tabName === 'hub' ? {} : { tab: tabName });
  };

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      {/* Platform Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-black tracking-widest uppercase px-2 py-0.5 rounded-md bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-sm">
              All-In-One Platform
            </span>
            <span className="text-xs text-slate-400 font-semibold">• AI Career Suite</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Interviews & Career Preparation
          </h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Master real-world technical and HR interviews, improve English communication, and solve algorithmic challenges.
          </p>
        </div>

        {/* Global Tab Switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-2xl bg-slate-900 border border-slate-800 shrink-0 overflow-x-auto">
          <button
            onClick={() => setTab('hub')}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 whitespace-nowrap ${
              currentTab === 'hub'
                ? 'bg-slate-800 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Layers className="w-3.5 h-3.5 text-blue-400" />
            <span>Overview Hub</span>
          </button>

          <button
            onClick={() => setTab('job_interviews')}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 whitespace-nowrap ${
              currentTab === 'job_interviews'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Bot className="w-3.5 h-3.5" />
            <span>Job Interviews</span>
          </button>

          <button
            onClick={() => setTab('communication')}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 whitespace-nowrap ${
              currentTab === 'communication'
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Communication</span>
          </button>

          <button
            onClick={() => setTab('skill_assessment')}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 whitespace-nowrap ${
              currentTab === 'skill_assessment'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>Skill Assessment</span>
          </button>
        </div>
      </div>

      {/* ==================================================================== */}
      {/* TAB 0: OVERVIEW HUB (THE 3 MAIN CARDS) */}
      {/* ==================================================================== */}
      {currentTab === 'hub' && (
        <div className="space-y-8 animate-fadeIn">
          {/* Quick Metrics Bar */}
          {hubStats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">
                  Interviews Finished
                </span>
                <div className="text-2xl font-black text-white mt-1">
                  {hubStats.job_interviews?.total_completed || 0}
                </div>
                <span className="text-[11px] text-blue-400 font-semibold mt-0.5 block">
                  Avg Score: {hubStats.job_interviews?.average_score || 0}%
                </span>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">
                  Communication Drills
                </span>
                <div className="text-2xl font-black text-white mt-1">
                  {hubStats.communication?.total_sessions || 0}
                </div>
                <span className="text-[11px] text-emerald-400 font-semibold mt-0.5 block">
                  Speaking Speed: {hubStats.communication?.average_speed_wpm || 130} WPM
                </span>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">
                  Coding Challenges Solved
                </span>
                <div className="text-2xl font-black text-white mt-1">
                  {hubStats.skill_assessment?.problems_solved || 0}
                </div>
                <span className="text-[11px] text-indigo-400 font-semibold mt-0.5 block">
                  Accuracy: {hubStats.skill_assessment?.accuracy_pct || 0}%
                </span>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">
                  Active Coding Streak
                </span>
                <div className="text-2xl font-black text-amber-400 mt-1 flex items-center gap-1.5">
                  <Flame className="w-5 h-5 fill-amber-400" />
                  <span>{hubStats.skill_assessment?.streak_days || 0} Days</span>
                </div>
                <span className="text-[11px] text-slate-400 block mt-0.5">Keep the streak alive!</span>
              </div>
            </div>
          )}

          {/* THE THREE VISUALLY DISTINCT CARDS */}
          <div>
            <div className="mb-4">
              <h2 className="text-lg font-extrabold text-white">Choose Your Preparation Track</h2>
              <p className="text-xs text-slate-400">
                Select one of the three dedicated modules below to begin your targeted practice.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Card 1: Job Interviews */}
              <div
                onClick={() => setTab('job_interviews')}
                className="group relative cursor-pointer overflow-hidden rounded-2xl bg-gradient-to-b from-blue-950/40 via-slate-900/80 to-slate-900 border border-blue-500/25 hover:border-blue-400/60 p-6 flex flex-col justify-between transition-all duration-300 hover:-translate-y-1.5 hover:shadow-2xl hover:shadow-blue-500/15"
              >
                <div className="absolute top-0 right-0 w-36 h-36 bg-blue-500/10 rounded-full blur-2xl pointer-events-none group-hover:bg-blue-500/20 transition-all" />

                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-blue-400 group-hover:scale-110 transition-transform">
                      <Bot className="w-6 h-6" />
                    </div>
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-blue-500/10 border border-blue-500/30 text-blue-300">
                      AI Interview Loops
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-white group-hover:text-blue-300 transition-colors">
                    Job Interviews
                  </h3>
                  <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                    Practice real-world HR, technical, and company-specific mock interviews with realistic AI interviewers.
                  </p>

                  <div className="mt-5 space-y-2 text-xs text-slate-400 border-t border-slate-800/80 pt-4">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />
                      <span>Role & experience level targeting</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />
                      <span>Speech-to-text & voice-enabled interview room</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />
                      <span>Dynamic follow-up questions & scorecard</span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400">
                    {hubStats?.job_interviews?.total_completed || 0} completed
                  </span>
                  <div className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-400 group-hover:text-blue-300 group-hover:translate-x-1 transition-all">
                    <span>Enter Job Interviews</span>
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </div>
              </div>

              {/* Card 2: Communication */}
              <div
                onClick={() => setTab('communication')}
                className="group relative cursor-pointer overflow-hidden rounded-2xl bg-gradient-to-b from-emerald-950/40 via-slate-900/80 to-slate-900 border border-emerald-500/25 hover:border-emerald-400/60 p-6 flex flex-col justify-between transition-all duration-300 hover:-translate-y-1.5 hover:shadow-2xl hover:shadow-emerald-500/15"
              >
                <div className="absolute top-0 right-0 w-36 h-36 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none group-hover:bg-emerald-500/20 transition-all" />

                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
                      <MessageSquare className="w-6 h-6" />
                    </div>
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                      Voice & Speaking AI
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-white group-hover:text-emerald-300 transition-colors">
                    Communication Practice
                  </h3>
                  <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                    Improve English fluency, pronunciation, grammar, and workplace speaking through live AI conversational drills.
                  </p>

                  <div className="mt-5 space-y-2 text-xs text-slate-400 border-t border-slate-800/80 pt-4">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Daily communication & elevator pitch drills</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Group discussion & public speaking simulation</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Grammar correction & sentence upgrades</span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400">
                    {hubStats?.communication?.total_sessions || 0} sessions
                  </span>
                  <div className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-400 group-hover:text-emerald-300 group-hover:translate-x-1 transition-all">
                    <span>Enter Communication</span>
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </div>
              </div>

              {/* Card 3: Skill Assessment */}
              <div
                onClick={() => setTab('skill_assessment')}
                className="group relative cursor-pointer overflow-hidden rounded-2xl bg-gradient-to-b from-indigo-950/40 via-slate-900/80 to-slate-900 border border-indigo-500/25 hover:border-indigo-400/60 p-6 flex flex-col justify-between transition-all duration-300 hover:-translate-y-1.5 hover:shadow-2xl hover:shadow-indigo-500/15"
              >
                <div className="absolute top-0 right-0 w-36 h-36 bg-indigo-500/10 rounded-full blur-2xl pointer-events-none group-hover:bg-indigo-500/20 transition-all" />

                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-indigo-500/15 border border-indigo-500/30 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
                      <Code2 className="w-6 h-6" />
                    </div>
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-indigo-500/10 border border-indigo-500/30 text-indigo-300">
                      LeetCode & MCQ Engine
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-white group-hover:text-indigo-300 transition-colors">
                    Skill Assessment
                  </h3>
                  <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                    Test your coding, DSA, SQL, and CS knowledge with an online code editor, test case execution, and diagnostics.
                  </p>

                  <div className="mt-5 space-y-2 text-xs text-slate-400 border-t border-slate-800/80 pt-4">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Python, JavaScript, Java, C++, and SQL</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Sample & hidden test case evaluation</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Streaks, analytics & weak-topic discovery</span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400">
                    {hubStats?.skill_assessment?.problems_solved || 0} problems solved
                  </span>
                  <div className="inline-flex items-center gap-1.5 text-xs font-bold text-indigo-400 group-hover:text-indigo-300 group-hover:translate-x-1 transition-all">
                    <span>Enter Skill Assessment</span>
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB 1: JOB INTERVIEWS SECTION */}
      {/* ==================================================================== */}
      {currentTab === 'job_interviews' && (
        <JobInterviewSection
          interviews={interviews}
          onRefresh={fetchHubData}
          userRole={user?.target_role}
        />
      )}

      {/* ==================================================================== */}
      {/* TAB 2: COMMUNICATION SECTION */}
      {/* ==================================================================== */}
      {currentTab === 'communication' && <CommunicationSection />}

      {/* ==================================================================== */}
      {/* TAB 3: SKILL ASSESSMENT SECTION */}
      {/* ==================================================================== */}
      {currentTab === 'skill_assessment' && <SkillAssessmentSection />}
    </div>
  );
};
