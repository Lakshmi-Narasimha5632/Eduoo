/**
 * Ultra-robust Browser Audio & Speech Service.
 * Solves standard browser speech bugs:
 * 1. Chrome SpeechSynthesis frozen queue lock (auto-unfreezes with cancel + resume).
 * 2. Chrome 15-second speech cutoff (chunks long text + keep-alive ping).
 * 3. Chrome SpeechRecognition auto-stop on silence (fresh instance recreation on pause).
 * 4. Eliminates AudioContext exclusive hardware lock so SpeechRecognition actually receives audio.
 * 5. Concurrent MediaRecorder audio backup + backend transcription fallback.
 */

import { api } from '../api/client';

class SpeechSpeakerService {
  constructor() {
    this.currentId = null;
    this.keepAliveTimer = null;
    this.chunkQueue = [];
    this.onEndCallback = null;
    this.onErrorCallback = null;
    this.onStartCallback = null;
    this.voices = [];

    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.initVoices();
      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = () => this.initVoices();
      }
    }
  }

  initVoices() {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;
    try {
      this.voices = window.speechSynthesis.getVoices() || [];
    } catch {
      // ignore
    }
  }

  getBestVoice() {
    if (!this.voices || this.voices.length === 0) {
      this.initVoices();
    }
    const voices = this.voices || [];
    return (
      voices.find((v) => v.lang === 'en-US' && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Online'))) ||
      voices.find((v) => v.lang === 'en-US' && v.name.includes('Microsoft')) ||
      voices.find((v) => v.lang.startsWith('en-US')) ||
      voices.find((v) => v.lang.startsWith('en')) ||
      voices[0] ||
      null
    );
  }

  splitIntoChunks(text) {
    const cleaned = text
      .replace(/[*_#`~[\]()]/g, ' ')
      .replace(/https?:\/\/\S+/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();

    if (!cleaned) return [];

    const rawSentences = cleaned.match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [cleaned];
    const chunks = [];

    for (const raw of rawSentences) {
      const sentence = raw.trim();
      if (!sentence) continue;

      if (sentence.length <= 160) {
        chunks.push(sentence);
      } else {
        const subParts = sentence.split(/([,;:\-–—]+)/);
        let currentChunk = '';
        for (const part of subParts) {
          if ((currentChunk + part).length > 150) {
            if (currentChunk.trim()) chunks.push(currentChunk.trim());
            currentChunk = part;
          } else {
            currentChunk += part;
          }
        }
        if (currentChunk.trim()) chunks.push(currentChunk.trim());
      }
    }

    return chunks.length > 0 ? chunks : [cleaned];
  }

  stop() {
    if (this.keepAliveTimer) {
      clearInterval(this.keepAliveTimer);
      this.keepAliveTimer = null;
    }
    this.chunkQueue = [];
    this.currentId = null;

    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
        window.speechSynthesis.resume();
      } catch {
        // ignore
      }
    }

    if (this.onEndCallback) {
      const cb = this.onEndCallback;
      this.onEndCallback = null;
      cb();
    }
  }

  speak(text, { id = 'global', onStart, onEnd, onError } = {}) {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      if (onError) onError('Speech synthesis is not supported in this browser.');
      return;
    }

    if (this.currentId === id) {
      this.stop();
      return;
    }

    this.stop();

    const chunks = this.splitIntoChunks(text);
    if (chunks.length === 0) return;

    this.currentId = id;
    this.chunkQueue = [...chunks];
    this.onStartCallback = onStart;
    this.onEndCallback = onEnd;
    this.onErrorCallback = onError;

    try {
      window.speechSynthesis.cancel();
      window.speechSynthesis.resume();
    } catch {
      // ignore
    }

    this.keepAliveTimer = setInterval(() => {
      if (window.speechSynthesis && window.speechSynthesis.speaking) {
        try {
          window.speechSynthesis.pause();
          window.speechSynthesis.resume();
        } catch {
          // ignore
        }
      }
    }, 7000);

    if (this.onStartCallback) {
      this.onStartCallback(id);
    }

    this.playNextChunk();
  }

  playNextChunk() {
    if (!this.currentId || this.chunkQueue.length === 0) {
      this.stop();
      return;
    }

    const nextChunk = this.chunkQueue.shift();
    const utterance = new SpeechSynthesisUtterance(nextChunk);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.lang = 'en-US';

    const voice = this.getBestVoice();
    if (voice) {
      utterance.voice = voice;
    }

    window._eduooActiveUtterance = utterance;

    utterance.onend = () => {
      window._eduooActiveUtterance = null;
      if (this.chunkQueue.length > 0) {
        setTimeout(() => this.playNextChunk(), 50);
      } else {
        this.stop();
      }
    };

    utterance.onerror = (e) => {
      console.warn('SpeechSynthesis chunk error:', e);
      window._eduooActiveUtterance = null;
      if (e.error !== 'interrupted' && e.error !== 'canceled') {
        if (this.chunkQueue.length > 0) {
          this.playNextChunk();
        } else {
          this.stop();
        }
      }
    };

    try {
      window.speechSynthesis.speak(utterance);
    } catch (err) {
      console.warn('Failed to call speechSynthesis.speak:', err);
      this.stop();
    }
  }

  isSpeaking(id = null) {
    if (id) {
      return this.currentId === id;
    }
    return Boolean(this.currentId);
  }
}

export const speechSpeaker = new SpeechSpeakerService();


/**
 * SpeechRecorderService:
 * 1. Clean SpeechRecognition without audio device locking.
 * 2. Fresh recognizer creation on every pause/restart.
 * 3. MediaRecorder audio backup for instant playback + backend transcription.
 * 4. Real-time microphone audio volume analyzer.
 */
class SpeechRecorderService {
  constructor() {
    this.isRecording = false;
    this.recognizer = null;
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.mediaStream = null;
    this.audioContext = null;
    this.volumeAnimFrame = null;

    this.baseText = '';
    this.committedText = '';
    this.lastInterim = '';

    this.onResultCallback = null;
    this.onVolumeCallback = null;
    this.onErrorCallback = null;
    this.onStatusChangeCallback = null;
    this.onAudioReadyCallback = null;
  }

  isSupported() {
    if (typeof window === 'undefined') return false;
    return Boolean(
      window.SpeechRecognition ||
      window.webkitSpeechRecognition ||
      (navigator.mediaDevices && window.MediaRecorder)
    );
  }

  start({
    initialText = '',
    onResult,
    onVolume,
    onError,
    onStatusChange,
    onAudioReady,
  }) {
    this.stop();

    this.baseText = (initialText || '').trim();
    this.committedText = '';
    this.lastInterim = '';
    this.audioChunks = [];

    this.onResultCallback = onResult;
    this.onVolumeCallback = onVolume;
    this.onErrorCallback = onError;
    this.onStatusChangeCallback = onStatusChange;
    this.onAudioReadyCallback = onAudioReady;
    this.isRecording = true;

    // 1. Start browser speech recognition
    this.startFreshRecognition();

    // 2. Start concurrent MediaRecorder audio capture with volume analyzer
    this.startMediaRecorder();

    if (this.onStatusChangeCallback) {
      this.onStatusChangeCallback(true);
    }

    return true;
  }

  startFreshRecognition() {
    if (!this.isRecording) return false;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return false;

    try {
      const recognizer = new SpeechRecognition();
      recognizer.continuous = true;
      recognizer.interimResults = true;
      recognizer.lang = 'en-US';
      recognizer.maxAlternatives = 1;

      recognizer.onresult = (event) => {
        let newlyFinalized = '';
        let currentInterim = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const res = event.results[i];
          const text = res[0]?.transcript || '';
          if (res.isFinal) {
            newlyFinalized += (newlyFinalized ? ' ' : '') + text.trim();
          } else {
            currentInterim += text;
          }
        }

        if (newlyFinalized) {
          this.committedText = [this.committedText, newlyFinalized]
            .filter(Boolean)
            .join(' ')
            .replace(/\s+/g, ' ');
        }

        this.lastInterim = currentInterim;

        const fullDisplay = [this.baseText, this.committedText, currentInterim.trim()]
          .filter(Boolean)
          .join(' ')
          .replace(/\s+/g, ' ');

        if (this.onResultCallback) {
          this.onResultCallback(fullDisplay, currentInterim.trim());
        }
      };

      recognizer.onerror = (e) => {
        if (e.error === 'no-speech') {
          // Pause between phrases, continue recording
          return;
        }
        console.warn('SpeechRecognition event notice:', e.error);
        if (e.error === 'not-allowed') {
          if (this.onErrorCallback) {
            this.onErrorCallback('Microphone permission blocked. Please allow microphone access in your browser address bar.');
          }
        } else if (e.error === 'network') {
          if (this.onErrorCallback) {
            this.onErrorCallback('Cloud speech-to-text had a network delay; direct audio recording is active.');
          }
        }
      };

      recognizer.onend = () => {
        if (this.isRecording) {
          // Commit any pending interim words before starting fresh session
          if (this.lastInterim && this.lastInterim.trim()) {
            this.committedText = [this.committedText, this.lastInterim.trim()]
              .filter(Boolean)
              .join(' ')
              .replace(/\s+/g, ' ');
            this.lastInterim = '';
          }
          setTimeout(() => {
            if (this.isRecording) {
              this.startFreshRecognition();
            }
          }, 200);
        }
      };

      this.recognizer = recognizer;
      recognizer.start();
      return true;
    } catch (err) {
      console.warn('SpeechRecognition start notice:', err);
      return false;
    }
  }

  async startMediaRecorder() {
    if (typeof navigator === 'undefined' || !navigator.mediaDevices) {
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      this.mediaStream = stream;

      // Volume analyzer using AudioContext
      try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) {
          const audioCtx = new AudioCtx();
          this.audioContext = audioCtx;
          const source = audioCtx.createMediaStreamSource(stream);
          const analyser = audioCtx.createAnalyser();
          analyser.fftSize = 256;
          analyser.smoothingTimeConstant = 0.5;
          source.connect(analyser);

          const dataArray = new Uint8Array(analyser.frequencyBinCount);
          const checkVolume = () => {
            if (!this.isRecording) return;
            analyser.getByteFrequencyData(dataArray);
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
              sum += dataArray[i];
            }
            const avg = sum / dataArray.length;
            const vol = Math.min(100, Math.round((avg / 90) * 100));
            if (this.onVolumeCallback) {
              this.onVolumeCallback(vol);
            }
            this.volumeAnimFrame = requestAnimationFrame(checkVolume);
          };
          this.volumeAnimFrame = requestAnimationFrame(checkVolume);
        }
      } catch (volErr) {
        console.warn('Volume meter analyzer init notice:', volErr);
      }

      // MediaRecorder audio capture
      if (window.MediaRecorder) {
        const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
          ? 'audio/webm;codecs=opus'
          : MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : MediaRecorder.isTypeSupported('audio/mp4')
          ? 'audio/mp4'
          : '';

        const options = mimeType ? { mimeType } : {};
        const mediaRecorder = new MediaRecorder(stream, options);
        this.audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data && event.data.size > 0) {
            this.audioChunks.push(event.data);
          }
        };

        mediaRecorder.onstop = () => {
          if (this.audioChunks.length > 0) {
            const finalType = mediaRecorder.mimeType || mimeType || 'audio/webm';
            const audioBlob = new Blob(this.audioChunks, { type: finalType });
            const audioUrl = URL.createObjectURL(audioBlob);

            if (this.onAudioReadyCallback) {
              this.onAudioReadyCallback({ audioBlob, audioUrl, mimeType: finalType });
            }
          }
        };

        this.mediaRecorder = mediaRecorder;
        mediaRecorder.start(250);
      }
    } catch (err) {
      console.warn('Microphone stream access notice:', err);
      if (this.onErrorCallback) {
        this.onErrorCallback('Microphone permission denied or device not found.');
      }
    }
  }

  stop() {
    this.isRecording = false;

    if (this.volumeAnimFrame) {
      cancelAnimationFrame(this.volumeAnimFrame);
      this.volumeAnimFrame = null;
    }

    if (this.audioContext) {
      try {
        this.audioContext.close();
      } catch {
        // ignore
      }
      this.audioContext = null;
    }

    if (this.recognizer) {
      try {
        this.recognizer.stop();
      } catch {
        // ignore
      }
      this.recognizer = null;
    }

    if (this.mediaRecorder) {
      try {
        if (this.mediaRecorder.state !== 'inactive') {
          this.mediaRecorder.stop();
        }
      } catch {
        // ignore
      }
      this.mediaRecorder = null;
    }

    if (this.mediaStream) {
      try {
        this.mediaStream.getTracks().forEach((track) => track.stop());
      } catch {
        // ignore
      }
      this.mediaStream = null;
    }

    if (this.onStatusChangeCallback) {
      this.onStatusChangeCallback(false);
    }

    if (this.onVolumeCallback) {
      this.onVolumeCallback(0);
    }

    if (this.lastInterim && this.lastInterim.trim()) {
      this.committedText = [this.committedText, this.lastInterim.trim()]
        .filter(Boolean)
        .join(' ')
        .replace(/\s+/g, ' ');
      this.lastInterim = '';
    }

    const finalFull = [this.baseText, this.committedText]
      .filter(Boolean)
      .join(' ')
      .replace(/\s+/g, ' ');

    return finalFull;
  }

  /**
   * Transcribes recorded audio blob via the backend transcribe API.
   */
  async transcribeAudioBlob(audioBlob, contextHint = '') {
    if (!audioBlob) return '';

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      if (contextHint) {
        formData.append('context', contextHint);
      }

      const res = await api.post('/interviews/transcribe/', formData);
      return res?.transcript || '';
    } catch (err) {
      console.warn('Backend audio transcription failed:', err);
      return '';
    }
  }
}

export const speechRecorder = new SpeechRecorderService();
