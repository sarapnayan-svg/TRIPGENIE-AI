import React from 'react';
import { Sparkles, Check, Clock, Tag, ArrowRight } from 'lucide-react';

export default function Packages({ destinationData, destinationName, onSelectPackage }) {
  const packages = destinationData?.packages || [];

  return (
    <section id="packages" className="scroll-mt-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-20">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-purple-50 text-purple-700 text-xs font-bold uppercase tracking-wider mb-2">
            <span>🎒 Bundled Travel Intelligence</span>
          </div>
          <h2 className="font-display font-bold text-2xl sm:text-3xl text-ink">
            Curated Holiday Packages for {destinationName || 'Destination'}
          </h2>
          <p className="text-sm text-ink-muted">
            All-inclusive itineraries combining handpicked resorts, private transport, and priority excursion passes.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {packages.map((pkg) => (
          <div
            key={pkg.id}
            className="group bg-white rounded-3xl overflow-hidden border border-sand-dark shadow-sm hover:shadow-card-hover transition-all duration-300 flex flex-col justify-between"
          >
            <div>
              {/* Package Image & Badges */}
              <div className="relative h-52 overflow-hidden bg-sand-dark">
                <img
                  src={pkg.image}
                  alt={pkg.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  loading="lazy"
                />
                <span className="absolute top-3 left-3 px-3 py-1 rounded-full bg-brand-600 text-white text-xs font-bold shadow-md">
                  {pkg.badge || 'Popular'}
                </span>
                <span className="absolute bottom-3 right-3 px-3 py-1 rounded-full bg-white/90 backdrop-blur-md text-ink text-xs font-semibold flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-brand-600" />
                  <span>{pkg.duration}</span>
                </span>
              </div>

              {/* Body */}
              <div className="p-6">
                <h3 className="font-display font-bold text-xl text-ink mb-3 group-hover:text-brand-600 transition-colors">
                  {pkg.title}
                </h3>

                <div className="text-xs font-bold text-ink-muted uppercase tracking-wider mb-2">
                  Package Inclusions:
                </div>
                <div className="space-y-2 mb-6">
                  {pkg.inclusions.map((inc, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-xs text-ink">
                      <Check className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                      <span>{inc}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Pricing & CTA */}
            <div className="p-6 pt-0 border-t border-sand-dark/60 mt-auto">
              <div className="flex items-baseline justify-between pt-4 mb-4">
                <div>
                  <span className="text-[11px] text-ink-muted line-through block">
                    ₹{pkg.originalPrice.toLocaleString('en-IN')}
                  </span>
                  <div className="font-display font-extrabold text-2xl text-ink">
                    ₹{pkg.price.toLocaleString('en-IN')}{' '}
                    <span className="text-xs font-normal text-ink-muted">/ person</span>
                  </div>
                </div>

                <span className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 text-xs font-bold">
                  Save ₹{(pkg.originalPrice - pkg.price).toLocaleString('en-IN')}
                </span>
              </div>

              <button
                onClick={() => onSelectPackage && onSelectPackage(pkg)}
                className="w-full py-3 rounded-xl bg-sand hover:bg-brand-600 text-ink hover:text-white font-bold text-sm transition-all duration-200 flex items-center justify-center gap-2 border border-sand-dark hover:border-brand-600 shadow-sm"
              >
                <span>Customize Package</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
