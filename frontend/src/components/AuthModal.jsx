import React, { useState } from 'react';
import { X, Lock, Mail, User, ShieldCheck, Loader2, AlertCircle, Sparkles } from 'lucide-react';
import { loginUser, registerUser } from '../services/api';

export default function AuthModal({ isOpen, onClose, onAuthSuccess, initialMode = 'login' }) {
  const [mode, setMode] = useState(initialMode); // 'login' or 'register'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === 'login') {
        const res = await loginUser({ email, password });
        if (res.success && res.data) {
          onAuthSuccess(res.data.user);
          onClose();
        } else {
          setError(res.error || 'Login failed. Please check your credentials.');
        }
      } else {
        if (password.length < 6) {
          setError('Password must be at least 6 characters long.');
          setLoading(false);
          return;
        }
        const res = await registerUser({ email, password, full_name: fullName });
        if (res.success && res.data) {
          onAuthSuccess(res.data.user);
          onClose();
        } else {
          setError(res.error || 'Registration failed.');
        }
      }
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/50 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl border border-sand-dark relative animate-in zoom-in-95 duration-200">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-ink-muted hover:text-ink p-1.5 rounded-full hover:bg-sand transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header Branding */}
        <div className="text-center mb-6">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-700 via-brand-600 to-indigo-600 text-white flex items-center justify-center text-2xl shadow-glow mx-auto mb-3">
            🧞‍♂️
          </div>
          <h3 className="font-display font-black text-2xl text-ink">
            {mode === 'login' ? 'Welcome Back' : 'Create Account'}
          </h3>
          <p className="text-xs text-ink-muted mt-1">
            {mode === 'login'
              ? 'Sign in to access and manage your saved itineraries'
              : 'Join TripGenie to save trips, customize routes, and access your profile'}
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex bg-sand p-1 rounded-2xl mb-6 border border-sand-dark/60">
          <button
            type="button"
            onClick={() => {
              setMode('login');
              setError(null);
            }}
            className={`flex-1 py-2 rounded-xl text-xs font-bold transition-all ${
              mode === 'login'
                ? 'bg-white text-ink shadow-sm'
                : 'text-ink-muted hover:text-ink'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setMode('register');
              setError(null);
            }}
            className={`flex-1 py-2 rounded-xl text-xs font-bold transition-all ${
              mode === 'register'
                ? 'bg-white text-ink shadow-sm'
                : 'text-ink-muted hover:text-ink'
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Error Notice */}
        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Auth Form */}
        <form onSubmit={handleSubmit} className="space-y-3.5">
          {mode === 'register' && (
            <div>
              <label className="block text-xs font-bold text-ink mb-1">Full Name</label>
              <div className="relative">
                <User className="w-4 h-4 text-ink-muted absolute left-3.5 top-3.5" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Nayan Sarap"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-sand-dark focus:border-brand-500 focus:ring-2 focus:ring-brand-100 text-sm font-medium text-ink transition-all"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-ink mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-ink-muted absolute left-3.5 top-3.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-sand-dark focus:border-brand-500 focus:ring-2 focus:ring-brand-100 text-sm font-medium text-ink transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-ink mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-ink-muted absolute left-3.5 top-3.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={mode === 'register' ? 'At least 6 characters' : '••••••••'}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-sand-dark focus:border-brand-500 focus:ring-2 focus:ring-brand-100 text-sm font-medium text-ink transition-all"
              />
            </div>
            {mode === 'register' && (
              <span className="text-[11px] text-ink-muted mt-1 block">
                Must be at least 6 characters. Passwords are securely hashed with bcrypt.
              </span>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 rounded-xl bg-brand-600 hover:bg-brand-700 active:bg-brand-800 text-white font-bold text-sm shadow-md shadow-brand-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>{mode === 'login' ? 'Signing in...' : 'Creating account...'}</span>
              </>
            ) : (
              <span>{mode === 'login' ? 'Sign In' : 'Create Account'}</span>
            )}
          </button>
        </form>

        {/* Security Note Footer */}
        <div className="mt-5 pt-4 border-t border-sand-dark/60 text-center">
          <div className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-ink-muted">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>PostgreSQL Database • Bcrypt Hashed • PyJWT Secured</span>
          </div>
        </div>

      </div>
    </div>
  );
}
