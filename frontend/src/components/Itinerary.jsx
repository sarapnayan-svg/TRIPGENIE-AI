import React, { useState } from 'react';
import { 
  Calendar, MapPin, CheckCircle2, ChevronDown, ChevronUp, 
  Sparkles, Layers, ShieldCheck, Bookmark, Backpack, Info, 
  ArrowRight, Utensils, Compass, IndianRupee, Lightbulb, Zap,
  Check, Loader2, Download
} from 'lucide-react';
import { generateTripPDF } from '../services/pdfExporter';

const PILL_COLORS = [
  { bg: 'bg-emerald-100', text: 'text-emerald-800', border: 'border-emerald-200' },
  { bg: 'bg-sky-100', text: 'text-sky-800', border: 'border-sky-200' },
  { bg: 'bg-amber-100', text: 'text-amber-800', border: 'border-amber-200' },
  { bg: 'bg-purple-100', text: 'text-purple-800', border: 'border-purple-200' },
  { bg: 'bg-rose-100', text: 'text-rose-800', border: 'border-rose-200' },
];

export default function Itinerary({ tripPlan, formData, destinationData, loading, onSaveTrip, isSavingTrip, isTripSaved }) {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const [isExportingPDF, setIsExportingPDF] = useState(false);
  const [pdfExported, setPdfExported] = useState(false);

  const handleExportPDF = async () => {
    if (!tripPlan) return;
    setIsExportingPDF(true);
    try {
      generateTripPDF({
        tripPlan,
        formData: formData || {},
        destinationData: destinationData || {},
        hotels: destinationData?.hotels || [],
      });
      setPdfExported(true);
      setTimeout(() => setPdfExported(false), 3000);
    } catch (err) {
      console.error('PDF export failed:', err);
      alert('Failed to generate PDF: ' + (err.message || 'Unknown error'));
    } finally {
      setIsExportingPDF(false);
    }
  };

  if (loading) {
    return (
      <section id="itinerary" className="scroll-mt-24 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mb-20">
        <div className="bg-white rounded-3xl p-8 sm:p-12 shadow-card border border-sand-dark animate-pulse">
          <div className="h-6 w-48 bg-brand-100 rounded-lg mb-4 animate-shimmer"></div>
          <div className="h-10 w-3/4 bg-brand-50 rounded-xl mb-8 animate-shimmer"></div>
          <div className="space-y-4">
            {[1, 2, 3, 4].map((n) => (
              <div key={n} className="h-32 rounded-2xl bg-sand/60 border border-sand-dark animate-shimmer"></div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (!tripPlan) {
    return (
      <section id="itinerary" className="scroll-mt-24 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mb-20">
        <div className="bg-white rounded-3xl p-8 sm:p-14 text-center shadow-card border border-sand-dark">
          <div className="w-16 h-16 rounded-2xl bg-brand-50 text-brand-500 text-3xl flex items-center justify-center mx-auto mb-4">
            🗺️
          </div>
          <h3 className="font-display font-bold text-2xl text-ink mb-2">
            Your AI Itinerary Will Appear Here
          </h3>
          <p className="text-sm text-ink-muted max-w-md mx-auto mb-6">
            Configure your destination, duration, and budget in the form above and click <strong>"PLAN MY TRIP"</strong> to generate a RAG-grounded daily travel schedule.
          </p>
          <a
            href="#planner"
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-brand-50 hover:bg-brand-100 text-brand-700 font-bold text-sm transition-colors"
          >
            <span>Go to Planning Form</span>
            <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </section>
    );
  }

  const days = Array.isArray(tripPlan.days) ? tripPlan.days : [];
  const sources = Array.isArray(tripPlan.sources) ? tripPlan.sources : [];
  const packingTips = Array.isArray(tripPlan.packing_tips) ? tripPlan.packing_tips : [];
  const travelTips = Array.isArray(tripPlan.travel_tips) ? tripPlan.travel_tips : [];
  const destinationTitle = tripPlan.destination || formData?.destination || 'Your Destination';

  return (
    <section id="itinerary" className="scroll-mt-24 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mb-20">
      <div className="bg-white rounded-3xl p-6 sm:p-10 shadow-card border border-sand-dark">
        
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-sand-dark mb-8">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-emerald-50 text-emerald-800 text-xs font-bold uppercase tracking-wider mb-2">
              <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
              <span>Grounded AI Itinerary</span>
            </div>
            <h2 className="font-display font-extrabold text-2xl sm:text-3xl text-ink">
              {days.length > 0 ? `${days.length}-Day Personalized Travel Plan for ` : 'Personalized Travel Plan for '}{destinationTitle}
            </h2>
            <p className="text-sm text-ink-muted mt-1">
              {tripPlan.summary || `Optimized for your selected preferences and budget.`}
            </p>
            {tripPlan.generated_by && (
              <div className="inline-flex items-center gap-1.5 mt-2 text-[11px] font-semibold text-brand-700 bg-brand-50 px-2.5 py-0.5 rounded-md border border-brand-200">
                <ShieldCheck className="w-3.5 h-3.5 text-brand-600" />
                <span>Generated by: {tripPlan.generated_by}</span>
              </div>
            )}
          </div>

          {/* Action Buttons: Save Trip & RAG Explainability */}
          <div className="flex flex-wrap items-center gap-2.5 flex-shrink-0">
            {onSaveTrip && (
              <button
                onClick={onSaveTrip}
                disabled={isSavingTrip || isTripSaved}
                className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold shadow-sm transition-all ${
                  isTripSaved
                    ? 'bg-emerald-50 text-emerald-800 border border-emerald-300'
                    : 'bg-brand-600 hover:bg-brand-700 active:bg-brand-800 text-white shadow-brand-500/20'
                }`}
                title={isTripSaved ? 'Trip is saved to your account' : 'Save this itinerary to your account'}
              >
                {isSavingTrip ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Saving...</span>
                  </>
                ) : isTripSaved ? (
                  <>
                    <Check className="w-4 h-4 text-emerald-600 stroke-[3]" />
                    <span>Trip Saved!</span>
                  </>
                ) : (
                  <>
                    <Bookmark className="w-4 h-4" />
                    <span>Save Trip</span>
                  </>
                )}
              </button>
            )}

            {/* Export PDF Button */}
            <button
              onClick={handleExportPDF}
              disabled={isExportingPDF}
              className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold shadow-sm transition-all ${
                pdfExported
                  ? 'bg-emerald-50 text-emerald-800 border border-emerald-300'
                  : 'bg-slate-900 hover:bg-slate-800 active:bg-slate-950 text-white shadow-slate-900/20'
              }`}
              title="Download complete trip itinerary & dossier as a PDF"
            >
              {isExportingPDF ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Generating PDF...</span>
                </>
              ) : pdfExported ? (
                <>
                  <Check className="w-4 h-4 text-emerald-600 stroke-[3]" />
                  <span>PDF Downloaded!</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  <span>Export PDF</span>
                </>
              )}
            </button>

            {sources.length > 0 && (
              <button
                onClick={() => setSourcesOpen(!sourcesOpen)}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-brand-50 hover:bg-brand-100 text-brand-800 text-xs sm:text-sm font-bold border border-brand-200 transition-all"
                title="Click to see retrieved knowledge base chunks that grounded this itinerary"
              >
                <ShieldCheck className="w-4 h-4 text-brand-600" />
                <span>RAG Sources ({sources.length})</span>
                {sourcesOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
            )}
          </div>
        </div>


        {/* Collapsible RAG Grounding Evidence Box */}
        {sourcesOpen && sources.length > 0 && (
          <div className="mb-8 p-5 sm:p-6 rounded-2xl bg-brand-50/70 border border-brand-200 animate-in fade-in duration-200">
            <div className="flex items-center gap-2 text-brand-900 font-bold text-sm mb-2">
              <Layers className="w-4 h-4 text-brand-600" />
              <span>Retrieved Knowledge Base Chunks (RAG Evidence)</span>
            </div>
            <p className="text-xs text-brand-800/80 mb-4">
              These travel knowledge chunks were retrieved via cosine similarity using <code>sentence-transformers/all-MiniLM-L6-v2</code> and injected into the LLM prompt to ground generation:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-72 overflow-y-auto pr-1">
              {sources.map((s, idx) => (
                <div key={idx} className="p-3 bg-white rounded-xl border border-brand-100 text-xs shadow-sm">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="px-2 py-0.5 rounded bg-brand-100 text-brand-800 font-bold text-[10px] uppercase">
                      {s.category || 'General'}
                    </span>
                    {s.score !== undefined && (
                      <span className="text-[10px] text-brand-700 font-semibold">
                        Sim: {(s.score * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                  <p className="text-ink text-[11px] leading-relaxed">
                    "{s.text}"
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Day-by-Day Timeline */}
        {days.length === 0 ? (
          <div className="p-8 rounded-2xl bg-sand/40 border border-sand-dark text-center my-6">
            <Compass className="w-8 h-8 text-brand-500 mx-auto mb-2" />
            <div className="font-bold text-ink text-base">Schedule In Progress</div>
            <div className="text-xs text-ink-muted mt-1 max-w-sm mx-auto">
              No daily schedule entries found in this plan. Fill in your preferred travel details above to generate a day-by-day plan.
            </div>
          </div>
        ) : (
          <div className="space-y-6 mb-10">
            {days.map((dayItem, index) => {
              const color = PILL_COLORS[index % PILL_COLORS.length];
              const dayNum = dayItem.day ?? (index + 1);
              const dayTitle = dayItem.title || `Day ${dayNum}`;

              return (
                <div 
                  key={dayNum}
                  className="group p-5 sm:p-6 rounded-2xl border border-sand-dark bg-white hover:border-brand-300 hover:shadow-sm transition-all duration-200"
                >
                  <div className="flex items-start gap-4">
                    {/* Day Badge */}
                    <div className={`w-16 sm:w-20 py-2.5 rounded-xl text-center flex-shrink-0 font-extrabold text-xs sm:text-sm border ${color.bg} ${color.text} ${color.border}`}>
                      Day {dayNum}
                    </div>

                    {/* Day Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                        <h3 className="font-display font-bold text-lg sm:text-xl text-ink leading-snug">
                          {dayTitle}
                        </h3>
                        {dayItem.estimated_cost != null && !isNaN(Number(dayItem.estimated_cost)) && (
                          <span className="self-start sm:self-auto px-3 py-1 rounded-full bg-sand text-ink font-bold text-xs border border-sand-dark flex items-center gap-1">
                            <IndianRupee className="w-3.5 h-3.5 text-brand-600" />
                            <span>Est. ₹{Math.round(Number(dayItem.estimated_cost)).toLocaleString('en-IN')}</span>
                          </span>
                        )}
                      </div>

                      {dayItem.description && (
                        <p className="text-sm text-ink-muted leading-relaxed whitespace-pre-line mb-4">
                          {dayItem.description}
                        </p>
                      )}

                      {/* Rich Breakdown: Places, Activities, Food */}
                      {((Array.isArray(dayItem.places) && dayItem.places.length > 0) ||
                        (Array.isArray(dayItem.activities) && dayItem.activities.length > 0) ||
                        (Array.isArray(dayItem.food_recommendations) && dayItem.food_recommendations.length > 0)) && (
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 border-t border-sand/80">
                          
                          {/* Places */}
                          {Array.isArray(dayItem.places) && dayItem.places.length > 0 && (
                            <div className="p-3 bg-sand/40 rounded-xl border border-sand-dark">
                              <div className="text-[10px] font-bold text-brand-800 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                                <MapPin className="w-3 h-3 text-brand-600" />
                                <span>Places to Visit</span>
                              </div>
                              <div className="flex flex-wrap gap-1">
                                {dayItem.places.map((place, pIdx) => (
                                  <span key={pIdx} className="px-2 py-0.5 rounded-md bg-white text-[11px] font-medium text-ink border border-sand-dark">
                                    {place}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Activities */}
                          {Array.isArray(dayItem.activities) && dayItem.activities.length > 0 && (
                            <div className="p-3 bg-sand/40 rounded-xl border border-sand-dark">
                              <div className="text-[10px] font-bold text-amber-800 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                                <Zap className="w-3 h-3 text-amber-600" />
                                <span>Key Activities</span>
                              </div>
                              <div className="flex flex-wrap gap-1">
                                {dayItem.activities.map((act, aIdx) => (
                                  <span key={aIdx} className="px-2 py-0.5 rounded-md bg-white text-[11px] font-medium text-ink border border-sand-dark">
                                    {act}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Food Recommendations */}
                          {Array.isArray(dayItem.food_recommendations) && dayItem.food_recommendations.length > 0 && (
                            <div className="p-3 bg-sand/40 rounded-xl border border-sand-dark">
                              <div className="text-[10px] font-bold text-emerald-800 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                                <Utensils className="w-3 h-3 text-emerald-600" />
                                <span>Food & Dining</span>
                              </div>
                              <div className="flex flex-wrap gap-1">
                                {dayItem.food_recommendations.map((food, fIdx) => (
                                  <span key={fIdx} className="px-2 py-0.5 rounded-md bg-white text-[11px] font-medium text-ink border border-sand-dark">
                                    {food}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                        </div>
                      )}

                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Travel Tips & Packing Recommendations */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Travel Tips */}
          {travelTips.length > 0 && (
            <div className="p-5 sm:p-6 rounded-2xl bg-sky-50/70 border border-sky-200/80">
              <div className="flex items-center gap-2 text-sky-900 font-bold text-base mb-3">
                <Lightbulb className="w-5 h-5 text-sky-600" />
                <span>Curated Travel Tips</span>
              </div>
              <div className="space-y-2 text-xs text-sky-950">
                {travelTips.map((tip, idx) => (
                  <div key={idx} className="flex items-start gap-2 bg-white/80 p-2.5 rounded-xl border border-sky-100">
                    <CheckCircle2 className="w-4 h-4 text-sky-600 flex-shrink-0 mt-0.5" />
                    <span className="font-medium">{tip}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Packing Tips */}
          {packingTips.length > 0 && (
            <div className="p-5 sm:p-6 rounded-2xl bg-amber-50/70 border border-amber-200/80">
              <div className="flex items-center gap-2 text-amber-900 font-bold text-base mb-3">
                <Backpack className="w-5 h-5 text-amber-600" />
                <span>Packing Checklist</span>
              </div>
              <div className="space-y-2 text-xs text-amber-950">
                {packingTips.map((tip, idx) => (
                  <div key={idx} className="flex items-start gap-2 bg-white/80 p-2.5 rounded-xl border border-amber-100">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <span className="font-medium">{tip}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

      </div>
    </section>
  );
}
