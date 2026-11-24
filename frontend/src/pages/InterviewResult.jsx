import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Award,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  FileText,
  RotateCcw,
  Sparkles,
  Volume2,
  VolumeX,
} from 'lucide-react';
import { api } from '../api/client';
import { getAgentProfile } from '../constants/aiAgents';
import { speechSpeaker } from '../utils/speechService';

export const InterviewResult = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [expandedQuestion, setExpandedQuestion] = useState('all');

  // Audio speech synthesis state
  const [playingKey, setPlayingKey] = useState(null);

  const stopSpeaking = useCallback(() => {
    speechSpeaker.stop();
    setPlayingKey(null);
  }, []);

  const speakText = (text, key) => {
    if (!text) return;

    if (playingKey === key) {
      stopSpeaking();
      return;
    }

    setPlayingKey(key);
    speechSpeaker.speak(text, {
      id: key,
      onStart: () => setPlayingKey(key),
      onEnd: () => setPlayingKey((curr) => (curr === key ? null : curr)),
      onError: (err) => {
        console.warn('Speech playback notice:', err);
        setPlayingKey((curr) => (curr === key ? null : curr));
      },
    });
  };

  useEffect(() => {
    const fetchResult = async () => {
      if (!id) return;
      setLoading(true);
      setErrorMsg(null);
      try {
        const res = await api.get(`/interviews/${id}/result/`);
        setResult(res.result || res);
      } catch (err) {
        setErrorMsg(err?.message || 'Failed to fetch interview scorecard.');
      } finally {
        setLoading(false);
      }
    };
    fetchResult();
    return () => {
      stopSpeaking();
    };
  }, [id, stopSpeaking]);

  if (loading) {
    return (
      <div className="py-24 text-center text-slate-400 space-y-3">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-500" />
        <p className="text-base font-bold text-white">Synthesizing AI Evaluation Scorecard...</p>
        <p className="text-xs text-slate-400">Aggregating dimensional rubrics, strengths, and recommendations.</p>
      </div>
    );
  }

  if (errorMsg || !result) {
    return (
      <div className="p-8 text-center text-slate-400">
        <p className="text-sm text-rose-400 mb-4">{errorMsg || 'Interview scorecard could not be found.'}</p>
        <button
          onClick={() => navigate('/interviews')}
          className="px-4 py-2 rounded-xl bg-blue-600 text-white font-semibold text-xs"
        >
          Return to Interviews Hub
        </button>
      </div>
    );
  }

  const agent = getAgentProfile(result.agent_persona || 'alex_architect');
  const overallScore = result.overall_score || 0;
  const decision = result.decision || 'Completed';

  const getDecisionBadge = (dec) => {
    if (dec.includes('Strong')) return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
    if (dec.includes('Hire')) return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
    if (dec.includes('Leaning')) return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
    return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
  };

  const assessmentText = result.agent_assessment || `Signed off by ${agent.name} (${agent.title} at ${agent.company})`;

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fadeIn pb-12">
      {/* Top Breadcrumb & Action */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/interviews')}
          className="text-xs font-semibold text-slate-400 hover:text-white flex items-center gap-1.5 transition-colors"
        >
          <span>← Back to Career Preparation Hub</span>
        </button>
        <button
          onClick={() => navigate('/interviews')}
          className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center gap-1.5 shadow-md shadow-blue-500/20 transition-all"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Start New Interview</span>
        </button>
      </div>

      {/* Hero Scorecard Card */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-950/60 via-slate-900 to-indigo-950/50 border border-blue-500/30 p-6 md:p-8 shadow-2xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-extrabold uppercase border ${getDecisionBadge(decision)}`}>
                {decision}
              </span>
              <span className="text-xs text-blue-400 font-semibold uppercase tracking-wider">
                • {result.interview_type?.replace('_', ' ')} Evaluation
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              {result.target_role}
            </h1>
            <div className="flex items-center gap-2 mt-2">
              <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
                {assessmentText}
              </p>
              <button
                onClick={() => speakText(assessmentText, 'assessment')}
                className="p-1 rounded-md text-blue-400 hover:text-blue-300 transition-colors"
                title={playingKey === 'assessment' ? 'Stop audio' : 'Listen to assessment'}
              >
                {playingKey === 'assessment' ? (
                  <VolumeX className="w-4 h-4 text-rose-300 animate-pulse" />
                ) : (
                  <Volume2 className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          <div className="flex flex-col items-center justify-center p-5 rounded-2xl bg-slate-900/90 border border-blue-500/30 min-w-[140px] text-center shrink-0">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Overall Score</span>
            <span className="text-5xl font-black text-white mt-1">{overallScore}</span>
            <span className="text-xs text-blue-400 font-semibold mt-0.5">/ 100</span>
          </div>
        </div>

        {/* 4 Multi-Dimensional Breakdown Tiles */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6 pt-6 border-t border-slate-800">
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
            <span className="text-[10px] text-slate-400 font-bold uppercase block">Technical Accuracy</span>
            <span className="text-xl font-extrabold text-blue-400 mt-1 block">
              {result.scores?.technical_accuracy || result.technical_score || 0}%
            </span>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
            <span className="text-[10px] text-slate-400 font-bold block uppercase">Communication</span>
            <span className="text-xl font-extrabold text-emerald-400 mt-1 block">
              {result.scores?.communication || result.communication_score || 0}%
            </span>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
            <span className="text-[10px] text-slate-400 font-bold block uppercase">Relevance</span>
            <span className="text-xl font-extrabold text-indigo-400 mt-1 block">
              {result.scores?.relevance || result.relevance_score || 0}%
            </span>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
            <span className="text-[10px] text-slate-400 font-bold block uppercase">Confidence</span>
            <span className="text-xl font-extrabold text-amber-400 mt-1 block">
              {result.scores?.confidence || result.confidence_score || 0}%
            </span>
          </div>
        </div>
      </div>

      {/* Strengths & Weaknesses Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Demonstrated Strengths</span>
          </h3>
          <ul className="space-y-2 text-xs text-slate-300">
            {result.strengths?.map((str, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold">•</span>
                <span>{str}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Target Areas for Improvement</span>
          </h3>
          <ul className="space-y-2 text-xs text-slate-300">
            {result.weaknesses?.map((w, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-amber-400 font-bold">•</span>
                <span>{w}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Recommended Next Step Box */}
      {result.recommended_next_step && (
        <div className="p-5 rounded-2xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Sparkles className="w-5 h-5 text-blue-400 shrink-0" />
            <div>
              <span className="text-[10px] font-bold text-blue-300 uppercase tracking-wider">
                Actionable Recommendation
              </span>
              <p className="text-xs text-white font-medium mt-0.5">{result.recommended_next_step}</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/interviews?tab=skill_assessment')}
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs whitespace-nowrap"
          >
            Practice Coding
          </button>
        </div>
      )}

      {/* Question-By-Question Detailed Breakdown with Speaker Buttons */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            <span>Question-by-Question Evaluation ({result.answers?.length || 0})</span>
          </h3>
          <button
            onClick={() => setExpandedQuestion(expandedQuestion === 'all' ? null : 'all')}
            className="text-xs text-blue-400 hover:text-blue-300 font-semibold transition-colors"
          >
            {expandedQuestion === 'all' ? 'Collapse All' : 'Expand All'}
          </button>
        </div>

        <div className="space-y-3">
          {result.answers?.map((item, idx) => {
            const isExpanded = expandedQuestion === 'all' || expandedQuestion === idx;
            const qText = item.question || item.question_text || '';
            const qKey = `q-${idx}`;
            const feedbackKey = `feedback-${idx}`;

            return (
              <div
                key={idx}
                className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden transition-all"
              >
                <div
                  onClick={() => {
                    if (expandedQuestion === 'all') {
                      setExpandedQuestion(idx);
                    } else {
                      setExpandedQuestion(expandedQuestion === idx ? null : idx);
                    }
                  }}
                  className="p-4 flex items-center justify-between cursor-pointer hover:bg-slate-800/40"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-lg bg-slate-800 text-blue-400 font-bold text-xs flex items-center justify-center">
                      Q{item.order}
                    </span>
                    <h4 className="text-sm font-bold text-white truncate max-w-xl">
                      {qText}
                    </h4>
                  </div>

                  <div className="flex items-center gap-4">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        speakText(qText, qKey);
                      }}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-blue-400 transition-colors"
                      title={playingKey === qKey ? 'Stop audio' : 'Listen to question'}
                    >
                      {playingKey === qKey ? (
                        <VolumeX className="w-3.5 h-3.5 text-rose-300 animate-pulse" />
                      ) : (
                        <Volume2 className="w-3.5 h-3.5" />
                      )}
                    </button>

                    <div className="flex items-center gap-1.5">
                      <Award className="w-4 h-4 text-emerald-400" />
                      <span className="text-sm font-extrabold text-white">{item.score}</span>
                      <span className="text-[10px] text-slate-400">/ 100</span>
                    </div>
                    {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                  </div>
                </div>

                {isExpanded && (
                  <div className="p-5 border-t border-slate-800 bg-slate-950/50 space-y-4 text-xs">
                    <div>
                      <span className="text-slate-400 font-semibold block mb-1">Your Submitted Answer:</span>
                      <p className="p-3 rounded-lg bg-slate-900 text-slate-200 whitespace-pre-wrap leading-relaxed border border-slate-800">
                        {item.answer || item.answer_text}
                      </p>
                    </div>

                    {item.feedback && (
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-blue-400 font-semibold">Interviewer Feedback:</span>
                          <button
                            onClick={() => speakText(item.feedback, feedbackKey)}
                            className="p-1 text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1"
                            title={playingKey === feedbackKey ? 'Stop feedback audio' : 'Listen to feedback'}
                          >
                            {playingKey === feedbackKey ? (
                              <VolumeX className="w-3.5 h-3.5 text-rose-300 animate-pulse" />
                            ) : (
                              <Volume2 className="w-3.5 h-3.5" />
                            )}
                            <span className="text-[10px]">{playingKey === feedbackKey ? 'Stop' : 'Listen'}</span>
                          </button>
                        </div>
                        <p className="p-3 rounded-lg bg-blue-500/10 text-blue-200 border border-blue-500/20 leading-relaxed">
                          {item.feedback}
                        </p>
                      </div>
                    )}

                    <div className="grid grid-cols-4 gap-2 pt-1 text-center font-mono text-[11px]">
                      <div className="p-2 rounded bg-slate-900">
                        <span className="text-slate-500 block text-[9px] uppercase font-sans">Accuracy</span>
                        <span className="font-bold text-blue-400">{item.technical_accuracy}%</span>
                      </div>
                      <div className="p-2 rounded bg-slate-900">
                        <span className="text-slate-500 block text-[9px] uppercase font-sans">Communication</span>
                        <span className="font-bold text-emerald-400">{item.communication_score}%</span>
                      </div>
                      <div className="p-2 rounded bg-slate-900">
                        <span className="text-slate-500 block text-[9px] uppercase font-sans">Relevance</span>
                        <span className="font-bold text-indigo-400">{item.relevance_score}%</span>
                      </div>
                      <div className="p-2 rounded bg-slate-900">
                        <span className="text-slate-500 block text-[9px] uppercase font-sans">Confidence</span>
                        <span className="font-bold text-amber-400">{item.confidence_score}%</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
