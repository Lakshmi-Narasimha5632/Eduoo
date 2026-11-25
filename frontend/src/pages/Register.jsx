import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, AlertCircle, CheckCircle2, RotateCw, ArrowLeft, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const TARGET_ROLES = [
  'Full Stack Developer',
  'Software Developer',
  'Frontend Developer',
  'Backend Developer',
  'Python Developer',
  'Data Scientist',
  'Data Analyst',
  'AI Engineer',
  'ML Engineer',
  'DevOps Engineer',
];

export const Register = () => {
  const [step, setStep] = useState('form');
  const [form, setForm] = useState({
    email: '',
    username: '',
    password: '',
    password_confirm: '',
    full_name: '',
    target_role: 'Full Stack Developer',
    daily_study_hours: 2.5,
    college: '',
    branch: '',
    graduation_year: 2026,
  });

  const [otp, setOtp] = useState('');
  const [otpHint, setOtpHint] = useState('');
  const [error, setError] = useState('');
  const [infoMsg, setInfoMsg] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [resending, setResending] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  const { register, verifyOtp, resendOtp } = useAuth();
  const navigate = useNavigate();

  // Handle resend countdown timer
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setInterval(() => {
      setResendCooldown((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [resendCooldown]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setInfoMsg('');

    if (form.password !== form.password_confirm) {
      setError('Passwords do not match.');
      return;
    }

    setSubmitting(true);
    try {
      const res = await register(form);
      if (res?.requires_verification) {
        setStep('otp');
        if (res?.otp_hint) {
          setOtpHint(res.otp_hint);
        }
        setInfoMsg(res.message || `A 6-digit verification code was sent to ${form.email}.`);
        setResendCooldown(60);
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err?.message || 'Registration failed.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleVerifySubmit = async (e) => {
    e.preventDefault();
    setError('');
    setInfoMsg('');

    const cleanOtp = otp.trim();
    if (!cleanOtp || cleanOtp.length !== 6) {
      setError('Please enter a valid 6-digit verification code.');
      return;
    }

    setVerifying(true);
    try {
      await verifyOtp(form.email, cleanOtp);
      navigate('/dashboard');
    } catch (err) {
      setError(err?.message || 'Verification failed. Please check the code.');
    } finally {
      setVerifying(false);
    }
  };

  const handleResendOtp = async () => {
    if (resendCooldown > 0 || resending) return;
    setError('');
    setInfoMsg('');
    setResending(true);
    try {
      const res = await resendOtp(form.email);
      if (res?.otp_hint) {
        setOtpHint(res.otp_hint);
      }
      setInfoMsg(res?.message || 'A fresh verification code has been sent to your email.');
      setResendCooldown(60);
    } catch (err) {
      setError(err?.message || 'Failed to resend verification code.');
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 relative overflow-hidden py-12">
      <div className="w-full max-w-xl glass-card rounded-2xl p-8 border border-slate-800 shadow-2xl relative z-10">
        
        {/* Header Branding */}
        <div className="text-center mb-6">
          <div className="w-12 h-12 mx-auto rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white font-black text-xl shadow-lg shadow-brand-500/30">
            {step === 'otp' ? <ShieldCheck className="w-6 h-6" /> : 'E'}
          </div>
          <h2 className="text-2xl font-black text-white mt-4 tracking-tight">
            {step === 'otp' ? 'Verify Your Email' : 'Create your Eduoo Profile'}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {step === 'otp'
              ? `Enter the 6-digit verification code sent to ${form.email}`
              : 'Personalize your career journey and interview preparation'}
          </p>
        </div>

        {/* Status Alerts */}
        {error && (
          <div className="mb-6 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {infoMsg && (
          <div className="mb-6 p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{infoMsg}</span>
          </div>
        )}

        {/* Step 1: Initial Registration Form */}
        {step === 'form' ? (
          <form onSubmit={handleRegisterSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  required
                  name="full_name"
                  value={form.full_name}
                  onChange={handleChange}
                  className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-brand-500 transition"
                  placeholder="Narasimha Reddy"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Username
                </label>
                <input
                  type="text"
                  required
                  name="username"
                  value={form.username}
                  onChange={handleChange}
                  className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-brand-500 transition"
                  placeholder="narasimha"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                Email Address <span className="text-brand-400">(Requires Verification)</span>
              </label>
              <input
                type="email"
                required
                name="email"
                value={form.email}
                onChange={handleChange}
                className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-brand-500 transition"
                placeholder="narasimha@example.com"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Password
                </label>
                <input
                  type="password"
                  required
                  name="password"
                  value={form.password}
                  onChange={handleChange}
                  className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-brand-500 transition"
                  placeholder="••••••••"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Confirm Password
                </label>
                <input
                  type="password"
                  required
                  name="password_confirm"
                  value={form.password_confirm}
                  onChange={handleChange}
                  className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-brand-500 transition"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Target Role
                </label>
                <select
                  name="target_role"
                  value={form.target_role}
                  onChange={handleChange}
                  className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-brand-500 transition"
                >
                  {TARGET_ROLES.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Daily Study Budget (Hours)
                </label>
                <input
                  type="number"
                  step="0.5"
                  min="0.5"
                  max="12"
                  name="daily_study_hours"
                  value={form.daily_study_hours}
                  onChange={handleChange}
                  className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-brand-500 transition"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full mt-4 py-3 px-4 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-brand-600/30 transition disabled:opacity-50"
            >
              {submitting ? 'Sending Verification Code...' : 'Complete Registration'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        ) : (
          /* Step 2: OTP Verification Screen */
          <form onSubmit={handleVerifySubmit} className="space-y-6">
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 text-center">
              <span className="text-xs text-slate-400 block mb-1">Verification code sent to</span>
              <span className="text-sm font-bold text-white block">{form.email}</span>
            </div>

            {otpHint && (
              <div className="bg-indigo-500/10 border border-indigo-500/30 p-3.5 rounded-xl text-xs text-indigo-300 flex items-center justify-between gap-3">
                <div>
                  <span className="font-semibold block text-indigo-200">Email Delivery Offline / Direct Code</span>
                  <span>Code: <strong className="text-white font-mono text-sm tracking-widest">{otpHint}</strong></span>
                </div>
                <button
                  type="button"
                  onClick={() => setOtp(otpHint)}
                  className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-bold text-xs shrink-0 transition shadow-sm"
                >
                  Auto-fill Code
                </button>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 text-center">
                Enter 6-Digit OTP Code
              </label>
              <div className="flex justify-center">
                <input
                  type="text"
                  maxLength={6}
                  autoFocus
                  required
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/[^0-9]/g, ''))}
                  placeholder="------"
                  className="w-48 text-center text-3xl tracking-[12px] font-mono py-3 px-4 bg-slate-900 border-2 border-brand-500/60 rounded-xl text-white focus:outline-none focus:border-brand-400 shadow-inner shadow-black/50"
                />
              </div>
              <p className="text-[11px] text-slate-400 text-center mt-2">
                The verification code is valid for 10 minutes.
              </p>
            </div>

            <div className="space-y-3">
              <button
                type="submit"
                disabled={verifying || otp.trim().length !== 6}
                className="w-full py-3 px-4 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-brand-600/30 transition disabled:opacity-50"
              >
                {verifying ? 'Verifying Account...' : 'Verify Email & Launch Eduoo'}
                <ArrowRight className="w-4 h-4" />
              </button>

              <div className="flex items-center justify-between pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setStep('form');
                    setError('');
                    setInfoMsg('');
                  }}
                  className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  Edit details
                </button>

                <button
                  type="button"
                  disabled={resendCooldown > 0 || resending}
                  onClick={handleResendOtp}
                  className="text-xs text-brand-400 font-semibold hover:underline flex items-center gap-1.5 disabled:opacity-50 disabled:no-underline"
                >
                  <RotateCw className={`w-3.5 h-3.5 ${resending ? 'animate-spin' : ''}`} />
                  {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend Code'}
                </button>
              </div>
            </div>
          </form>
        )}

        <div className="mt-6 text-center text-xs text-slate-400">
          Already have an account?{' '}
          <Link to="/login" className="text-brand-400 font-semibold hover:underline">
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
