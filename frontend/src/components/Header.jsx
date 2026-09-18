import React, { useState } from 'react';
import {
  Sparkles,
  MapPin,
  Compass,
  User,
  CheckCircle2,
  AlertCircle,
  Menu,
  X,
  ShieldCheck,
  Bookmark,
  LogOut,
  LogIn,
  Wallet,
  Calendar,
} from 'lucide-react';

export default function Header({
  backendStatus,
  onNavClick,
  currentSection,
  currentUser,
  onOpenAuthModal,
  onOpenSavedTrips,
  onLogout,
  savedTripsCount = 0,
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileModalOpen, setProfileModalOpen] = useState(false);

  const navItems = [
    { label: 'Plan Trip', href: '#planner' },
    { label: 'Itinerary', href: '#itinerary' },
    { label: 'Hotels', href: '#hotels' },
    { label: 'Places', href: '#places' },
    { label: 'Map', href: '#map' },
    { label: 'Budget', href: '#budget' },
    { label: 'Weather', href: '#weather' },
    { label: 'Packages', href: '#packages' },
    { label: 'Ask AI', href: '#chat' },
  ];

  const handleNav = (href) => {
    setMobileMenuOpen(false);
    if (onNavClick) {
      onNavClick(href.replace('#', ''));
    }
  };

  const getInitials = (name) => {
    if (!name) return 'TG';
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <>
      <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-sand-dark shadow-sm transition-all duration-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          
          {/* Logo & Tagline */}
          <a 
            href="#hero" 
            className="flex items-center gap-3 group focus:outline-none"
            onClick={(e) => { e.preventDefault(); handleNav('#hero'); }}
          >
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-700 via-brand-500 to-brand-400 flex items-center justify-center text-2xl shadow-glow group-hover:scale-105 transition-transform duration-300">
              🧞‍♂️
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-display font-extrabold text-2xl tracking-tight text-brand-900">
                  Trip<span className="text-brand-500">Genie</span>
                </span>
                <span className="px-1.5 py-0.5 rounded-md bg-brand-100 text-brand-700 text-xs font-bold uppercase tracking-wider">
                  AI
                </span>
              </div>
              <p className="text-xs text-ink-muted font-medium -mt-1 hidden sm:block">
                Your AI Travel Agent
              </p>
            </div>
          </a>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center gap-1 xl:gap-2">
            {navItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                onClick={(e) => {
                  e.preventDefault();
                  handleNav(item.href);
                }}
                className={`px-3 py-2 rounded-xl text-sm font-semibold transition-all duration-200 ${
                  currentSection === item.href.replace('#', '')
                    ? 'text-brand-600 bg-brand-50 font-bold'
                    : 'text-ink-muted hover:text-brand-700 hover:bg-sand-dark/60'
                }`}
              >
                {item.label}
              </a>
            ))}
          </nav>

          {/* Right Area: Health, Saved Trips & Auth */}
          <div className="flex items-center gap-2.5 sm:gap-3">
            {/* Backend Health Badge */}
            <div 
              className={`hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border ${
                backendStatus.online 
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                  : 'bg-amber-50 text-amber-700 border-amber-200'
              }`}
              title={backendStatus.online ? 'FastAPI & RAG Engine Connected' : 'Backend Standby (Mocking/Fallback mode)'}
            >
              <span className={`w-2 h-2 rounded-full ${backendStatus.online ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`}></span>
              <span>{backendStatus.online ? 'RAG Core Online' : 'FastAPI Offline'}</span>
            </div>

            {/* Saved Trips Button */}
            {currentUser && (
              <button
                onClick={onOpenSavedTrips}
                className="hidden sm:inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-brand-50 hover:bg-brand-100 text-brand-700 text-xs font-bold border border-brand-200 transition-all shadow-sm"
                title="View my saved itineraries"
              >
                <Bookmark className="w-3.5 h-3.5 fill-brand-600 text-brand-600" />
                <span>Saved Trips</span>
                {savedTripsCount > 0 && (
                  <span className="px-1.5 py-0.2 rounded-full bg-brand-600 text-white text-[10px] font-bold">
                    {savedTripsCount}
                  </span>
                )}
              </button>
            )}

            {/* User Profile / Auth Area */}
            {currentUser ? (
              <button
                onClick={() => setProfileModalOpen(true)}
                className="flex items-center gap-2 p-1.5 sm:px-3 sm:py-2 rounded-xl bg-sand hover:bg-sand-dark border border-sand-dark text-ink transition-all duration-200 focus:outline-none"
                aria-label="User Profile"
              >
                <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-600 text-white flex items-center justify-center font-bold text-sm">
                  {getInitials(currentUser.full_name)}
                </div>
                <div className="text-left hidden sm:block">
                  <div className="text-xs font-bold leading-tight text-ink truncate max-w-[100px]">
                    {currentUser.full_name}
                  </div>
                  <div className="text-[10px] text-emerald-600 font-bold leading-tight">
                    ● Signed In
                  </div>
                </div>
              </button>
            ) : (
              <button
                onClick={() => onOpenAuthModal('login')}
                className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-sm transition-all"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Sign In</span>
              </button>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-xl text-ink-muted hover:text-ink hover:bg-sand-dark focus:outline-none"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Navigation */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-sand-dark bg-white px-4 pt-2 pb-6 space-y-1 shadow-lg">
            <div className="py-2 mb-2 border-b border-sand-dark flex items-center justify-between text-xs">
              <span className="text-ink-muted">Backend Connection:</span>
              <span className={`font-semibold ${backendStatus.online ? 'text-emerald-600' : 'text-amber-600'}`}>
                {backendStatus.online ? '● Connected (FastAPI)' : '○ Standby'}
              </span>
            </div>

            {/* Mobile Auth Button */}
            <div className="py-2 border-b border-sand-dark mb-2">
              {currentUser ? (
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-brand-600 text-white flex items-center justify-center font-bold text-xs">
                      {getInitials(currentUser.full_name)}
                    </div>
                    <div>
                      <div className="text-xs font-bold text-ink">{currentUser.full_name}</div>
                      <div className="text-[10px] text-ink-muted">{currentUser.email}</div>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setMobileMenuOpen(false);
                      onOpenSavedTrips();
                    }}
                    className="px-3 py-1 rounded-lg bg-brand-50 text-brand-700 font-bold text-xs"
                  >
                    Saved ({savedTripsCount})
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    onOpenAuthModal('login');
                  }}
                  className="w-full py-2.5 rounded-xl bg-brand-600 text-white font-bold text-xs text-center"
                >
                  Sign In / Create Account
                </button>
              )}
            </div>

            {navItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                onClick={(e) => {
                  e.preventDefault();
                  handleNav(item.href);
                }}
                className="block px-3 py-2.5 rounded-lg text-base font-semibold text-ink hover:bg-brand-50 hover:text-brand-700 transition-colors"
              >
                {item.label}
              </a>
            ))}
          </div>
        )}
      </header>

      {/* User Profile Modal */}
      {profileModalOpen && currentUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/50 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl border border-sand-dark relative animate-in zoom-in-95 duration-200">
            <button 
              onClick={() => setProfileModalOpen(false)}
              className="absolute top-5 right-5 text-ink-muted hover:text-ink p-1 rounded-full hover:bg-sand transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-600 text-white flex items-center justify-center font-extrabold text-2xl shadow-lg">
                {getInitials(currentUser.full_name)}
              </div>
              <div>
                <h3 className="text-xl font-bold text-ink">{currentUser.full_name}</h3>
                <p className="text-xs text-ink-muted">{currentUser.email}</p>
                <div className="inline-flex items-center gap-1 mt-1 px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800 text-xs font-semibold">
                  <ShieldCheck className="w-3.5 h-3.5" /> Authenticated Traveler
                </div>
              </div>
            </div>

            <div className="space-y-3 border-t border-sand-dark pt-4 text-sm">
              <div className="flex justify-between py-1.5 border-b border-sand/60">
                <span className="text-ink-muted">Saved Itineraries</span>
                <span className="font-bold text-brand-600">{savedTripsCount} trips</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-sand/60">
                <span className="text-ink-muted">Database Engine</span>
                <span className="font-semibold text-ink">PostgreSQL / SQLAlchemy</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-sand/60">
                <span className="text-ink-muted">Password Security</span>
                <span className="font-semibold text-emerald-600">Bcrypt Salted & Hashed</span>
              </div>
            </div>

            <div className="mt-6 flex flex-col gap-2.5">
              <button
                onClick={() => {
                  setProfileModalOpen(false);
                  onOpenSavedTrips();
                }}
                className="w-full py-3 rounded-xl bg-brand-50 hover:bg-brand-100 text-brand-700 font-bold text-xs transition-colors border border-brand-200 flex items-center justify-center gap-2"
              >
                <Bookmark className="w-4 h-4 fill-brand-600" />
                <span>View My Saved Trips ({savedTripsCount})</span>
              </button>

              <button
                onClick={() => {
                  setProfileModalOpen(false);
                  onLogout();
                }}
                className="w-full py-3 rounded-xl bg-sand hover:bg-rose-50 text-ink-muted hover:text-rose-600 font-bold text-xs transition-colors border border-sand-dark flex items-center justify-center gap-2"
              >
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
