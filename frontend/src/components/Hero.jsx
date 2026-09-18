import React from 'react';
import { Sparkles, ArrowDown, MapPin, Calendar, Compass, ShieldCheck } from 'lucide-react';

export default function Hero({ onSelectDestination, onStartPlanning, selectedDestination = 'Goa', destinationData }) {
  const popularDestinations = [
    { name: 'Goa', emoji: '🏖️', desc: 'Beaches & Nightlife' },
    { name: 'Kerala', emoji: '🌴', desc: 'Backwaters & Tea Hills' },
    { name: 'Manali', emoji: '🏔️', desc: 'Snow & Adventure' },
    { name: 'Jaipur', emoji: '🏰', desc: 'Palaces & Heritage' },
    { name: 'Rishikesh', emoji: '🧘‍♂️', desc: 'Yoga & River Rafting' },
  ];

  const heroImg = destinationData?.heroImage || 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=80';
  const tagline = destinationData?.tagline || 'Experience verifiable travel intelligence with specialized RAG.';
  const bestTime = destinationData?.bestTimeToVisit || 'October to March';

  return (
    <section id="hero" className="relative pt-6 pb-12 lg:pt-10 lg:pb-16 overflow-hidden">
      {/* Dynamic Background with Ambient Gradients */}
      <div className="absolute inset-0 pointer-events-none -z-10 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full bg-brand-200/50 blur-3xl"></div>
        <div className="absolute top-1/2 -left-40 w-[500px] h-[500px] rounded-full bg-amber-100/60 blur-3xl"></div>
        <div className="absolute -bottom-20 right-1/4 w-[400px] h-[400px] rounded-full bg-emerald-100/50 blur-3xl"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
          
          {/* Left Column: Heading, Value Prop & Destination Selector */}
          <div className="lg:col-span-7 text-left">
            {/* Project Highlight Pill */}
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/90 border border-brand-200 shadow-sm text-brand-800 text-xs sm:text-sm font-semibold mb-4 animate-fade-in">
              <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-ping"></span>
              <Sparkles className="w-4 h-4 text-brand-500" />
              <span>Intelligent AI Travel Planner • RAG Grounded</span>
            </div>

            {/* Main Hero Title with Dynamic Active Destination */}
            <h1 className="font-display font-extrabold text-3xl sm:text-4xl lg:text-5xl text-ink tracking-tight leading-[1.18] mb-4">
              Explore{' '}
              <span className="bg-gradient-to-r from-brand-600 via-brand-500 to-indigo-600 bg-clip-text text-transparent">
                {selectedDestination}
              </span>{' '}
              with Intelligent AI
            </h1>

            {/* Tagline for currently selected destination */}
            <p className="text-base sm:text-lg text-ink-muted leading-relaxed mb-6">
              {tagline} Powered by verified retrieval-augmented intelligence, deterministic budget models, and real-time GPS waypoints.
            </p>

            {/* Destination Meta Chips */}
            <div className="flex flex-wrap items-center gap-2 mb-8">
              <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white border border-sand-dark shadow-xs text-xs font-semibold text-ink">
                <MapPin className="w-3.5 h-3.5 text-brand-500" />
                <span>{selectedDestination}, India</span>
              </div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white border border-sand-dark shadow-xs text-xs font-semibold text-ink">
                <Calendar className="w-3.5 h-3.5 text-emerald-500" />
                <span>Best: {bestTime}</span>
              </div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white border border-sand-dark shadow-xs text-xs font-semibold text-ink">
                <ShieldCheck className="w-3.5 h-3.5 text-blue-500" />
                <span>RAG Verified</span>
              </div>
            </div>

            {/* Quick Action Buttons */}
            <div className="flex flex-wrap items-center gap-4 mb-8">
              <button
                onClick={onStartPlanning}
                className="px-7 py-3.5 rounded-2xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-700 hover:to-brand-600 text-white font-bold text-sm sm:text-base shadow-glow hover:shadow-card-hover transform hover:-translate-y-0.5 transition-all duration-200 flex items-center gap-2"
              >
                <span>Build {selectedDestination} Itinerary</span>
                <ArrowDown className="w-4 h-4 animate-bounce" />
              </button>
              <a
                href="#chat"
                className="px-6 py-3.5 rounded-2xl bg-white hover:bg-sand-dark text-ink font-bold text-sm sm:text-base border border-sand-dark shadow-sm hover:shadow-md transition-all duration-200 flex items-center gap-2"
              >
                <span>Ask AI Concierge</span>
                <span className="text-base">💬</span>
              </a>
            </div>

            {/* Quick Destination Selectors with Active Highlight */}
            <div className="pt-4 border-t border-sand-dark/60">
              <p className="text-xs uppercase tracking-wider font-bold text-ink-muted mb-2.5 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-brand-500" />
                <span>Explore Top Grounded Destinations (Click to Switch Photo):</span>
              </p>
              <div className="flex flex-wrap items-center gap-2">
                {popularDestinations.map((dest) => {
                  const isActive = selectedDestination.toLowerCase() === dest.name.toLowerCase();
                  return (
                    <button
                      key={dest.name}
                      onClick={() => onSelectDestination(dest.name)}
                      className={`group px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-200 flex items-center gap-1.5 ${
                        isActive
                          ? 'bg-brand-600 text-white shadow-md ring-2 ring-brand-400 scale-105'
                          : 'bg-white/90 hover:bg-brand-50 text-ink hover:text-brand-800 border border-sand-dark hover:border-brand-300 shadow-sm'
                      }`}
                    >
                      <span className="text-sm">{dest.emoji}</span>
                      <span>{dest.name}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Right Column: Live Destination Photography Showcase */}
          <div className="lg:col-span-5">
            <div className="relative group rounded-3xl overflow-hidden shadow-2xl border-4 border-white bg-slate-900 transition-all duration-500 hover:shadow-brand-500/20">
              <img
                src={heroImg}
                alt={selectedDestination}
                className="w-full h-80 sm:h-96 lg:h-[430px] object-cover transition-transform duration-700 group-hover:scale-105"
              />
              {/* Top Live Badge */}
              <div className="absolute top-4 left-4 inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-black/65 backdrop-blur-md text-white text-xs font-bold border border-white/20 shadow-lg">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
                <span>LIVE PHOTO • {selectedDestination.toUpperCase()}</span>
              </div>

              {/* Bottom Gradient Overlay with Destination Info */}
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent p-5 text-white">
                <div className="flex items-center justify-between mb-1">
                  <h3 className="text-xl sm:text-2xl font-bold font-display">{selectedDestination}</h3>
                  <span className="text-xs bg-white/20 backdrop-blur-sm px-2.5 py-1 rounded-full font-medium">📍 Verified</span>
                </div>
                <p className="text-xs sm:text-sm text-white/90 line-clamp-2 leading-relaxed">
                  {tagline}
                </p>
                <div className="flex items-center gap-2 mt-3 text-[11px] text-white/80 font-medium">
                  <span>📅 Best Season: {bestTime}</span>
                  <span>•</span>
                  <span>4+ Curated Landmarks</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
