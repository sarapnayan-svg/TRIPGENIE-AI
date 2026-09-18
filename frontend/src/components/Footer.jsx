import React from 'react';
import { Sparkles, ShieldCheck, Heart } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-white border-t border-sand-dark py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          
          {/* Col 1: Brand & Academic Overview */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-700 to-brand-500 flex items-center justify-center text-xl shadow-sm">
                🧞‍♂️
              </div>
              <span className="font-display font-bold text-2xl text-brand-900">
                Trip<span className="text-brand-500">Genie</span> AI
              </span>
            </div>
            <p className="text-xs text-ink-muted leading-relaxed max-w-md mb-4">
              <strong>Intelligent AI Travel Planner Using Large Language Models and Retrieval-Augmented Generation (RAG).</strong> Built as a Final-Year B.Tech Information Technology capstone project demonstrating grounded knowledge retrieval and hallucination mitigation.
            </p>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-sand text-xs font-semibold text-ink-muted border border-sand-dark">
              <ShieldCheck className="w-4 h-4 text-brand-600" />
              <span>Verifiable Ground Truth • Zero Hallucination Pipeline</span>
            </div>
          </div>

          {/* Col 2: Architecture Highlights */}
          <div>
            <h4 className="font-display font-bold text-sm text-ink uppercase tracking-wider mb-3">
              Technology Stack
            </h4>
            <ul className="space-y-1.5 text-xs text-ink-muted">
              <li>• FastAPI (Asynchronous ASGI Server)</li>
              <li>• Sentence-Transformers (all-MiniLM-L6-v2)</li>
              <li>• Anthropic Claude / LLM Integration</li>
              <li>• React 18 / 19 & Tailwind CSS v3</li>
              <li>• Open-Meteo Live Weather Meteorological API</li>
            </ul>
          </div>

          {/* Col 3: Indexed Knowledge Base */}
          <div>
            <h4 className="font-display font-bold text-sm text-ink uppercase tracking-wider mb-3">
              Curated Destinations
            </h4>
            <ul className="space-y-1.5 text-xs text-ink-muted">
              <li>• Goa (Coastal, Heritage & Watersports)</li>
              <li>• Kerala (Backwaters & Munnar Hills)</li>
              <li>• Manali (Himalayan Adventure & Solang)</li>
              <li>• Jaipur (Rajput Forts & Royal Palaces)</li>
              <li>• Rishikesh (Ganges Rafting & Yoga Ghats)</li>
            </ul>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-sand-dark flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-ink-muted">
          <div>
            © {new Date().getFullYear()} TripGenie AI • B.Tech IT Capstone Project
          </div>
          <div className="flex items-center gap-1">
            <span>Engineered with pair-programming intelligence</span>
          </div>
        </div>

      </div>
    </footer>
  );
}
