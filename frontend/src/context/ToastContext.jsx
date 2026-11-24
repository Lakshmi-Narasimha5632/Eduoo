import React, { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
import {
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  Info,
  X,
  HelpCircle,
} from 'lucide-react';

const ToastContext = createContext(null);

// Standalone global dispatcher so non-React services can trigger toasts
let globalToastHandler = null;
let globalConfirmHandler = null;

export const toast = {
  success: (message, title = 'Success') => globalToastHandler?.('success', message, title),
  error: (message, title = 'Error') => globalToastHandler?.('error', message, title),
  warning: (message, title = 'Notice') => globalToastHandler?.('warning', message, title),
  info: (message, title = 'Information') => globalToastHandler?.('info', message, title),
  confirm: (options) => globalConfirmHandler?.(options) || Promise.resolve(false),
};

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);
  const [confirmDialog, setConfirmDialog] = useState(null);
  const confirmResolveRef = useRef(null);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback(
    (type, message, title = '') => {
      const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const defaultTitle =
        title ||
        (type === 'success'
          ? 'Success'
          : type === 'error'
          ? 'Error'
          : type === 'warning'
          ? 'Notice'
          : 'Information');

      const newToast = {
        id,
        type,
        title: defaultTitle,
        message: typeof message === 'string' ? message : JSON.stringify(message),
        duration: type === 'error' ? 5000 : 4000,
        createdAt: Date.now(),
      };

      setToasts((prev) => [newToast, ...prev.slice(0, 4)]); // Keep at most 5 toasts at once

      setTimeout(() => {
        removeToast(id);
      }, newToast.duration);

      return id;
    },
    [removeToast]
  );

  const confirm = useCallback((options) => {
    return new Promise((resolve) => {
      confirmResolveRef.current = resolve;
      setConfirmDialog({
        title: options.title || 'Please Confirm',
        message: options.message || 'Are you sure you want to proceed?',
        confirmText: options.confirmText || 'Confirm',
        cancelText: options.cancelText || 'Cancel',
        variant: options.variant || 'danger', // 'danger' | 'primary' | 'success'
        icon: options.icon || null,
      });
    });
  }, []);

  const handleConfirmAction = (result) => {
    if (confirmResolveRef.current) {
      confirmResolveRef.current(result);
      confirmResolveRef.current = null;
    }
    setConfirmDialog(null);
  };

  useEffect(() => {
    globalToastHandler = addToast;
    globalConfirmHandler = confirm;

    // Expose global toast on window
    window.toast = toast;

    // Intercept native browser alert so "localhost says" popups never appear
    const originalAlert = window.alert;
    window.alert = (msg) => {
      const str = String(msg);
      const lower = str.toLowerCase();
      if (
        lower.includes('fail') ||
        lower.includes('error') ||
        lower.includes('invalid') ||
        lower.includes('cannot') ||
        lower.includes('rejected')
      ) {
        addToast('error', str, 'Alert');
      } else if (
        lower.includes('success') ||
        lower.includes('passed') ||
        lower.includes('accepted') ||
        lower.includes('completed')
      ) {
        addToast('success', str, 'Success');
      } else if (lower.includes('warn') || lower.includes('caution') || lower.includes('notice')) {
        addToast('warning', str, 'Notice');
      } else {
        addToast('info', str, 'System Notice');
      }
    };

    return () => {
      globalToastHandler = null;
      globalConfirmHandler = null;
      window.alert = originalAlert;
    };
  }, [addToast, confirm]);

  return (
    <ToastContext.Provider value={{ toast, addToast, confirm }}>
      {children}

      {/* Box-Type Toast Notifications Container */}
      <div className="fixed bottom-5 right-5 z-[99999] flex flex-col gap-3 max-w-sm sm:max-w-md w-full px-4 sm:px-0 pointer-events-none select-none">
        {toasts.map((t) => {
          const isSuccess = t.type === 'success';
          const isError = t.type === 'error';
          const isWarning = t.type === 'warning';

          const iconColor = isSuccess
            ? 'text-emerald-400 bg-emerald-500/15 border-emerald-500/30'
            : isError
            ? 'text-rose-400 bg-rose-500/15 border-rose-500/30'
            : isWarning
            ? 'text-amber-400 bg-amber-500/15 border-amber-500/30'
            : 'text-blue-400 bg-blue-500/15 border-blue-500/30';

          const boxTheme = isSuccess
            ? 'bg-gradient-to-br from-emerald-950/50 via-slate-900/95 to-slate-900/95 border-emerald-500/40 shadow-emerald-950/50'
            : isError
            ? 'bg-gradient-to-br from-rose-950/50 via-slate-900/95 to-slate-900/95 border-rose-500/40 shadow-rose-950/50'
            : isWarning
            ? 'bg-gradient-to-br from-amber-950/50 via-slate-900/95 to-slate-900/95 border-amber-500/40 shadow-amber-950/50'
            : 'bg-gradient-to-br from-blue-950/50 via-slate-900/95 to-slate-900/95 border-blue-500/40 shadow-blue-950/50';

          const progressBarColor = isSuccess
            ? 'bg-emerald-500'
            : isError
            ? 'bg-rose-500'
            : isWarning
            ? 'bg-amber-500'
            : 'bg-blue-500';

          return (
            <div
              key={t.id}
              className={`pointer-events-auto relative overflow-hidden rounded-2xl border ${boxTheme} shadow-2xl backdrop-blur-xl p-4 transition-all duration-300 flex items-start gap-3.5 animate-toast-slide-in hover:scale-[1.01]`}
            >
              {/* Box Icon */}
              <div className={`w-9 h-9 rounded-xl border flex items-center justify-center shrink-0 ${iconColor}`}>
                {isSuccess && <CheckCircle2 className="w-5 h-5" />}
                {isError && <AlertCircle className="w-5 h-5" />}
                {isWarning && <AlertTriangle className="w-5 h-5" />}
                {!isSuccess && !isError && !isWarning && <Info className="w-5 h-5" />}
              </div>

              {/* Message Content */}
              <div className="flex-1 min-w-0 pr-2">
                <div className="flex items-center gap-2">
                  <h5 className="text-xs font-bold uppercase tracking-wider text-white">
                    {t.title}
                  </h5>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {isSuccess ? '✓ OK' : isError ? '⚠ ALERT' : '• NOTICE'}
                  </span>
                </div>
                <p className="text-xs text-slate-300 mt-1 leading-relaxed break-words font-medium">
                  {t.message}
                </p>
              </div>

              {/* Close Button */}
              <button
                onClick={() => removeToast(t.id)}
                className="w-6 h-6 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 flex items-center justify-center shrink-0 transition-colors"
                title="Dismiss"
              >
                <X className="w-4 h-4" />
              </button>

              {/* Progress bar line */}
              <div
                className={`absolute bottom-0 left-0 h-1 ${progressBarColor} animate-toast-progress opacity-80`}
                style={{ animationDuration: `${t.duration}ms` }}
              />
            </div>
          );
        })}
      </div>

      {/* Box-Type Confirmation Modal Dialog */}
      {confirmDialog && (
        <div className="fixed inset-0 z-[100000] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 relative overflow-hidden animate-fadeIn">
            {/* Header Badge */}
            <div className="flex items-center gap-3 mb-4">
              <div
                className={`w-11 h-11 rounded-xl border flex items-center justify-center shrink-0 ${
                  confirmDialog.variant === 'danger'
                    ? 'bg-rose-500/15 border-rose-500/30 text-rose-400'
                    : confirmDialog.variant === 'success'
                    ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400'
                    : 'bg-blue-500/15 border-blue-500/30 text-blue-400'
                }`}
              >
                {confirmDialog.variant === 'danger' ? (
                  <AlertCircle className="w-6 h-6" />
                ) : confirmDialog.variant === 'success' ? (
                  <CheckCircle2 className="w-6 h-6" />
                ) : (
                  <HelpCircle className="w-6 h-6" />
                )}
              </div>
              <div>
                <h4 className="text-base font-extrabold text-white tracking-tight">
                  {confirmDialog.title}
                </h4>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Confirmation Dialog
                </span>
              </div>
            </div>

            {/* Description */}
            <p className="text-xs text-slate-300 leading-relaxed mb-6 bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80">
              {confirmDialog.message}
            </p>

            {/* Actions */}
            <div className="flex items-center justify-end gap-2.5">
              <button
                type="button"
                onClick={() => handleConfirmAction(false)}
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-semibold transition-colors"
              >
                {confirmDialog.cancelText}
              </button>

              <button
                type="button"
                onClick={() => handleConfirmAction(true)}
                className={`px-5 py-2.5 rounded-xl text-white font-bold text-xs shadow-lg transition-all ${
                  confirmDialog.variant === 'danger'
                    ? 'bg-rose-600 hover:bg-rose-500 shadow-rose-600/30'
                    : confirmDialog.variant === 'success'
                    ? 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-600/30'
                    : 'bg-blue-600 hover:bg-blue-500 shadow-blue-600/30'
                }`}
              >
                {confirmDialog.confirmText}
              </button>
            </div>
          </div>
        </div>
      )}
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    return {
      toast,
      addToast: () => {},
      confirm: () => Promise.resolve(false),
    };
  }
  return context;
};
