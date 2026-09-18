import React from 'react';
import { Sparkles, Compass, ShieldCheck, Zap, ArrowDown, MapPin } from 'lucide-react';

export default function Hero({ onSelectDestination, onStartPlanning }) {
  const popularDestinations = [
    { name: 'Goa', emoji: '🏖️', desc: 'Beaches & Nightlife' },
    { name: 'Kerala', emoji: '🌴', desc: 'Backwaters & Tea Hills' },
    { name: 'Manali', emoji: '🏔️', desc: 'Snow & Adventure' },
    { name: 'Jaipur', emoji: '🏰', desc: 'Palaces & Heritage' },
    { name: 'Rishikesh', emoji: '🧘‍♂️', desc: 'Yoga & River Rafting' },
  ];

  return (
    <section id="hero" className="relative pt-8 pb-16 lg:pt-14 lg:pb-24 overflow-hidden">
      {/* Dynamic Background with Ambient Gradients */}
      <div className="absolute inset-0 pointer-events-none -z-10 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full bg-brand-200/50 blur-3xl"></div>
        <div className="absolute top-1/2 -left-40 w-[500px] h-[500px] rounded-full bg-amber-100/60 blur-3xl"></div>
        <div className="absolute -bottom-20 right-1/4 w-[400px] h-[400px] rounded-full bg-emerald-100/50 blur-3xl"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto">
          
          {/* Project Highlight Pill */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/80 border border-brand-200 shadow-sm text-brand-800 text-xs sm:text-sm font-semibold mb-6 animate-fade-in">
            <span className="flex h-2 w-2 rounded-full bg-brand-500 animate-ping"></span>
            <Sparkles className="w-4 h-4 text-brand-500" />
            <span>Intelligent AI Travel Planner • RAG Grounded</span>
          </div>

          {/* Main Hero Title */}
          <h1 className="font-display font-extrabold text-4xl sm:text-5xl lg:text-6xl text-ink tracking-tight leading-[1.15] mb-6">
            Plan Your Perfect Trip with{' '}
            <span className="bg-gradient-to-r from-brand-600 via-brand-500 to-indigo-600 bg-clip-text text-transparent">
              Intelligent AI
            </span>
          </h1>

          {/* Short Value Proposition Description */}
          <p className="text-base sm:text-lg lg:text-xl text-ink-muted leading-relaxed mb-8">
            Experience verifiable travel intelligence. TripGenie AI combines{' '}
            <strong className="text-ink font-semibold">Large Language Models</strong> with a specialized{' '}
            <strong className="text-ink font-semibold">Retrieval-Augmented Generation (RAG)</strong> knowledge base to craft tailor-made itineraries, exact budget breakdowns, and live weather forecasts without hallucinations.
          </p>

          {/* Quick Action Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-4 mb-12">
            <button
              onClick={onStartPlanning}
              className="px-8 py-4 rounded-2xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-700 hover:to-brand-600 text-white font-bold text-base shadow-glow hover:shadow-card-hover transform hover:-translate-y-0.5 transition-all duration-200 flex items-center gap-2"
            >
              <span>Build Custom Itinerary</span>
              <ArrowDown className="w-4 h-4 animate-bounce" />
            </button>
            <a
              href="#chat"
              className="px-8 py-4 rounded-2xl bg-white hover:bg-sand-dark text-ink font-bold text-base border border-sand-dark shadow-sm hover:shadow-md transition-all duration-200 flex items-center gap-2"
            >
              <span>Ask TripGenie AI</span>
              <span className="text-lg">💬</span>
            </a>
          </div>

          {/* Quick Destination Selectors */}
          <div className="pt-2 border-t border-sand-dark/60">
            <p className="text-xs uppercase tracking-wider font-bold text-ink-muted mb-3 flex items-center justify-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-brand-500" />
              <span>Explore Top Grounded Destinations:</span>
            </p>
            <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-3">
              {popularDestinations.map((dest) => (
                <button
                  key={dest.name}
                  onClick={() => onSelectDestination(dest.name)}
                  className="group px-4 py-2 rounded-xl bg-white/90 hover:bg-brand-50 border border-sand-dark hover:border-brand-300 text-ink hover:text-brand-800 text-sm font-semibold shadow-sm transition-all duration-200 flex items-center gap-2 hover:scale-105"
                >
                  <span className="text-base">{dest.emoji}</span>
                  <span>{dest.name}</span>
                  <span className="text-[11px] text-ink-muted group-hover:text-brand-600 font-normal hidden sm:inline">
                    ({dest.desc})
                  </span>
                </button>
              ))}
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
