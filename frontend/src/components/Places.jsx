import React, { useState } from 'react';
import { Compass, Clock, Ticket, Sparkles, ExternalLink, Lightbulb } from 'lucide-react';

export default function Places({ destinationData, destinationName }) {
  const places = destinationData?.places || [];
  const [activeFilter, setActiveFilter] = useState('all');

  const categories = ['all', ...new Set(places.map(p => p.category))];

  const filteredPlaces = activeFilter === 'all' 
    ? places 
    : places.filter(p => p.category === activeFilter);

  return (
    <section id="places" className="scroll-mt-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-20">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-emerald-50 text-emerald-700 text-xs font-bold uppercase tracking-wider mb-2">
            <span>📍 Must-Visit Attractions</span>
          </div>
          <h2 className="font-display font-bold text-2xl sm:text-3xl text-ink">
            Top Places & Sights in {destinationName || 'Destination'}
          </h2>
          <p className="text-sm text-ink-muted">
            Curated points of interest grounded with entry information and local tips.
          </p>
        </div>

        <a
          href={`https://www.google.com/search?q=top+attractions+in+${encodeURIComponent(destinationName || 'Goa')}`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 text-xs font-bold text-brand-600 hover:text-brand-700 hover:underline flex-shrink-0"
        >
          <span>Explore more attractions</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>

      {/* Category Filter Pills */}
      {categories.length > 1 && (
        <div className="flex flex-wrap items-center gap-2 mb-6">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveFilter(cat)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all capitalize ${
                activeFilter === cat
                  ? 'bg-brand-600 text-white shadow-sm'
                  : 'bg-sand hover:bg-sand-dark text-ink-muted'
              }`}
            >
              {cat === 'all' ? 'All Attractions' : cat}
            </button>
          ))}
        </div>
      )}

      {filteredPlaces.length === 0 ? (
        <div className="bg-white rounded-3xl p-10 text-center border border-sand-dark max-w-md mx-auto my-6">
          <Compass className="w-8 h-8 text-brand-600 mx-auto mb-2" />
          <h3 className="font-bold text-ink">No attractions found</h3>
          <p className="text-xs text-ink-muted mt-1">Try selecting a different category filter above.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPlaces.map((place) => (
            <div
              key={place.id || place.name}
              className="group bg-white rounded-3xl overflow-hidden border border-sand-dark shadow-sm hover:shadow-card-hover transition-all duration-300 flex flex-col"
            >
              {/* Image */}
              <div className="relative h-52 overflow-hidden bg-sand-dark">
                <img
                  src={place.image}
                  alt={place.name || 'Attraction in destination'}
                  onError={(e) => {
                    e.currentTarget.onerror = null;
                    e.currentTarget.src = 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800&auto=format&fit=crop&q=80';
                  }}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  loading="lazy"
                />
                <span className="absolute top-3 left-3 px-3 py-1 rounded-full bg-white/95 backdrop-blur-md text-ink text-xs font-bold shadow-sm">
                  {place.category}
                </span>
              </div>

              {/* Place Details */}
              <div className="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <h3 className="font-display font-bold text-lg text-ink mb-2 group-hover:text-brand-600 transition-colors">
                    {place.name}
                  </h3>
                  <p className="text-xs text-ink-muted leading-relaxed mb-4">
                    {place.description}
                  </p>

                  {/* Timings & Fees */}
                  <div className="space-y-1.5 text-xs text-ink font-medium bg-sand/50 p-3 rounded-xl mb-4 border border-sand-dark">
                    <div className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-brand-500 flex-shrink-0" />
                      <span className="truncate">{place.timing}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Ticket className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
                      <span className="truncate">{place.fee}</span>
                    </div>
                  </div>
                </div>

                {/* RAG Insider Tip */}
                {place.tip && (
                  <div className="pt-3 border-t border-sand-dark flex items-start gap-2 text-xs text-emerald-800 bg-emerald-50/50 p-2.5 rounded-xl border border-emerald-100">
                    <Lightbulb className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <span className="leading-snug">
                      <strong className="font-bold">Insider Tip:</strong> {place.tip}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
