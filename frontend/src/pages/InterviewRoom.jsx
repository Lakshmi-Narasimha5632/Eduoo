import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Clock,
  Sparkles,
  RefreshCw,
  LogOut,
  Volume2,
  VolumeX,
  Mic,
  MicOff,
  Video,
  VideoOff,
  HelpCircle,
  Lightbulb,
  AlertCircle,
  Code2,
  Bot,
  User,
  ChevronRight,
  Copy,
  Check,
  CheckCircle2,
} from 'lucide-react';
import { api } from '../api/client';
import { useToast } from '../context/ToastContext';
import { getAgentProfile } from '../constants/aiAgents';
import { speechSpeaker, speechRecorder } from '../utils/speechService';

export const InterviewRoom = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast, confirm } = useToast();

  // Interview state
  const [session, setSession] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [finishing, setFinishing] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Chat & Answer state
  const [answerText, setAnswerText] = useState('');
  const [timerSeconds, setTimerSeconds] = useState(0);

  // Audio / Speech Recognition state
  const [isListening, setIsListening] = useState(false);
  const [voiceOutputEnabled, setVoiceOutputEnabled] = useState(true);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentSpeakingKey, setCurrentSpeakingKey] = useState(null);
  const [speechDuration, setSpeechDuration] = useState(0);
  const [micVolume, setMicVolume] = useState(0);

  // Recorded Audio Backup & Playback state
  const [recordedAudioUrl, setRecordedAudioUrl] = useState(null);
  const [recordedAudioBlob, setRecordedAudioBlob] = useState(null);
  const [transcribing, setTranscribing] = useState(false);

  // Last Evaluated Answer Preview
  const [lastEvaluation, setLastEvaluation] = useState(null);

  // Video Camera Simulator
  const [cameraActive, setCameraActive] = useState(false);
  const videoRef = useRef(null);
  const mediaStreamRef = useRef(null);

  // Code Workspace Drawer
  const [showCodeDrawer, setShowCodeDrawer] = useState(false);
  const [codeSnippet, setCodeSnippet] = useState('// Architecture or algorithm draft\nfunction solution() {\n  \n}');
  const [copiedCode, setCopiedCode] = useState(false);

  // Stop any ongoing speech or microphone on unmount
  useEffect(() => {
    return () => {
      speechSpeaker.stop();
      speechRecorder.stop();
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  // Fetch interview details
  const fetchInterviewDetails = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.get(`/interviews/${id}/`);
      const interviewData = res.interview || res;
      setSession(interviewData);

      const currQ = res.current_question || interviewData.current_question;
      setCurrentQuestion(currQ);
    } catch (err) {
      setErrorMsg(err?.message || 'Failed to load interview room.');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchInterviewDetails();
  }, [fetchInterviewDetails]);

  // Overall Timer
  useEffect(() => {
    const timer = setInterval(() => {
      setTimerSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Mic recording duration timer
  useEffect(() => {
    let interval = null;
    if (isListening) {
      interval = setInterval(() => {
        setSpeechDuration((prev) => prev + 1);
      }, 1000);
    } else {
      setSpeechDuration(0);
    }
    return () => clearInterval(interval);
  }, [isListening]);

  // Unified speech playback function
  const handleSpeakText = (text, key = 'interviewer') => {
    if (!text) return;

    if (isSpeaking && currentSpeakingKey === key) {
      speechSpeaker.stop();
      setIsSpeaking(false);
      setCurrentSpeakingKey(null);
      return;
    }

    if (isListening) {
      speechRecorder.stop();
      setIsListening(false);
    }

    setCurrentSpeakingKey(key);
    setIsSpeaking(true);

    speechSpeaker.speak(text, {
      id: key,
      onStart: () => {
        setIsSpeaking(true);
        setCurrentSpeakingKey(key);
      },
      onEnd: () => {
        setIsSpeaking(false);
        setCurrentSpeakingKey(null);
      },
      onError: (err) => {
        console.warn('Speech playback notice:', err);
        setIsSpeaking(false);
        setCurrentSpeakingKey(null);
      },
    });
  };

  // Auto transcribe recorded audio blob
  const handleAutoTranscribeAudio = async (blobToTranscribe = null) => {
    const blob = blobToTranscribe || recordedAudioBlob;
    if (!blob) return;

    setTranscribing(true);
    setErrorMsg(null);
    try {
      const qContext = currentQuestion?.question || currentQuestion?.question_text || '';
      const transcript = await speechRecorder.transcribeAudioBlob(blob, qContext);
      if (transcript && transcript.trim()) {
        setAnswerText((prev) => (prev ? `${prev.trim()} ${transcript.trim()}` : transcript.trim()));
      }
    } catch (err) {
      console.warn('Auto transcription notice:', err);
    } finally {
      setTranscribing(false);
    }
  };

  // Unified microphone toggle
  const handleToggleMic = async () => {
    setErrorMsg(null);

    if (isListening) {
      const finalRecordedText = speechRecorder.stop();
      setIsListening(false);
      setMicVolume(0);

      if (finalRecordedText && finalRecordedText.trim()) {
        setAnswerText(finalRecordedText.trim());
      }
    } else {
      if (isSpeaking) {
        speechSpeaker.stop();
        setIsSpeaking(false);
        setCurrentSpeakingKey(null);
      }

      setRecordedAudioUrl(null);
      setRecordedAudioBlob(null);

      speechRecorder.start({
        initialText: answerText,
        onResult: (fullText) => {
          setAnswerText(fullText);
        },
        onVolume: (vol) => {
          setMicVolume(vol);
        },
        onError: (errMsg) => {
          console.warn('Microphone notice:', errMsg);
          setErrorMsg(errMsg);
        },
        onStatusChange: (active) => {
          setIsListening(active);
          if (!active) setMicVolume(0);
        },
        onAudioReady: ({ audioBlob, audioUrl }) => {
          setRecordedAudioBlob(audioBlob);
          setRecordedAudioUrl(audioUrl);

          // If SpeechRecognition produced no text (e.g. Chrome network blocked), auto-transcribe audio blob!
          if (!answerText.trim()) {
            handleAutoTranscribeAudio(audioBlob);
          }
        },
      });

      setIsListening(true);
    }
  };

  // Insert structured role-specific answer
  const handleInsertSampleAnswer = () => {
    const role = session?.target_role || 'Software Engineer';
    const sample = `In my experience as a ${role}, I design this solution by first evaluating performance constraints and bottlenecks. We implement distributed caching using Redis with an LRU eviction policy to maintain sub-20ms latency. We optimize database queries with composite indices and handle high-throughput spikes using asynchronous message queues to ensure fault tolerance.`;
    setAnswerText(sample);
  };

  // Camera toggle
  const toggleCamera = async () => {
    if (cameraActive) {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
        mediaStreamRef.current = null;
      }
      setCameraActive(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        mediaStreamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        setCameraActive(true);
      } catch (err) {
        console.warn('Webcam access not granted or unavailable:', err);
        setCameraActive(true);
      }
    }
  };

  // Submit Answer to current question
  const handleSubmitAnswer = async (e) => {
    e?.preventDefault();
    const trimmed = answerText.trim();
    if (!trimmed || sending) return;

    if (isListening) {
      speechRecorder.stop();
      setIsListening(false);
    }

    speechSpeaker.stop();
    setIsSpeaking(false);
    setCurrentSpeakingKey(null);

    setSending(true);
    setErrorMsg(null);
    try {
      const res = await api.post(`/interviews/${id}/answer/`, { answer: trimmed });
      setAnswerText('');
      setRecordedAudioUrl(null);
      setRecordedAudioBlob(null);

      // Save last evaluation preview to display on screen
      if (res.evaluation) {
        setLastEvaluation({
          order: currentQuestion?.order,
          question: currentQuestion?.question || currentQuestion?.question_text,
          answer: trimmed,
          score: res.evaluation.score,
          feedback: res.evaluation.feedback,
          strengths: res.evaluation.strengths,
          weaknesses: res.evaluation.weaknesses,
        });
        toast.success(`Question ${currentQuestion?.order || 1} evaluated! Score: ${res.evaluation.score}/100`, 'Evaluation Updated');
      }

      if (res.is_complete || res.is_finished) {
        toast.success('Interview complete! Directing to comprehensive scorecard...', 'Round Completed');
        navigate(`/interviews/${id}/result`);
      } else if (res.next_question) {
        setCurrentQuestion(res.next_question);
        if (voiceOutputEnabled) {
          handleSpeakText(res.next_question.question || res.next_question.question_text, 'next-q');
        }
      }
    } catch (err) {
      const msg = err?.message || 'Failed to submit answer.';
      setErrorMsg(msg);
      toast.error(msg, 'Submission Error');
    } finally {
      setSending(false);
    }
  };

  // Request Hint or Clarification
  const handleInteraction = async (type) => {
    setSending(true);
    toast.info(`Requesting ${type} from interviewer...`, 'Consulting Interviewer');
    try {
      const res = await api.post(`/interviews/${id}/agent-interaction/`, {
        type,
        message: type === 'hint' ? 'Could you give me an architectural hint?' : 'Could you clarify the production constraints?',
      });
      if (res.agent_response) {
        if (voiceOutputEnabled) {
          handleSpeakText(res.agent_response, 'hint-reply');
        }
        fetchInterviewDetails();
      }
    } catch (err) {
      const msg = err?.message || 'Interaction failed';
      setErrorMsg(msg);
      toast.error(msg, 'Interaction Notice');
    } finally {
      setSending(false);
    }
  };

  // End Interview Early
  const handleFinishEarly = async () => {
    const isConfirmed = await confirm({
      title: 'Finish Interview Early?',
      message: 'Are you sure you want to conclude the interview and calculate your scorecard now? Your evaluation will be synthesized based on your submitted answers.',
      confirmText: 'Yes, Finish & Score',
      cancelText: 'Stay in Interview',
      variant: 'primary',
    });
    if (!isConfirmed) return;

    setFinishing(true);
    toast.info('Synthesizing your multi-dimensional evaluation scorecard...', 'Grading Interview');
    speechSpeaker.stop();
    speechRecorder.stop();
    try {
      await api.post(`/interviews/${id}/finish/`);
      toast.success('Scorecard synthesized successfully!', 'Interview Finished');
      navigate(`/interviews/${id}/result`);
    } catch (err) {
      const msg = err?.message || 'Failed to finish interview';
      setErrorMsg(msg);
      toast.error(msg, 'Evaluation Notice');
      setFinishing(false);
    }
  };

  const agentProfile = getAgentProfile(session?.agent_persona || 'alex_architect');
  const totalQuestions = session?.num_questions || 5;
  const currentOrder = currentQuestion?.order || 1;

  const formatTimer = (s) => {
    const mins = Math.floor(s / 60);
    const secs = s % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center text-slate-400">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mb-3" />
        <p className="text-xs uppercase tracking-wider font-semibold">Entering AI Interview Room...</p>
      </div>
    );
  }

  const currentQText = currentQuestion?.question || currentQuestion?.question_text || '';

  return (
    <div className="space-y-5 animate-fadeIn pb-8">
      {/* Top Header Bar */}
      <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-900 border border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-white">{session?.target_role}</span>
              <span className="text-[10px] text-blue-400 uppercase font-semibold">
                • {session?.interview_type?.replace('_', ' ')}
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Interviewer: {agentProfile.name} ({agentProfile.company})
            </p>
          </div>
        </div>

        {/* Center Progress & Timer */}
        <div className="flex items-center gap-4 sm:gap-6">
          <div className="hidden sm:flex items-center gap-2">
            <span className="text-xs text-slate-400">Question</span>
            <span className="px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-300 font-extrabold text-xs">
              {currentOrder} / {totalQuestions}
            </span>
          </div>

          <div className="flex items-center gap-1.5 font-mono text-xs text-slate-300 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
            <Clock className="w-3.5 h-3.5 text-blue-400" />
            <span>{formatTimer(timerSeconds)}</span>
          </div>

          <button
            onClick={handleFinishEarly}
            disabled={finishing}
            className="px-3.5 py-1.5 rounded-xl bg-rose-600/10 hover:bg-rose-600/20 border border-rose-500/30 text-rose-400 hover:text-rose-300 text-xs font-semibold transition-colors flex items-center gap-1.5"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Finish Early</span>
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main Dual-Tile Video / Interviewer Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Tile 1: AI Interviewer */}
        <div className="relative h-64 md:h-72 rounded-2xl bg-slate-950 border border-slate-800 overflow-hidden flex flex-col justify-between p-5 shadow-inner">
          <div className="flex items-center justify-between relative z-10">
            <div className="flex items-center gap-2">
              <span className={`w-2.5 h-2.5 rounded-full ${isSpeaking ? 'bg-blue-400 animate-ping' : 'bg-emerald-400 animate-pulse'}`} />
              <span className="text-xs font-bold text-white">{agentProfile.name}</span>
              {isSpeaking && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  Speaking...
                </span>
              )}
            </div>

            <div className="flex items-center gap-1.5">
              <button
                onClick={() => handleSpeakText(currentQText, 'interviewer-voice')}
                className={`p-2 rounded-lg border text-xs flex items-center gap-1.5 transition-colors ${
                  isSpeaking && currentSpeakingKey === 'interviewer-voice'
                    ? 'bg-blue-600 border-blue-500 text-white shadow-md shadow-blue-500/30'
                    : 'bg-slate-900 border-slate-700 text-slate-300 hover:text-white hover:border-slate-600'
                }`}
                title={isSpeaking && currentSpeakingKey === 'interviewer-voice' ? 'Stop Voice' : 'Play Voice'}
              >
                {isSpeaking && currentSpeakingKey === 'interviewer-voice' ? (
                  <>
                    <VolumeX className="w-3.5 h-3.5 text-rose-300" />
                    <span className="text-[11px] font-bold">Stop Audio</span>
                  </>
                ) : (
                  <>
                    <Volume2 className="w-3.5 h-3.5 text-blue-400" />
                    <span className="text-[11px] font-bold">Play Voice</span>
                  </>
                )}
              </button>

              <button
                onClick={() => {
                  const nextState = !voiceOutputEnabled;
                  setVoiceOutputEnabled(nextState);
                  if (!nextState && isSpeaking) {
                    speechSpeaker.stop();
                    setIsSpeaking(false);
                    setCurrentSpeakingKey(null);
                  }
                }}
                className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors"
                title={voiceOutputEnabled ? 'Auto-voice enabled (Click to mute)' : 'Auto-voice disabled (Click to enable)'}
              >
                {voiceOutputEnabled ? <Volume2 className="w-4 h-4 text-emerald-400" /> : <VolumeX className="w-4 h-4 text-slate-500" />}
              </button>
            </div>
          </div>

          {/* Animated Wave / Avatar Centerpiece */}
          <div className="flex flex-col items-center justify-center relative z-10">
            <div className="relative">
              <div className={`w-20 h-20 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white text-2xl font-black shadow-xl ${
                isSpeaking ? 'shadow-blue-500/50 ring-4 ring-blue-500/30' : 'shadow-blue-500/25'
              }`}>
                {agentProfile.name.charAt(0)}
              </div>
              <span className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-slate-900 border-2 border-slate-950 flex items-center justify-center text-[10px]">
                🤖
              </span>
            </div>

            {/* Speaking Audio Waves */}
            <div className="flex items-center gap-1.5 mt-4 h-6">
              <span className={`w-1 rounded-full transition-all ${isSpeaking ? 'h-4 bg-blue-500 animate-bounce' : 'h-1.5 bg-slate-700'}`} style={{ animationDelay: '0ms' }} />
              <span className={`w-1 rounded-full transition-all ${isSpeaking ? 'h-6 bg-indigo-400 animate-bounce' : 'h-1.5 bg-slate-700'}`} style={{ animationDelay: '150ms' }} />
              <span className={`w-1 rounded-full transition-all ${isSpeaking ? 'h-5 bg-cyan-400 animate-bounce' : 'h-1.5 bg-slate-700'}`} style={{ animationDelay: '300ms' }} />
              <span className={`w-1 rounded-full transition-all ${isSpeaking ? 'h-3 bg-blue-400 animate-bounce' : 'h-1.5 bg-slate-700'}`} style={{ animationDelay: '450ms' }} />
            </div>
          </div>

          <div className="text-[11px] text-slate-400 relative z-10 flex items-center justify-between">
            <span>{agentProfile.title}</span>
            <span className="text-blue-400 font-semibold">{agentProfile.company}</span>
          </div>
        </div>

        {/* Tile 2: Candidate Feed / Webcam Simulator */}
        <div className="relative h-64 md:h-72 rounded-2xl bg-slate-950 border border-slate-800 overflow-hidden flex flex-col justify-between p-5 shadow-inner">
          <div className="flex items-center justify-between relative z-10">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-white">You (Candidate)</span>
              {isListening && (
                <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 animate-pulse">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping" />
                  <span>Recording ({speechDuration}s)</span>
                </div>
              )}
            </div>

            <div className="flex items-center gap-1.5">
              <button
                onClick={handleToggleMic}
                className={`p-2 rounded-lg border text-xs flex items-center gap-1.5 transition-colors ${
                  isListening
                    ? 'bg-rose-500 text-white border-rose-400 shadow-md shadow-rose-500/30 animate-pulse'
                    : 'bg-slate-900 border-slate-700 text-slate-300 hover:text-white'
                }`}
                title={isListening ? 'Stop Recording Microphone' : 'Start Recording Microphone'}
              >
                {isListening ? (
                  <>
                    <MicOff className="w-3.5 h-3.5 text-white" />
                    <span className="text-[11px] font-bold">Stop Mic</span>
                  </>
                ) : (
                  <>
                    <Mic className="w-3.5 h-3.5 text-blue-400" />
                    <span className="text-[11px] font-bold">Start Mic</span>
                  </>
                )}
              </button>

              <button
                onClick={toggleCamera}
                className={`p-2 rounded-lg border transition-colors ${
                  cameraActive
                    ? 'bg-blue-600 text-white border-blue-500'
                    : 'bg-slate-900 border-slate-700 text-slate-400 hover:text-white'
                }`}
                title={cameraActive ? 'Turn Off Camera' : 'Turn On Camera'}
              >
                {cameraActive ? <Video className="w-4 h-4" /> : <VideoOff className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Camera Feed or Default Candidate Avatar */}
          <div className="flex flex-col items-center justify-center relative z-10">
            {cameraActive ? (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-32 h-24 object-cover rounded-xl border border-slate-700 shadow-md"
              />
            ) : (
              <div className={`w-20 h-20 rounded-full bg-slate-800 border flex items-center justify-center text-slate-400 text-2xl font-bold transition-all ${
                isListening ? 'border-rose-500 ring-4 ring-rose-500/20 shadow-rose-500/30 shadow-lg' : 'border-slate-700'
              }`}>
                <User className="w-8 h-8" />
              </div>
            )}

            {/* Speaking Audio Waves for Candidate */}
            <div className="flex items-center gap-1.5 mt-3 h-5">
              <span className={`w-1 rounded-full transition-all ${isListening ? 'h-3 bg-rose-500 animate-bounce' : 'h-1 bg-slate-700'}`} style={{ animationDelay: '0ms' }} />
              <span className={`w-1 rounded-full transition-all ${isListening ? 'h-5 bg-rose-400 animate-bounce' : 'h-1 bg-slate-700'}`} style={{ animationDelay: '150ms' }} />
              <span className={`w-1 rounded-full transition-all ${isListening ? 'h-4 bg-amber-400 animate-bounce' : 'h-1 bg-slate-700'}`} style={{ animationDelay: '300ms' }} />
              <span className={`w-1 rounded-full transition-all ${isListening ? 'h-2 bg-rose-400 animate-bounce' : 'h-1 bg-slate-700'}`} style={{ animationDelay: '450ms' }} />
            </div>

            <span className="text-xs text-slate-400 mt-1 font-medium">
              {isListening ? 'Recording voice live... spoken words appear below' : 'Ready to articulate solution'}
            </span>
          </div>

          <div className="text-[11px] text-slate-500 relative z-10 flex items-center justify-between">
            <span className={isListening ? 'text-rose-400 font-semibold flex items-center gap-1.5' : ''}>
              {isListening ? (
                <>
                  <span>Audio: Live ({speechDuration}s)</span>
                  <div className="w-12 h-1.5 bg-slate-800 rounded overflow-hidden inline-block border border-slate-700">
                    <div
                      className="h-full bg-gradient-to-r from-emerald-400 to-rose-400 transition-all duration-75"
                      style={{ width: `${Math.max(5, micVolume)}%` }}
                    />
                  </div>
                </>
              ) : (
                'Audio: Standby'
              )}
            </span>
            <span>Camera: {cameraActive ? 'Connected' : 'Off'}</span>
          </div>
        </div>
      </div>

      {/* Previous Evaluated Answer Card (Represented on screen!) */}
      {lastEvaluation && (
        <div className="p-4 rounded-xl bg-slate-900 border border-emerald-500/30 text-xs space-y-2 animate-fadeIn shadow-lg">
          <div className="flex items-center justify-between">
            <span className="font-bold text-emerald-400 flex items-center gap-1.5 text-xs">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Question {lastEvaluation.order} Evaluated • Score: {lastEvaluation.score}/100</span>
            </span>
            <button
              onClick={() => handleSpeakText(lastEvaluation.feedback, 'last-eval-feedback')}
              className="text-slate-400 hover:text-white p-1 rounded"
              title="Listen to feedback"
            >
              <Volume2 className="w-3.5 h-3.5 text-emerald-400" />
            </button>
          </div>
          <div className="text-slate-300">
            <span className="text-slate-500 font-semibold">Your Evaluated Answer: </span>
            "{lastEvaluation.answer}"
          </div>
          <div className="text-blue-300 bg-blue-500/10 p-2.5 rounded-lg border border-blue-500/20">
            <span className="font-semibold text-blue-200">Interviewer Feedback: </span>
            {lastEvaluation.feedback}
          </div>
        </div>
      )}

      {/* Current Question Focus Box */}
      {currentQuestion && (
        <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-950/40 via-slate-900 to-indigo-950/30 border border-blue-500/30 shadow-lg">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-extrabold text-blue-400 uppercase tracking-wider">
                Question {currentQuestion.order}
              </span>
              {currentQuestion.is_follow_up && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                  <Sparkles className="w-3 h-3" />
                  <span>Dynamic Follow-Up</span>
                </span>
              )}

              {/* Dedicated Speaker Button directly on Question */}
              <button
                onClick={() => handleSpeakText(currentQText, 'question-read')}
                className={`p-1.5 rounded-lg border text-xs flex items-center gap-1 transition-colors ${
                  isSpeaking && currentSpeakingKey === 'question-read'
                    ? 'bg-blue-600 border-blue-500 text-white shadow-md shadow-blue-500/30'
                    : 'bg-slate-800/80 hover:bg-slate-700 border-slate-700 text-blue-400 hover:text-blue-300'
                }`}
                title={isSpeaking && currentSpeakingKey === 'question-read' ? 'Stop reading question' : 'Listen to question aloud'}
              >
                {isSpeaking && currentSpeakingKey === 'question-read' ? (
                  <>
                    <VolumeX className="w-3.5 h-3.5 text-rose-300 animate-pulse" />
                    <span className="text-[10px] font-semibold text-rose-300">Stop</span>
                  </>
                ) : (
                  <>
                    <Volume2 className="w-3.5 h-3.5" />
                    <span className="text-[10px] font-semibold">Listen</span>
                  </>
                )}
              </button>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => handleInteraction('hint')}
                disabled={sending}
                className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white text-xs font-semibold transition-colors flex items-center gap-1 disabled:opacity-50"
              >
                <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
                <span>Request Hint</span>
              </button>

              <button
                onClick={() => handleInteraction('clarification')}
                disabled={sending}
                className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white text-xs font-semibold transition-colors flex items-center gap-1 disabled:opacity-50"
              >
                <HelpCircle className="w-3.5 h-3.5 text-blue-400" />
                <span>Ask Clarification</span>
              </button>

              <button
                onClick={() => setShowCodeDrawer(!showCodeDrawer)}
                className={`px-3 py-1 rounded-lg border text-xs font-semibold transition-colors flex items-center gap-1 ${
                  showCodeDrawer
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-300'
                }`}
              >
                <Code2 className="w-3.5 h-3.5" />
                <span>Code Drawer</span>
              </button>
            </div>
          </div>

          <h3 className="text-base md:text-lg font-bold text-white leading-relaxed">
            {currentQText}
          </h3>
        </div>
      )}

      {/* Code Drawer (if toggled) */}
      {showCodeDrawer && (
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2 animate-fadeIn">
          <div className="flex items-center justify-between text-xs text-slate-400 font-semibold">
            <span className="flex items-center gap-1.5">
              <Code2 className="w-4 h-4 text-blue-400" />
              <span>Candidate Architecture / Algorithm Workspace</span>
            </span>
            <button
              onClick={() => {
                navigator.clipboard.writeText(codeSnippet);
                setCopiedCode(true);
                toast.success('Architecture snippet copied to clipboard!', 'Code Copied');
                setTimeout(() => setCopiedCode(false), 2000);
              }}
              className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
            >
              {copiedCode ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              <span>{copiedCode ? 'Copied' : 'Copy'}</span>
            </button>
          </div>
          <textarea
            value={codeSnippet}
            onChange={(e) => setCodeSnippet(e.target.value)}
            rows={5}
            className="w-full p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs text-emerald-300 focus:outline-none focus:border-blue-500"
          />
        </div>
      )}

      {/* Answer Input Submission Bar */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3 shadow-xl">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span className="font-semibold text-slate-300">Your Answer (Recorded from Mic or Typed):</span>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleInsertSampleAnswer}
              className="text-xs text-slate-400 hover:text-blue-400 transition-colors flex items-center gap-1"
              title="Dictate an example answer for testing"
            >
              <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
              <span>Dictate Example Answer</span>
            </button>
            {isListening ? (
              <span className="text-rose-400 font-semibold animate-pulse">
                Recording microphone live ({speechDuration}s)...
              </span>
            ) : (
              <span className="text-slate-500">
                {answerText.trim() ? `${answerText.trim().split(/\s+/).length} words recorded` : 'Speak into mic to record'}
              </span>
            )}
          </div>
        </div>

        <textarea
          rows={4}
          placeholder="Click 'Record Answer with Mic' to speak. Spoken words will appear here in real-time and will be submitted for evaluation..."
          value={answerText}
          onChange={(e) => setAnswerText(e.target.value)}
          className={`w-full p-4 rounded-xl bg-slate-950/80 border text-white text-sm focus:outline-none placeholder-slate-500 leading-relaxed resize-none transition-colors ${
            isListening ? 'border-rose-500/80 shadow-md shadow-rose-500/10 ring-1 ring-rose-500/30' : 'border-slate-800 focus:border-blue-500'
          }`}
        />

        {/* Recorded Voice Clip Player & Transcribe Fallback */}
        {recordedAudioUrl && (
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex flex-wrap items-center justify-between gap-3 animate-fadeIn">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span className="text-xs text-slate-300 font-semibold">Your Voice Recording:</span>
              <audio src={recordedAudioUrl} controls className="h-7 max-w-[220px]" />
            </div>

            {(!answerText || !answerText.trim()) && (
              <button
                type="button"
                onClick={() => handleAutoTranscribeAudio()}
                disabled={transcribing}
                className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors"
              >
                {transcribing ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                <span>Auto-Transcribe Recorded Audio</span>
              </button>
            )}
          </div>
        )}

        <div className="flex items-center justify-between pt-1">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleToggleMic}
              className={`px-4 py-2.5 rounded-xl border flex items-center gap-2 text-xs font-semibold transition-all ${
                isListening
                  ? 'bg-rose-500 text-white border-rose-400 shadow-md shadow-rose-500/30 animate-pulse'
                  : 'bg-slate-800 text-slate-300 border-slate-700 hover:text-white hover:border-slate-600'
              }`}
            >
              {isListening ? (
                <>
                  <MicOff className="w-4 h-4 text-white" />
                  <span>Stop Recording ({speechDuration}s)</span>
                </>
              ) : (
                <>
                  <Mic className="w-4 h-4 text-blue-400" />
                  <span>Record Answer with Mic</span>
                </>
              )}
            </button>

            {answerText.trim() && (
              <button
                type="button"
                onClick={() => {
                  setAnswerText('');
                  setRecordedAudioUrl(null);
                  setRecordedAudioBlob(null);
                }}
                className="px-3 py-2 text-xs text-slate-500 hover:text-slate-300 transition-colors"
              >
                Clear
              </button>
            )}
          </div>

          <button
            onClick={handleSubmitAnswer}
            disabled={!answerText.trim() || sending}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-blue-500/20 transition-all disabled:opacity-40"
          >
            {sending ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Evaluating Your Answer...</span>
              </>
            ) : (
              <>
                <span>Submit Answer</span>
                <ChevronRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
