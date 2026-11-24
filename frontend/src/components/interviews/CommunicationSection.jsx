import React, { useState, useEffect, useRef } from 'react';
import {
  MessageSquare,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Play,
  Send,
  Sparkles,
  Users,
  Award,
  BookOpen,
  Calendar,
  UserCheck,
  CheckCircle2,
  AlertCircle,
  Clock,
  TrendingUp,
  RefreshCw,
  X,
  Zap,
  Activity,
  Lightbulb,
} from 'lucide-react';
import { api } from '../../api/client';
import { useToast } from '../../context/ToastContext';
import { speechSpeaker, speechRecorder } from '../../utils/speechService';

const MODES = [
  {
    id: 'daily_practice',
    title: 'Daily Communication Drill',
    tagline: '5-minute daily speech drills and spontaneous articulation',
    icon: Calendar,
    color: 'from-blue-500/20 to-indigo-500/20 border-blue-500/30 text-blue-400',
  },
  {
    id: 'conversational',
    title: 'AI Conversational Practice',
    tagline: 'Fluid interactive dialogues with an adaptive AI career coach',
    icon: MessageSquare,
    color: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/30 text-emerald-400',
  },
  {
    id: 'self_intro',
    title: 'Self-Introduction & Pitch',
    tagline: 'Master your 60-second elevator pitch using the STAR framework',
    icon: UserCheck,
    color: 'from-purple-500/20 to-pink-500/20 border-purple-500/30 text-purple-400',
  },
  {
    id: 'group_discussion',
    title: 'Group Discussion (GD) Simulator',
    tagline: 'Multi-agent debate with AI moderator and peer participants',
    icon: Users,
    color: 'from-amber-500/20 to-orange-500/20 border-amber-500/30 text-amber-400',
  },
  {
    id: 'public_speaking',
    title: 'Public Speaking & Extempore',
    tagline: 'Deliver persuasive presentations with pacing and vocal variety',
    icon: Mic,
    color: 'from-rose-500/20 to-red-500/20 border-rose-500/30 text-rose-400',
  },
  {
    id: 'fluency_pronunciation',
    title: 'Fluency & Pronunciation Drills',
    tagline: 'Phonetic articulation, syllable stress, and tongue twisters',
    icon: Sparkles,
    color: 'from-cyan-500/20 to-sky-500/20 border-cyan-500/30 text-cyan-400',
  },
  {
    id: 'vocabulary',
    title: 'Vocabulary & Executive Phrasing',
    tagline: 'Upgrade colloquial speech into high-impact corporate terminology',
    icon: BookOpen,
    color: 'from-indigo-500/20 to-violet-500/20 border-indigo-500/30 text-indigo-400',
  },
  {
    id: 'grammar',
    title: 'Grammar & Error Correction',
    tagline: 'Eliminate tense inconsistencies and non-native grammatical missteps',
    icon: CheckCircle2,
    color: 'from-teal-500/20 to-emerald-500/20 border-teal-500/30 text-teal-400',
  },
  {
    id: 'sentence_formation',
    title: 'Sentence Formation & Connectors',
    tagline: 'Form sophisticated compound sentences with logical transitions',
    icon: TrendingUp,
    color: 'from-sky-500/20 to-blue-500/20 border-sky-500/30 text-sky-400',
  },
  {
    id: 'workplace_scenarios',
    title: 'Workplace Scenarios & Conflict',
    tagline: 'Roleplay salary negotiations, escalations, and executive presentations',
    icon: Zap,
    color: 'from-yellow-500/20 to-amber-500/20 border-yellow-500/30 text-yellow-400',
  },
];

const SAMPLE_DICTATIONS = {
  daily_practice:
    'Recently, I diagnosed a subtle race condition in our distributed cache where stale keys were overwriting active session data. I isolated the issue by attaching distributed trace IDs and resolved it by enforcing atomic Redis transactions.',
  conversational:
    'In our upcoming sprint, I recommend prioritizing our observability infrastructure. Establishing distributed tracing and latency budgets will allow our team to catch performance regressions well before they impact downstream production users.',
  self_intro:
    'Hello, I am a Full Stack Developer specializing in distributed React and Python architectures. Recently, I architected an asynchronous data ingestion pipeline that processed 10 million daily events with sub-50ms latency. I am eager to bring this passion for scalable cloud systems to your engineering team.',
  group_discussion:
    "I agree with Arjun's point on spontaneous collaboration; however, telemetry data indicates that hybrid asynchronous workflows yield a 30% increase in focused deep-work output when supported by clear documentation.",
  public_speaking:
    "Every second of downtime costs our business revenue and customer trust. Migrating our monolithic codebase to isolated microservices isn't just an architectural upgrade—it is our strategic moat for fault isolation, rapid continuous delivery, and five-nines reliability.",
  fluency_pronunciation:
    'She sells synthetic silicon circuits to specific systemic servers, ensuring synchronized data streaming across scalable cloud networks.',
  vocabulary:
    'I spearheaded the performance overhaul, optimizing database indices and reducing p99 API latency by 45% across all production clusters.',
  grammar:
    'We discussed the root cause, and the engineer did not know why the database had crashed.',
  sentence_formation:
    'Our engineering team adopted containerization; consequently, our deployment velocity accelerated substantially while maintaining zero-downtime availability.',
  workplace_scenarios:
    'Thank you for acknowledging my impact on the Q3 microservices delivery. Based on market benchmarks for Staff Engineer responsibilities and the 40% latency reduction my team delivered, I would like to discuss aligning my compensation and title to reflect this level of ownership.',
};

export const CommunicationSection = () => {
  const { toast } = useToast();
  const [sessions, setSessions] = useState([]);
  const [topicsCatalog, setTopicsCatalog] = useState({});
  const [, setLoading] = useState(true);
  const [, setErrorMsg] = useState(null);

  // Active Session State
  const [activeSession, setActiveSession] = useState(null);
  const [exchanges, setExchanges] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [sending, setSending] = useState(false);
  const [finishing, setFinishing] = useState(false);
  const [completedReport, setCompletedReport] = useState(null);

  // Voice recognition and TTS states
  const [isListening, setIsListening] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [speechTimer, setSpeechTimer] = useState(0);
  const [audioVolume, setAudioVolume] = useState(0);
  const [playingId, setPlayingId] = useState(null);

  // Recorded Audio Backup & Playback state
  const [recordedAudioUrl, setRecordedAudioUrl] = useState(null);
  const [recordedAudioBlob, setRecordedAudioBlob] = useState(null);
  const [transcribing, setTranscribing] = useState(false);

  const chatScrollRef = useRef(null);

  // Mode Selection Modal
  const [showStartModal, setShowStartModal] = useState(false);
  const [selectedMode, setSelectedMode] = useState('daily_practice');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [customTopic, setCustomTopic] = useState('');

  // Clean up audio on unmount
  useEffect(() => {
    return () => {
      speechSpeaker.stop();
      speechRecorder.stop();
    };
  }, []);

  // Speak specific text with unique tracking ID using speechSpeaker
  const speakText = (text, id = 'global') => {
    if (!text) return;

    if (playingId === id) {
      speechSpeaker.stop();
      setPlayingId(null);
      return;
    }

    if (isListening) {
      speechRecorder.stop();
      setIsListening(false);
      setAudioVolume(0);
    }

    setPlayingId(id);
    speechSpeaker.speak(text, {
      id,
      onStart: () => setPlayingId(id),
      onEnd: () => setPlayingId((curr) => (curr === id ? null : curr)),
      onError: (err) => {
        console.warn('Speech playback notice:', err);
        setPlayingId((curr) => (curr === id ? null : curr));
      },
    });
  };

  const fetchTopicsAndHistory = async () => {
    setLoading(true);
    try {
      const [topicsRes, sessionsRes] = await Promise.all([
        api.get('/interviews/communication/topics/'),
        api.get('/interviews/communication/'),
      ]);
      setTopicsCatalog(topicsRes.topics_catalog || {});
      setSessions(sessionsRes.sessions || []);
    } catch (err) {
      setErrorMsg(err?.message || 'Failed to fetch communication data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTopicsAndHistory();
  }, []);

  // Auto-scroll chat
  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [exchanges]);

  // Speaking timer
  useEffect(() => {
    let interval = null;
    if (isListening) {
      interval = setInterval(() => {
        setSpeechTimer((prev) => prev + 1);
      }, 1000);
    } else {
      setSpeechTimer(0);
    }
    return () => clearInterval(interval);
  }, [isListening]);

  const handleAutoTranscribeAudio = async (blobToTranscribe = null) => {
    const blob = blobToTranscribe || recordedAudioBlob;
    if (!blob) return;

    setTranscribing(true);
    try {
      const topicContext = activeSession?.topic || '';
      const transcript = await speechRecorder.transcribeAudioBlob(blob, topicContext);
      if (transcript && transcript.trim()) {
        setUserInput((prev) => (prev ? `${prev.trim()} ${transcript.trim()}` : transcript.trim()));
        toast.success('Recorded voice transcribed into response box!', 'Voice Transcribed');
      }
    } catch (err) {
      console.warn('Communication transcription notice:', err);
    } finally {
      setTranscribing(false);
    }
  };

  const handleDictateExampleMessage = () => {
    const mode = activeSession?.mode || selectedMode || 'daily_practice';
    const sample =
      SAMPLE_DICTATIONS[mode] ||
      `I would like to propose a structured approach for ${activeSession?.topic || 'our project roadmap'}. First, we benchmark our current operational metrics. Then, we implement iterative improvements with continuous feedback to keep all stakeholders aligned.`;
    setUserInput(sample);
    toast.info('Example articulation populated for testing.', 'Dictate Helper');
  };

  const handleDirectLaunch = async (modeId) => {
    setSelectedMode(modeId);
    setSending(true);
    setErrorMsg(null);
    try {
      const presets = topicsCatalog[modeId] || [];
      const chosenTopic = presets[0] || '';
      const res = await api.post('/interviews/communication/', {
        mode: modeId,
        topic: chosenTopic,
      });
      const session = res.session;
      setActiveSession(session);
      setExchanges(session.exchanges || []);
      setCompletedReport(null);
      setShowStartModal(false);
      toast.success(`Started ${session.mode?.replace('_', ' ')} session!`, 'Voice Room Ready');

      if (session.exchanges?.[0]?.content && voiceEnabled) {
        speakText(session.exchanges[0].content, session.exchanges[0].id || 'intro');
      }
    } catch (err) {
      const msg = err?.message || 'Failed to start communication session.';
      setErrorMsg(msg);
      toast.error(msg, 'Session Error');
    } finally {
      setSending(false);
    }
  };

  const toggleListening = async () => {
    if (isListening) {
      const finalRecordedText = speechRecorder.stop();
      setIsListening(false);
      setAudioVolume(0);

      if (finalRecordedText && finalRecordedText.trim()) {
        setUserInput(finalRecordedText.trim());
      }
    } else {
      if (playingId) {
        speechSpeaker.stop();
        setPlayingId(null);
      }

      setRecordedAudioUrl(null);
      setRecordedAudioBlob(null);

      const started = await speechRecorder.start({
        initialText: userInput,
        onResult: (fullText) => {
          setUserInput(fullText);
        },
        onVolume: (vol) => {
          setAudioVolume(vol);
        },
        onError: (errMsg) => {
          console.warn('Speech recognition notice:', errMsg);
        },
        onStatusChange: (active) => {
          setIsListening(active);
          if (!active) setAudioVolume(0);
        },
        onAudioReady: ({ audioBlob, audioUrl }) => {
          setRecordedAudioBlob(audioBlob);
          setRecordedAudioUrl(audioUrl);

          // If SpeechRecognition produced no text (e.g. Chrome network STT delay), auto-transcribe audio!
          if (!userInput.trim()) {
            handleAutoTranscribeAudio(audioBlob);
          }
        },
      });

      if (started) {
        setIsListening(true);
      }
    }
  };

  const handleStartSession = async (modeId, topicPreset = '') => {
    setSelectedMode(modeId);
    const presets = topicsCatalog[modeId] || [];
    setSelectedTopic(topicPreset || presets[0] || '');
    setShowStartModal(true);
  };

  const handleLaunchSession = async (e) => {
    e.preventDefault();
    setSending(true);
    setErrorMsg(null);
    try {
      const finalTopic = customTopic.trim() || selectedTopic;
      const res = await api.post('/interviews/communication/', {
        mode: selectedMode,
        topic: finalTopic,
      });
      const session = res.session;
      setActiveSession(session);
      setExchanges(session.exchanges || []);
      setCompletedReport(null);
      setShowStartModal(false);
      toast.success(`Configured ${session.mode?.replace('_', ' ')} practice!`, 'Session Launched');

      if (session.exchanges?.[0]?.content && voiceEnabled) {
        speakText(session.exchanges[0].content, session.exchanges[0].id || 'intro');
      }
    } catch (err) {
      const msg = err?.message || 'Failed to start communication session.';
      setErrorMsg(msg);
      toast.error(msg, 'Session Error');
    } finally {
      setSending(false);
    }
  };

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    const message = userInput.trim();
    if (!message || !activeSession || sending) return;

    if (isListening) {
      speechRecorder.stop();
      setIsListening(false);
      setAudioVolume(0);
    }

    speechSpeaker.stop();
    setPlayingId(null);

    setSending(true);
    setUserInput('');

    try {
      const res = await api.post(`/interviews/communication/${activeSession.id}/message/`, {
        message,
        audio_metrics: { duration_seconds: speechTimer || 10 },
      });

      const userEx = res.user_exchange;
      const aiExs = res.ai_exchanges || [];
      setExchanges((prev) => [...prev, userEx, ...aiExs]);

      if (aiExs.length > 0 && voiceEnabled) {
        const lastMsg = aiExs[aiExs.length - 1];
        speakText(lastMsg.content, lastMsg.id || `ai-${Date.now()}`);
      }
    } catch (err) {
      const msg = err?.message || 'Failed to send message.';
      setErrorMsg(msg);
      toast.error(msg, 'Message Notice');
    } finally {
      setSending(false);
    }
  };

  const handleFinishSession = async () => {
    if (!activeSession || finishing) return;
    setFinishing(true);
    toast.info('Evaluating pronunciation, grammar, and speech cadence...', 'Grading Communication');
    speechSpeaker.stop();
    speechRecorder.stop();
    setPlayingId(null);
    setIsListening(false);

    try {
      const res = await api.post(`/interviews/communication/${activeSession.id}/finish/`);
      setCompletedReport(res.session);
      toast.success('Communication scorecard evaluated!', 'Evaluation Ready');
      fetchTopicsAndHistory();
    } catch (err) {
      const msg = err?.message || 'Failed to finish communication evaluation.';
      setErrorMsg(msg);
      toast.error(msg, 'Grading Error');
    } finally {
      setFinishing(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-emerald-950/60 via-slate-900 to-teal-950/50 border border-emerald-500/20 p-6 md:p-8">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Dedicated English & Speaking Mastery</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              AI Professional Communication Practice
            </h2>
            <p className="text-sm md:text-base text-slate-300 mt-2 leading-relaxed">
              Elevate your English fluency, workplace conversations, group discussions, and executive presence with real-time AI speech evaluation, pronunciation checks, and grammar corrections.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => handleStartSession('daily_practice')}
              className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs shadow-lg shadow-emerald-500/20 transition-all shrink-0"
            >
              <Calendar className="w-4 h-4" />
              <span>Daily Practice Drill</span>
            </button>
          </div>
        </div>
      </div>

      {/* Active Interactive Practice Room Modal */}
      {activeSession && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-3 md:p-6 bg-slate-950/85 backdrop-blur-md animate-fadeIn">
          <div className="w-full max-w-4xl h-[90vh] bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
            {/* Room Header */}
            <div className="p-4 md:p-5 border-b border-slate-800 bg-slate-900/90 flex items-center justify-between shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
                      {activeSession.mode?.replace('_', ' ')}
                    </span>
                    <span className="text-[10px] font-semibold text-slate-400">• Live Session</span>
                  </div>
                  <h3 className="text-base font-bold text-white truncate max-w-md">{activeSession.topic}</h3>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    const nextVal = !voiceEnabled;
                    setVoiceEnabled(nextVal);
                    if (!nextVal && playingId) {
                      speechSpeaker.stop();
                      setPlayingId(null);
                    }
                  }}
                  className={`p-2 rounded-lg border text-xs flex items-center gap-1.5 transition-colors ${
                    voiceEnabled
                      ? 'bg-slate-800 border-slate-700 text-emerald-400'
                      : 'bg-slate-800 border-slate-700 text-slate-500'
                  }`}
                  title={voiceEnabled ? 'Auto-voice enabled (Click to mute)' : 'Auto-voice disabled (Click to unmute)'}
                >
                  {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                </button>

                <button
                  onClick={handleFinishSession}
                  disabled={finishing}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-1.5 transition-colors shadow-md disabled:opacity-50"
                >
                  {finishing ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Grading...</span>
                    </>
                  ) : (
                    <>
                      <Award className="w-3.5 h-3.5" />
                      <span>Finish & Evaluate</span>
                    </>
                  )}
                </button>

                <button
                  onClick={() => {
                    speechSpeaker.stop();
                    speechRecorder.stop();
                    setPlayingId(null);
                    setActiveSession(null);
                  }}
                  className="w-8 h-8 rounded-lg bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Module Instructions & Focus Drill Card */}
            {!completedReport && (
              <div className="px-5 py-3 border-b border-slate-800/80 bg-slate-950/70 flex flex-wrap items-center justify-between gap-3 text-xs shrink-0">
                <div className="flex items-center gap-2 max-w-xl">
                  <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold uppercase tracking-wider text-[10px]">
                    {activeSession.mode?.replace('_', ' ')}
                  </span>
                  <p className="text-slate-300 font-medium truncate">
                    {activeSession.scenario_prompt || activeSession.topic}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={toggleListening}
                    className={`px-3 py-1.5 rounded-lg border text-xs font-bold flex items-center gap-1.5 transition-all ${
                      isListening
                        ? 'bg-rose-500 text-white border-rose-400 shadow-md shadow-rose-500/30 animate-pulse'
                        : 'bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border-emerald-500/30'
                    }`}
                  >
                    {isListening ? (
                      <>
                        <MicOff className="w-3.5 h-3.5 text-white" />
                        <span>Recording ({speechTimer}s)</span>
                      </>
                    ) : (
                      <>
                        <Mic className="w-3.5 h-3.5" />
                        <span>Record Voice with Mic</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}

            {/* If completed report is available, show Report view */}
            {completedReport ? (
              <div className="flex-1 p-6 md:p-8 overflow-y-auto space-y-6 bg-slate-950/60">
                <div className="p-6 rounded-2xl bg-gradient-to-r from-emerald-950/60 to-slate-900 border border-emerald-500/30 flex flex-col md:flex-row md:items-center justify-between gap-6">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest">
                        Performance Evaluation Scorecard
                      </span>
                      {/* Speaker button to listen to summary feedback */}
                      {completedReport.summary_feedback && (
                        <button
                          onClick={() => speakText(completedReport.summary_feedback, 'summary-feedback')}
                          className="p-1 rounded-md text-emerald-400 hover:text-emerald-300 transition-colors"
                          title={playingId === 'summary-feedback' ? 'Stop audio' : 'Listen to summary feedback'}
                        >
                          {playingId === 'summary-feedback' ? (
                            <VolumeX className="w-4 h-4 text-rose-300 animate-pulse" />
                          ) : (
                            <Volume2 className="w-4 h-4" />
                          )}
                        </button>
                      )}
                    </div>
                    <h4 className="text-2xl font-black text-white">{completedReport.topic}</h4>
                    <p className="text-xs text-slate-300 mt-2 max-w-xl leading-relaxed">
                      {completedReport.summary_feedback}
                    </p>
                  </div>
                  <div className="flex flex-col items-center justify-center p-4 rounded-xl bg-slate-900/80 border border-emerald-500/30 shrink-0 min-w-[130px]">
                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Overall Score</span>
                    <span className="text-4xl font-extrabold text-white mt-1">{completedReport.overall_score}</span>
                    <span className="text-xs text-emerald-400 font-semibold mt-0.5">/ 100</span>
                  </div>
                </div>

                {/* Metrics Breakdown Grid */}
                <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
                  <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-center">
                    <span className="text-[10px] text-slate-400 font-bold block uppercase">Pronunciation</span>
                    <span className="text-xl font-extrabold text-emerald-400 mt-1 block">
                      {completedReport.pronunciation_score}%
                    </span>
                  </div>
                  <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-center">
                    <span className="text-[10px] text-slate-400 font-bold block uppercase">Grammar</span>
                    <span className="text-xl font-extrabold text-blue-400 mt-1 block">
                      {completedReport.grammar_score}%
                    </span>
                  </div>
                  <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-center">
                    <span className="text-[10px] text-slate-400 font-bold block uppercase">Fluency</span>
                    <span className="text-xl font-extrabold text-indigo-400 mt-1 block">
                      {completedReport.fluency_score}%
                    </span>
                  </div>
                  <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-center">
                    <span className="text-[10px] text-slate-400 font-bold block uppercase">Vocabulary</span>
                    <span className="text-xl font-extrabold text-purple-400 mt-1 block">
                      {completedReport.vocabulary_score}%
                    </span>
                  </div>
                  <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-center">
                    <span className="text-[10px] text-slate-400 font-bold block uppercase">Clarity</span>
                    <span className="text-xl font-extrabold text-amber-400 mt-1 block">
                      {completedReport.confidence_clarity_score}%
                    </span>
                  </div>
                  <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-center">
                    <span className="text-[10px] text-slate-400 font-bold block uppercase">Pace (WPM)</span>
                    <span className="text-xl font-extrabold text-teal-400 mt-1 block">
                      {completedReport.speed_wpm}
                    </span>
                  </div>
                </div>

                {/* Mistakes & Corrections with Speaker Button */}
                {completedReport.mistakes_and_corrections?.length > 0 && (
                  <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                    <h5 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-rose-400" />
                      <span>Mistakes & Corrections</span>
                    </h5>
                    <div className="space-y-2.5">
                      {completedReport.mistakes_and_corrections.map((item, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs">
                          <div className="text-rose-400 line-through">"{item.original}"</div>
                          <div className="flex items-center justify-between mt-1">
                            <div className="text-emerald-400 font-semibold">✓ "{item.correction}"</div>
                            <button
                              onClick={() => speakText(item.correction, `mistake-${idx}`)}
                              className="p-1 rounded text-slate-400 hover:text-emerald-400 transition-colors flex items-center gap-1"
                              title="Listen to corrected speech"
                            >
                              {playingId === `mistake-${idx}` ? (
                                <VolumeX className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
                              ) : (
                                <Volume2 className="w-3.5 h-3.5" />
                              )}
                              <span className="text-[10px]">{playingId === `mistake-${idx}` ? 'Stop' : 'Listen'}</span>
                            </button>
                          </div>
                          {item.reason && <div className="text-slate-400 text-[11px] mt-1">{item.reason}</div>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Better Sentence Suggestions with Speaker Button */}
                {completedReport.better_sentence_suggestions?.length > 0 && (
                  <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                    <h5 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-amber-400" />
                      <span>Better Sentence & Executive Alternatives</span>
                    </h5>
                    <div className="space-y-2.5">
                      {completedReport.better_sentence_suggestions.map((item, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs">
                          <div className="text-slate-400">Original: "{item.original}"</div>
                          <div className="flex items-center justify-between mt-1">
                            <div className="text-amber-300 font-semibold">Upgrade: "{item.better_alternative}"</div>
                            <button
                              onClick={() => speakText(item.better_alternative, `upgrade-${idx}`)}
                              className="p-1 rounded text-slate-400 hover:text-amber-300 transition-colors flex items-center gap-1"
                              title="Listen to professional alternative"
                            >
                              {playingId === `upgrade-${idx}` ? (
                                <VolumeX className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
                              ) : (
                                <Volume2 className="w-3.5 h-3.5" />
                              )}
                              <span className="text-[10px]">{playingId === `upgrade-${idx}` ? 'Stop' : 'Listen'}</span>
                            </button>
                          </div>
                          {item.explanation && <div className="text-slate-400 text-[11px] mt-1">{item.explanation}</div>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actionable recommendations */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                    <h5 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-blue-400" />
                      <span>Areas for Improvement</span>
                    </h5>
                    <ul className="space-y-1.5 text-xs text-slate-300 list-disc list-inside">
                      {completedReport.areas_for_improvement?.map((area, i) => (
                        <li key={i}>{area}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                    <h5 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-emerald-400" />
                      <span>Personalized Practice Drills</span>
                    </h5>
                    <ul className="space-y-1.5 text-xs text-slate-300 list-disc list-inside">
                      {completedReport.personalized_recommendations?.map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="text-center pt-2">
                  <button
                    onClick={() => {
                      speechSpeaker.stop();
                      speechRecorder.stop();
                      setPlayingId(null);
                      setActiveSession(null);
                    }}
                    className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs"
                  >
                    Done & Return to Modules
                  </button>
                </div>
              </div>
            ) : (
              /* Live Chat & Voice Flow */
              <>
                <div ref={chatScrollRef} className="flex-1 p-4 md:p-6 overflow-y-auto space-y-4 bg-slate-950/40">
                  {exchanges.map((ex, idx) => {
                    const isUser = ex.sender === 'user';
                    const msgId = ex.id || `exchange-${idx}`;
                    const isMsgPlaying = playingId === msgId;

                    return (
                      <div key={msgId} className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
                        <div className="flex items-center gap-2 mb-1 px-1">
                          <span className="text-[10px] font-bold text-slate-400">
                            {ex.sender_name || (isUser ? 'You' : 'AI Coach')}
                          </span>

                          {/* Speaker Button on ALL AI & Peer Messages */}
                          {!isUser && (
                            <button
                              onClick={() => speakText(ex.content, msgId)}
                              className={`p-1 rounded text-xs flex items-center gap-1 transition-colors ${
                                isMsgPlaying
                                  ? 'bg-emerald-500/20 text-emerald-300 ring-1 ring-emerald-500/40'
                                  : 'text-slate-400 hover:text-emerald-300'
                              }`}
                              title={isMsgPlaying ? 'Stop listening' : 'Listen to this message'}
                            >
                              {isMsgPlaying ? (
                                <>
                                  <VolumeX className="w-3 h-3 text-rose-300 animate-pulse" />
                                  <span className="text-[9px] font-bold text-rose-300">Stop</span>
                                </>
                              ) : (
                                <>
                                  <Volume2 className="w-3 h-3" />
                                  <span className="text-[9px]">Listen</span>
                                </>
                              )}
                            </button>
                          )}
                        </div>

                        <div
                          className={`max-w-[85%] md:max-w-[70%] p-4 rounded-2xl text-sm leading-relaxed ${
                            isUser
                              ? 'bg-emerald-600 text-white rounded-br-none shadow-md shadow-emerald-600/20'
                              : `bg-slate-800/90 text-slate-100 rounded-bl-none border shadow-md ${
                                  isMsgPlaying ? 'border-emerald-500/60 ring-2 ring-emerald-500/20' : 'border-slate-700/80'
                                }`
                          }`}
                        >
                          <p className="whitespace-pre-wrap">{ex.content}</p>

                          {ex.turn_feedback?.tip && (
                            <div className="mt-2 pt-2 border-t border-emerald-500/30 text-[11px] text-emerald-200 flex items-center gap-1.5">
                              <Sparkles className="w-3.5 h-3.5 shrink-0" />
                              <span>{ex.turn_feedback.tip}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                  {sending && (
                    <div className="flex items-center gap-2 text-xs text-slate-400 p-2">
                      <RefreshCw className="w-3.5 h-3.5 animate-spin text-emerald-400" />
                      <span>AI Coach is analyzing your speech...</span>
                    </div>
                  )}
                </div>

                {/* Bottom Input Controls */}
                <div className="p-4 border-t border-slate-800 bg-slate-900/95 shrink-0 space-y-2">
                  {/* Recorded Audio Preview Bar if user captured voice */}
                  {recordedAudioUrl && (
                    <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 flex flex-wrap items-center justify-between gap-2 animate-fadeIn text-xs">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-400" />
                        <span className="text-slate-300 font-semibold">Your Voice Recording:</span>
                        <audio src={recordedAudioUrl} controls className="h-7 max-w-[220px]" />
                      </div>

                      {(!userInput || !userInput.trim()) && (
                        <button
                          type="button"
                          onClick={() => handleAutoTranscribeAudio()}
                          disabled={transcribing}
                          className="px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold flex items-center gap-1.5 transition-colors"
                        >
                          {transcribing ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                          <span>Auto-Transcribe Recorded Audio</span>
                        </button>
                      )}
                    </div>
                  )}

                  {isListening && (
                    <div className="flex items-center justify-between text-xs text-rose-400 font-semibold px-2 animate-pulse">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                        <span>Listening to microphone live ({speechTimer}s)... Speak clearly</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Activity className="w-3 h-3 text-rose-400 animate-pulse" />
                        <span className="text-[10px] text-slate-400">Mic Level:</span>
                        <div className="w-16 h-2 bg-slate-800 rounded overflow-hidden border border-slate-700">
                          <div
                            className="h-full bg-gradient-to-r from-emerald-400 to-rose-400 transition-all duration-75"
                            style={{ width: `${Math.max(5, audioVolume)}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-xs text-slate-400 px-1">
                    <span className="text-[11px] text-slate-500">
                      {userInput.trim() ? `${userInput.trim().split(/\s+/).length} words recorded` : 'Speak into mic to record your response'}
                    </span>
                    <button
                      type="button"
                      onClick={handleDictateExampleMessage}
                      className="text-[11px] text-slate-400 hover:text-emerald-400 transition-colors flex items-center gap-1"
                      title="Dictate an example response for oral assessment"
                    >
                      <Lightbulb className="w-3 h-3 text-amber-400" />
                      <span>Dictate Example Response</span>
                    </button>
                  </div>

                  <form onSubmit={handleSendMessage} className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={toggleListening}
                      className={`p-3 rounded-xl border flex items-center justify-center transition-all ${
                        isListening
                          ? 'bg-rose-500 text-white border-rose-400 shadow-lg shadow-rose-500/30 animate-pulse'
                          : 'bg-slate-800 text-slate-300 border-slate-700 hover:text-white hover:border-slate-600'
                      }`}
                      title={isListening ? 'Stop Recording' : 'Speak into Microphone'}
                    >
                      {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5 text-emerald-400" />}
                    </button>

                    <input
                      type="text"
                      placeholder={isListening ? 'Listening live... words will appear here' : 'Type or speak your answer...'}
                      value={userInput}
                      onChange={(e) => setUserInput(e.target.value)}
                      className={`flex-1 px-4 py-3 rounded-xl bg-slate-800/80 border text-white text-sm focus:outline-none placeholder-slate-500 transition-colors ${
                        isListening ? 'border-rose-500/70 shadow-sm shadow-rose-500/10' : 'border-slate-700 focus:border-emerald-500'
                      }`}
                    />

                    {userInput.trim() && (
                      <button
                        type="button"
                        onClick={() => {
                          setUserInput('');
                          setRecordedAudioUrl(null);
                          setRecordedAudioBlob(null);
                        }}
                        className="px-2 text-xs text-slate-500 hover:text-slate-300 transition-colors"
                      >
                        Clear
                      </button>
                    )}

                    <button
                      type="submit"
                      disabled={!userInput.trim() || sending}
                      className="p-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold transition-all disabled:opacity-40 disabled:hover:bg-emerald-600 shadow-md shadow-emerald-500/20"
                    >
                      <Send className="w-5 h-5" />
                    </button>
                  </form>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* 10 Modes Grid Catalog */}
      <div>
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-emerald-400" />
          <span>Interactive Communication Modules</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {MODES.map((m) => {
            const Icon = m.icon;
            return (
              <div
                key={m.id}
                className="group rounded-xl bg-slate-900/70 border border-slate-800 hover:border-emerald-500/50 p-5 flex flex-col justify-between transition-all duration-200 hover:-translate-y-1 hover:shadow-xl hover:shadow-emerald-950/40"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className={`w-9 h-9 rounded-xl border flex items-center justify-center ${m.color}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                      <Mic className="w-2.5 h-2.5" />
                      <span>Voice Ready</span>
                    </span>
                  </div>
                  <h4 className="text-base font-bold text-white group-hover:text-emerald-300 transition-colors">
                    {m.title}
                  </h4>
                  <p className="text-xs text-slate-400 mt-2 line-clamp-3 leading-relaxed">
                    {m.tagline}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-2">
                  <button
                    onClick={() => handleDirectLaunch(m.id)}
                    className="w-full py-2 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center justify-center gap-1.5 shadow-md shadow-emerald-500/20 transition-all"
                  >
                    <Mic className="w-3.5 h-3.5" />
                    <span>Start Voice Practice</span>
                  </button>
                  <button
                    onClick={() => handleStartSession(m.id)}
                    className="w-full py-1 text-center text-[11px] text-slate-400 hover:text-emerald-300 transition-colors block"
                  >
                    Select Custom Topic...
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* History of Past Sessions */}
      <div>
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5 text-teal-400" />
          <span>Practice Session History</span>
        </h3>

        {sessions.length === 0 ? (
          <div className="rounded-2xl bg-slate-900/40 border border-slate-800/80 p-8 text-center">
            <MessageSquare className="w-10 h-10 text-slate-600 mx-auto mb-2" />
            <h4 className="text-sm font-bold text-white">No communication practice sessions yet</h4>
            <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1 mb-4">
              Select any of the 10 modules above to sharpen your English pronunciation, sentence structure, and workplace speaking.
            </p>
            <button
              onClick={() => handleStartSession('daily_practice')}
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs"
            >
              Start Daily Practice
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {sessions.map((item) => (
              <div
                key={item.id}
                className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between text-xs text-emerald-400 uppercase font-semibold mb-1">
                    <span>{item.mode?.replace('_', ' ')}</span>
                    <span className="text-slate-400 text-[11px] font-normal">
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-white truncate">{item.topic}</h4>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <Award className="w-4 h-4 text-emerald-400" />
                    <span className="text-sm font-bold text-white">{item.overall_score || '--'}</span>
                    <span className="text-[10px] text-slate-400">/ 100</span>
                  </div>

                  <button
                    onClick={async () => {
                      const res = await api.get(`/interviews/communication/${item.id}/`);
                      setActiveSession(res.session);
                      setCompletedReport(res.session.status === 'completed' ? res.session : null);
                      setExchanges(res.session.exchanges || []);
                    }}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition-colors"
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Start Session Setup Modal */}
      {showStartModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <h4 className="text-base font-bold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <span>Configure Communication Practice</span>
              </h4>
              <button
                onClick={() => setShowStartModal(false)}
                className="w-7 h-7 rounded-lg bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleLaunchSession} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Selected Module
                </label>
                <select
                  value={selectedMode}
                  onChange={(e) => {
                    setSelectedMode(e.target.value);
                    const list = topicsCatalog[e.target.value] || [];
                    setSelectedTopic(list[0] || '');
                  }}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-xs"
                >
                  {MODES.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.title}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Choose a Curated Practice Topic
                </label>
                <select
                  value={selectedTopic}
                  onChange={(e) => setSelectedTopic(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-xs"
                >
                  {(topicsCatalog[selectedMode] || []).map((t, idx) => (
                    <option key={idx} value={t}>
                      {t}
                    </option>
                  ))}
                  <option value="Custom">Custom Topic...</option>
                </select>
              </div>

              {selectedTopic === 'Custom' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Custom Scenario or Topic
                  </label>
                  <input
                    type="text"
                    placeholder="Enter custom scenario or presentation topic..."
                    value={customTopic}
                    onChange={(e) => setCustomTopic(e.target.value)}
                    required
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-xs"
                  />
                </div>
              )}

              <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowStartModal(false)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:text-white text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={sending}
                  className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-1.5 shadow-md"
                >
                  {sending ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Starting...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-3.5 h-3.5" />
                      <span>Launch Session</span>
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
